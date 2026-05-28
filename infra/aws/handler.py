"""
Security Remediation Agent
Analiza vulnerabilidades detectadas por Trivy/Checkov
y genera fixes automáticos via Pull Request
"""

import json
import os
import re
import base64
import requests


def call_groq(prompt: str, system: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no está configurada")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def analyze_vulnerability(vuln: dict) -> dict:
    system = """Eres un experto en seguridad DevSecOps.
    Analizas vulnerabilidades en contenedores Docker y generas fixes concisos.
    Responde SIEMPRE en este formato JSON exacto, sin texto adicional:
    {
        "risk_summary": "descripción del riesgo en 1-2 frases",
        "fix_type": "base_image_update|package_update|config_change",
        "fix_description": "qué cambiar exactamente",
        "urgency": "critical|high|medium|low",
        "pr_title": "título del PR en inglés, máximo 72 caracteres",
        "is_python_package": true or false,
        "python_package_name": "nombre exacto del paquete en requirements.txt o null",
        "python_fixed_version": "versión exacta del fix o null"
    }"""

    prompt = f"""Vulnerabilidad encontrada:
- CVE: {vuln.get('cve_id', 'N/A')}
- Paquete: {vuln.get('package', 'N/A')}
- Versión actual: {vuln.get('version', 'N/A')}
- Versión con fix: {vuln.get('fixed_version', 'N/A')}
- Severidad: {vuln.get('severity', 'N/A')}
- Imagen: {vuln.get('image', 'N/A')}

Analiza y genera el fix. Si el paquete es una librería Python que podría
estar en requirements.txt, indica is_python_package: true y el nombre exacto."""

    response = call_groq(prompt, system)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())

    return {
        "risk_summary": response[:200],
        "fix_type": "unknown",
        "fix_description": "Manual review required",
        "urgency": vuln.get('severity', 'medium').lower(),
        "pr_title": f"fix: address {vuln.get('cve_id')} in {vuln.get('package')}",
        "is_python_package": False,
        "python_package_name": None,
        "python_fixed_version": None
    }


def get_file_content(repo: str, path: str, ref: str, headers: dict) -> tuple:
    """Obtiene el contenido de un fichero del repo. Devuelve (content, sha)."""
    r = requests.get(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        headers=headers,
        params={"ref": ref}
    )
    if r.status_code == 404:
        return None, None
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content, data["sha"]


def update_requirements_txt(
    content: str,
    package_name: str,
    fixed_version: str
) -> tuple:
    """
    Actualiza la versión de un paquete en requirements.txt.
    Devuelve (nuevo_contenido, cambio_realizado).
    """
    lines = content.split("\n")
    new_lines = []
    changed = False

    for line in lines:
        stripped = line.strip()
        # Ignora comentarios y líneas vacías
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        # Extrae el nombre del paquete de la línea
        pkg = re.split(r'[>=<!~\[]', stripped)[0].strip().lower()

        if pkg == package_name.lower():
            # Reemplaza la línea con la versión fixeada
            new_line = f"{package_name}=={fixed_version}"
            new_lines.append(new_line)
            changed = True
            print(f"Updated {package_name}: {stripped} -> {new_line}")
        else:
            new_lines.append(line)

    return "\n".join(new_lines), changed


def commit_file(
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
    existing_sha: str,
    headers: dict
) -> bool:
    """Crea o actualiza un fichero en una rama."""
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch
    }
    if existing_sha:
        payload["sha"] = existing_sha

    r = requests.put(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        headers=headers,
        json=payload
    )
    r.raise_for_status()
    return True


def pr_already_exists(cve_id: str, repo: str, headers: dict) -> bool:
    r = requests.get(
        f"https://api.github.com/repos/{repo}/pulls",
        headers=headers,
        params={"state": "open", "per_page": 100}
    )
    if r.status_code != 200:
        return False
    for pr in r.json():
        if cve_id.lower() in pr.get("title", "").lower():
            print(f"PR already exists for {cve_id}: {pr['html_url']}")
            return True
    return False


def ensure_labels_exist(repo: str, headers: dict):
    labels = [
        {"name": "security", "color": "d73a4a", "description": "Security vulnerability fix"},
        {"name": "automated", "color": "0075ca", "description": "Automatically generated by AI agent"},
        {"name": "ai-generated", "color": "7057ff", "description": "Generated by Groq AI agent"}
    ]
    for label in labels:
        r = requests.post(
            f"https://api.github.com/repos/{repo}/labels",
            headers=headers,
            json=label
        )
        if r.status_code == 201:
            print(f"Label created: {label['name']}")
        elif r.status_code == 422:
            print(f"Label already exists: {label['name']}")


