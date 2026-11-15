#!/usr/bin/env python3
"""PreToolUse hook on Bash: a final (non-draft) pipeline run needs a passing QA verdict first."""
import json, os, re, sys
try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    sys.exit(0)
m = re.search(r"pipeline\.py\s+([\w-]+)", cmd)
if not m or "--draft" in cmd:
    sys.exit(0)
root = os.environ.get("VF_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
qa = os.path.join(root, "work", m.group(1), "qa.json")
try:
    ok = json.load(open(qa)).get("verdict") == "pass"
except Exception:
    ok = False
if not ok:
    print(f"Blocked: {qa} has no passing verdict. Run the qa-reviewer agent on this script before the final render.", file=sys.stderr)
    sys.exit(2)
