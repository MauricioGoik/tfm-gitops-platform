#!/usr/bin/env python3
"""
Parsea el output SARIF de Trivy y extrae vulnerabilidades
HIGH y CRITICAL para pasarlas al agente IA.
"""

import json
import sys
import os


def parse_trivy_sarif(sarif_path: str, max_vulns: int = 3) -> list:
    if not os.path.exists(sarif_path):
        print(f"Error: {sarif_path} no existe", file=sys.stderr)
        return []

    with open(sarif_path) as f:
        sarif = json.load(f)

    vulnerabilities = []
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
            properties = rule.get("properties", {})
            help_text = rule.get("help", {}).get("text", "")

            fixed_version = "unknown"
            if "fixed version:" in help_text.lower():
                for line in help_text.split("\n"):
                    if "fixed version:" in line.lower():
                        fixed_version = line.split(":")[-1].strip()
                        break

            severity = "CRITICAL" if level == "error" else "HIGH"

            message = result.get("message", {}).get("text", "")

            # Extraer nombre del paquete del mensaje
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

            vuln = {
                "cve_id": rule_id,
                "package": package_name,
                "version": version,
                "fixed_version": fixed_version,
                "severity": severity,
                "image": os.getenv("IMAGE_NAME", "ghcr.io/mauriciogoik/demo-web:latest"),
                "description": message[:200]
            }

            vulnerabilities.append(vuln)

            if len(vulnerabilities) >= max_vulns:
                break

        if len(vulnerabilities) >= max_vulns:
            break

    return vulnerabilities


if __name__ == "__main__":
    sarif_path = sys.argv[1] if len(sys.argv) > 1 else "trivy-image-results.sarif"
    max_vulns = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    vulns = parse_trivy_sarif(sarif_path, max_vulns)

    # Siempre imprime el conteo en stderr para no contaminar stdout
    print(f"Found {len(vulns)} vulnerabilities", file=sys.stderr)

    # JSON puro en stdout o en fichero
    if output_path:
        with open(output_path, "w") as f:
            json.dump(vulns, f, indent=2)
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(json.dumps(vulns, indent=2))