def create_github_pr(analysis: dict, vuln: dict, repo: str, token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if pr_already_exists(vuln.get('cve_id', ''), repo, headers):
        return f"SKIPPED: PR already exists for {vuln.get('cve_id')}"

    ensure_labels_exist(repo, headers)

    # Obtener SHA de main
    r = requests.get(
        f"https://api.github.com/repos/{repo}/git/refs/heads/main",
        headers=headers
    )
    r.raise_for_status()
    main_sha = r.json()["object"]["sha"]

    cve_safe = vuln.get('cve_id', 'vuln').lower().replace('/', '-')
    branch_name = f"fix/security-{cve_safe}-{main_sha[:7]}"

    # Crear rama
    r = requests.post(
        f"https://api.github.com/repos/{repo}/git/refs",
        headers=headers,
        json={"ref": f"refs/heads/{branch_name}", "sha": main_sha}
    )
    if r.status_code not in [201, 422]:
        r.raise_for_status()
    print(f"Branch: {branch_name}")

    # --- FIX REAL: intentar actualizar requirements.txt ---
    real_fix_applied = False
    fix_details = ""

    is_python = analysis.get("is_python_package", False)
    pkg_name = analysis.get("python_package_name")
    fixed_version = analysis.get("python_fixed_version")

    if is_python and pkg_name and fixed_version:
        print(f"Attempting real fix for Python package: {pkg_name} -> {fixed_version}")

        req_content, req_sha = get_file_content(
            repo, "apps/demo-web/requirements.txt", branch_name, headers
        )

        if req_content:
            new_content, changed = update_requirements_txt(
                req_content, pkg_name, fixed_version
            )
            if changed:
                commit_file(
                    repo=repo,
                    path="apps/demo-web/requirements.txt",
                    content=new_content,
                    message=f"fix: update {pkg_name} to {fixed_version} to address {vuln.get('cve_id')}",
                    branch=branch_name,
                    existing_sha=req_sha,
                    headers=headers
                )
                real_fix_applied = True
                fix_details = f"✅ **Real fix applied:** `{pkg_name}` updated to `{fixed_version}` in `requirements.txt`"
                print(f"Real fix applied: {pkg_name} -> {fixed_version}")
            else:
                fix_details = f"ℹ️ Package `{pkg_name}` not found in `requirements.txt` — manual fix required"
                print(f"Package not found in requirements.txt: {pkg_name}")
        else:
            fix_details = "ℹ️ `requirements.txt` not found — manual fix required"
    else:
        fix_details = f"ℹ️ Not a Python package — {analysis.get('fix_description', 'manual fix required')}"

    # Crear fichero de reporte siempre
    report_content = json.dumps({
        "cve_id": vuln.get("cve_id"),
        "package": vuln.get("package"),
        "current_version": vuln.get("version"),
        "fixed_version": vuln.get("fixed_version"),
        "severity": vuln.get("severity"),
        "analysis": analysis,
        "real_fix_applied": real_fix_applied,
        "status": "fixed" if real_fix_applied else "pending_manual_fix"
    }, indent=2)

    file_path = f"security-reports/{vuln.get('cve_id', 'vuln').replace('/', '-')}.json"
    _, existing_sha = get_file_content(repo, file_path, branch_name, headers)

    commit_file(
        repo=repo,
        path=file_path,
        content=report_content,
        message=f"security: add vulnerability report for {vuln.get('cve_id')}",
        branch=branch_name,
        existing_sha=existing_sha,
        headers=headers
    )

    # Cuerpo del PR
    fix_badge = "✅ Real fix applied" if real_fix_applied else "⚠️ Manual fix required"

    pr_body = f"""## 🔒 Security Vulnerability Fix

**Automated PR generated by AI Security Agent** | {fix_badge}

### Vulnerability Details
| Field | Value |
|-------|-------|
| CVE | `{vuln.get('cve_id', 'N/A')}` |
| Package | `{vuln.get('package', 'N/A')}` |
| Current Version | `{vuln.get('version', 'N/A')}` |
| Fixed Version | `{vuln.get('fixed_version', 'N/A')}` |
| Severity | `{vuln.get('severity', 'N/A')}` |

### AI Risk Analysis
{analysis.get('risk_summary', 'N/A')}

### Fix Applied
{fix_details}

### Urgency
**{analysis.get('urgency', 'medium').upper()}**

---
*This PR was automatically generated by the Security Remediation Agent*
*Powered by Groq (Llama 3.3 70B) · {vuln.get('image', 'N/A')}*"""

    r = requests.post(
        f"https://api.github.com/repos/{repo}/pulls",
        headers=headers,
        json={
            "title": analysis.get('pr_title', f"fix: address {vuln.get('cve_id')}"),
            "body": pr_body,
            "head": branch_name,
            "base": "main"
        }
    )
    r.raise_for_status()
    pr_number = r.json()["number"]
    pr_url = r.json()["html_url"]

    # Añadir labels
    requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/labels",
        headers=headers,
        json={"labels": ["security", "automated", "ai-generated"]}
    )

    return pr_url


def handler(event, context):
    print(f"Event received: {json.dumps(event)}")

    vulnerabilities = event.get("vulnerabilities", [])
    repo = event.get("repo", "")
    github_token = event.get("github_token", "")

    if not vulnerabilities:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No vulnerabilities to process"})
        }

    results = []

    for vuln in vulnerabilities[:3]:
        try:
            print(f"Analyzing: {vuln.get('cve_id')} in {vuln.get('package')}")
            analysis = analyze_vulnerability(vuln)
            print(f"Analysis: {json.dumps(analysis)}")

            pr_url = None
            if github_token and repo:
                pr_url = create_github_pr(analysis, vuln, repo, github_token)
                print(f"PR result: {pr_url}")

            results.append({
                "cve_id": vuln.get("cve_id"),
                "analysis": analysis,
                "pr_url": pr_url,
                "status": "success"
            })

        except Exception as e:
            print(f"Error processing {vuln.get('cve_id')}: {str(e)}")
            results.append({
                "cve_id": vuln.get("cve_id"),
                "error": str(e),
                "status": "error"
            })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "processed": len(results),
            "results": results
        })
    }
