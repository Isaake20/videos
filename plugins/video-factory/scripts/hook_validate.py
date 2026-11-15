#!/usr/bin/env python3
"""PostToolUse hook: every time a script.json is written, validate it and feed problems back to the agent."""
import json, os, subprocess, sys
try:
    fp = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)
if os.path.basename(fp) != "script.json" or "/work/" not in fp:
    sys.exit(0)
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_script.py"), fp],
                   capture_output=True, text=True)
if r.returncode:
    print(r.stderr, file=sys.stderr); sys.exit(2)  # exit 2 = show the problems to the agent
