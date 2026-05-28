#!/usr/bin/env python3
import json
import sys
import os


def parse_trivy_sarif(sarif_path: str, max_vulns: int = 3) -> list:
    if not os.path.exists(sarif_path):
        print(f"Error: {sarif_path} no existe", file=sys.stderr)
        return []

    with open(sarif_path) as f:
        sarif = json.load(f)

    python_vulns = []
    os_vulns = []
    seen_cves = set()

    for run in sarif.get("runs", []):
        rules = {
            rule["id"]: rule
            for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
        }

        for result in run.get("results", []):
            rule_id = result.get("ruleId", "")
            level = result.get("level", "")

            if level not in ["error", "warning"]:
                continue

            if rule_id in seen_cves:
                continue
            seen_cves.add(rule_id)

            rule = rules.get(rule_id, {})
            message = result.get("message", {}).get("text", "")
            help_text = rule.get("help", {}).get("text", "")

            fixed_version = "unknown"
            if "fixed version:" in help_text.lower():
                for line in help_text.split("\n"):
                    if "fixed version:" in line.lower():
                        fixed_version = line.split(":")[-1].strip()
                        break

            severity = "CRITICAL" if level == "error" else "HIGH"

            package_name = "unknown"
            for line in message.split("\n"):
                if line.startswith("Package:"):
                    package_name = line.replace("Package:", "").strip()
                    break

            version = "unknown"
            for line in message.split("\n"):
                if "Installed Version:" in line:
                    version = line.replace("Installed Version:", "").strip()
                    break

            # Detectar si es paquete Python mirando las locations del SARIF
            locations = result.get("locations", [])
            is_python = False
            for loc in locations:
                uri = loc.get("physicalLocation", {}).get(
                    "artifactLocation", {}).get("uri", "")
                if "site-packages" in uri or "python" in uri.lower():
                    is_python = True
                    break

            vuln = {
                "cve_id": rule_id,
                "package": package_name,
                "version": version,
                "fixed_version": fixed_version,
                "severity": severity,
                "image": os.getenv(
                    "IMAGE_NAME",
                    "ghcr.io/mauriciogoik/demo-web:latest"
                ),
                "description": message[:200],
                "is_python": is_python
            }

            if is_python:
                python_vulns.append(vuln)
                print(f"Python vuln: {rule_id} in {package_name}", file=sys.stderr)
            else:
                os_vulns.append(vuln)
                print(f"OS vuln: {rule_id} in {package_name}", file=sys.stderr)

    # Priorizar Python sobre OS
    all_vulns = python_vulns + os_vulns
    return all_vulns[:max_vulns]


if __name__ == "__main__":
    sarif_path = sys.argv[1] if len(sys.argv) > 1 else "trivy-image-results.sarif"
    max_vulns = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    vulns = parse_trivy_sarif(sarif_path, max_vulns)

    print(f"Found {len(vulns)} vulnerabilities", file=sys.stderr)

    if output_path:
        with open(output_path, "w") as f:
            json.dump(vulns, f, indent=2)
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(json.dumps(vulns, indent=2))
