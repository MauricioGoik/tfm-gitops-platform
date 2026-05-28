#!/usr/bin/env python3
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/vulnerabilities.json'
try:
    data = json.load(open(path))
    print(len(data) if isinstance(data, list) else 0)
except Exception:
    print(0)
