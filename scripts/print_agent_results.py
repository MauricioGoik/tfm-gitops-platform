#!/usr/bin/env python3
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/agent-response.json'
try:
    resp = json.load(open(path))
    body = json.loads(resp.get('body', '{}'))
    results = body.get('results', [])
    print('### 🤖 AI Agent Results')
    for r in results:
        if r.get('pr_url'):
            print(f"- PR created: {r['pr_url']}")
        elif r.get('error'):
            print(f"- Error for {r['cve_id']}: {r['error']}")
except Exception as e:
    print(f'Error parsing response: {e}')
