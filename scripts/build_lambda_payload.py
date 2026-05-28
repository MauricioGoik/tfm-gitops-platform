#!/usr/bin/env python3
import json
import sys

vulns_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/vulnerabilities.json'
repo = sys.argv[2] if len(sys.argv) > 2 else ''
token = sys.argv[3] if len(sys.argv) > 3 else ''

try:
    vulns = json.load(open(vulns_path))
    if not isinstance(vulns, list):
        vulns = []
except Exception:
    vulns = []

payload = {
    'vulnerabilities': vulns,
    'repo': repo,
    'github_token': token
}
print(json.dumps(payload))
