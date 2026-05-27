#!/usr/bin/env python3
"""
Genera un dashboard HTML con los resultados de seguridad
a partir de los ficheros SARIF generados por Trivy y Checkov.
"""

import json
import sys
import os
from datetime import datetime

def parse_sarif(filepath):
    """Extrae findings de un fichero SARIF."""
    findings = []
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} no existe, saltando...")
        return findings
    try:
        with open(filepath) as f:
            data = json.load(f)
        for run in data.get("runs", []):
            tool = run.get("tool", {}).get("driver", {}).get("name", "Unknown")
            for result in run.get("results", []):
                level = result.get("level", "warning")
                message = result.get("message", {}).get("text", "")[:200]
                locations = result.get("locations", [])
                location = ""
                if locations:
                    loc = locations[0].get("physicalLocation", {})
                    uri = loc.get("artifactLocation", {}).get("uri", "")
                    line = loc.get("region", {}).get("startLine", "")
                    location = f"{uri}:{line}" if line else uri
                rule_id = result.get("ruleId", "")
                findings.append({
                    "tool": tool,
                    "level": level,
                    "rule_id": rule_id,
                    "message": message,
                    "location": location
                })
    except Exception as e:
        print(f"Warning: could not parse {filepath}: {e}")
    return findings

def severity_color(level):
    colors = {
        "error": "#f85149",
        "warning": "#d29922",
        "note": "#58a6ff",
        "none": "#8b949e"
    }
    return colors.get(level, "#8b949e")

def severity_badge(level):
    labels = {
        "error": "HIGH/CRITICAL",
        "warning": "MEDIUM",
        "note": "LOW",
        "none": "INFO"
    }
    return labels.get(level, level.upper())

def generate_html(all_findings, commit, timestamp):
    total = len(all_findings)
    errors = sum(1 for f in all_findings if f["level"] == "error")
    warnings = sum(1 for f in all_findings if f["level"] == "warning")
    notes = sum(1 for f in all_findings if f["level"] == "note")

    rows = ""
    for f in all_findings:
        color = severity_color(f["level"])
        badge = severity_badge(f["level"])
        rows += f"""
        <tr>
          <td><span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44">{badge}</span></td>
          <td><code>{f['tool']}</code></td>
          <td><code>{f['rule_id']}</code></td>
          <td>{f['message']}</td>
          <td><code>{f['location']}</code></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Security Dashboard — TFM GitOps Platform</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #0d1117; color: #e6edf3; padding: 24px; }}
    h1 {{ font-size: 24px; color: #58a6ff; margin-bottom: 4px; }}
    .subtitle {{ color: #8b949e; font-size: 13px; margin-bottom: 24px; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; text-align: center; }}
    .card .num {{ font-size: 32px; font-weight: 800; }}
    .card .label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
    .card.red .num {{ color: #f85149; }}
    .card.yellow .num {{ color: #d29922; }}
    .card.blue .num {{ color: #58a6ff; }}
    .card.gray .num {{ color: #8b949e; }}
    table {{ width: 100%; border-collapse: collapse; background: #161b22;
             border: 1px solid #30363d; border-radius: 10px; overflow: hidden; }}
    th {{ background: #21262d; padding: 10px 14px; text-align: left;
          font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }}
    td {{ padding: 10px 14px; font-size: 13px; border-top: 1px solid #21262d;
          vertical-align: top; max-width: 300px; word-break: break-word; }}
    tr:hover td {{ background: #1c2128; }}
    .badge {{ padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap; }}
    code {{ font-family: monospace; font-size: 12px; color: #79c0ff; }}
    .meta {{ font-size: 11px; color: #8b949e; margin-bottom: 16px; }}
    .empty {{ text-align: center; padding: 40px; color: #8b949e; }}
  </style>
</head>
<body>
  <h1>🔒 Security Dashboard</h1>
  <p class="subtitle">AI-Powered GitOps Platform — TFM Máster Multicloud & DevOps</p>
  <p class="meta">
    Generated: {timestamp} &nbsp;|&nbsp;
    Commit: <code>{commit[:8]}</code> &nbsp;|&nbsp;
    Tools: Trivy · Checkov · Grype
  </p>

  <div class="cards">
    <div class="card gray"><div class="num">{total}</div><div class="label">Total Findings</div></div>
    <div class="card red"><div class="num">{errors}</div><div class="label">High / Critical</div></div>
    <div class="card yellow"><div class="num">{warnings}</div><div class="label">Medium</div></div>
    <div class="card blue"><div class="num">{notes}</div><div class="label">Low / Info</div></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Severity</th>
        <th>Tool</th>
        <th>Rule</th>
        <th>Description</th>
        <th>Location</th>
      </tr>
    </thead>
    <tbody>
      {"".join([rows]) if all_findings else '<tr><td colspan="5" class="empty">✅ No findings found</td></tr>'}
    </tbody>
  </table>
</body>
</html>"""

if __name__ == "__main__":
    # Checkov genera results_sarif.sarif dentro de una carpeta
    # con el nombre del fichero — bug conocido de bridgecrewio/checkov-action
    sarif_files = [
        ("trivy-image-sarif/trivy-image-results.sarif", "trivy-image-results.sarif"),
        ("trivy-iac-sarif/trivy-iac-results.sarif", "trivy-iac-results.sarif"),
        ("checkov-results/checkov-terraform-results.sarif/results_sarif.sarif", "checkov-terraform-results.sarif"),
        ("checkov-results/checkov-k8s-results.sarif/results_sarif.sarif", "checkov-k8s-results.sarif"),
        ("checkov-results/checkov-dockerfile-results.sarif/results_sarif.sarif", "checkov-dockerfile-results.sarif"),
    ]

    all_findings = []
    for filepath, label in sarif_files:
        findings = parse_sarif(filepath)
        print(f"{label}: {len(findings)} findings")
        all_findings.extend(findings)

    commit = os.getenv("GITHUB_SHA", "local")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = generate_html(all_findings, commit, timestamp)

    with open("index.html", "w") as f:
        f.write(html)

    print(f"Dashboard generado: {len(all_findings)} findings totales")
