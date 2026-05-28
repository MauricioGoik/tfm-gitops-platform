#!/usr/bin/env python3
"""
Parsea el output SARIF de Trivy y extrae vulnerabilidades
HIGH y CRITICAL para pasarlas al agente IA.
"""

import json
import sys
import os


def parse_trivy_sarif(sarif_path: str, max_vulns: int = 3) -> list:
    """Extrae vulnerabilidades HIGH/CRITICAL del SARIF de Trivy."""

    if not os.path.exists(sarif_path):
        print(f"Error: {sarif_path} no existe")
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

            # Solo HIGH y CRITICAL
            if level not in ["error", "warning"]:
                continue

            # Evitar duplicados
            if rule_id in seen_cves:
                continue
            seen_cves.add(rule_id)

            rule = rules.get(rule_id, {})
            properties = rule.get("properties", {})
            help_text = rule.get("help", {}).get("text", "")

            # Extraer versión con fix del help text
            fixed_version = "unknown"
            if "fixed version:" in help_text.lower():
                for line in help_text.split("\n"):
                    if "fixed version:" in line.lower():
                        fixed_version = line.split(":")[-1].strip()
                        break

            # Extraer severidad
            severity = "HIGH"
            if level == "error":
                severity = "CRITICAL"
            elif level == "warning":
                severity = "HIGH"

            # Extraer nombre del paquete y versión del mensaje
            message = result.get("message", {}).get("text", "")
            package_name = properties.get("affected_version", "unknown")

            # El ruleId de Trivy es el CVE
            vuln = {
                "cve_id": rule_id,
                "package": rule.get("name", rule_id),
                "version": properties.get("affected_version", "unknown"),
                "fixed_version": fixed_version,
                "severity": severity,
                "image": os.getenv("IMAGE_NAME", "unknown"),
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

    vulns = parse_trivy_sarif(sarif_path, max_vulns)

    if not vulns:
        print("No HIGH/CRITICAL vulnerabilities found")
        print(json.dumps([]))
    else:
        print(f"Found {len(vulns)} vulnerabilities")
        print(json.dumps(vulns, indent=2))
