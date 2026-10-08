"""Fail unless the Tools table in README.md lists exactly the tools in mcpb/manifest.json.

gen_tools.py --check keeps the manifest equal to the MCP server's tools, so together the two
checks keep the README in step with the server the plugin installs. Needs only python3:

    python3 scripts/check_readme_tools.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
README = root / "README.md"
MANIFEST = root / "mcpb/manifest.json"


def readme_tools() -> list:
    text = README.read_text(encoding="utf-8")
    m = re.search(r"^## Tools\n(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        raise SystemExit(f"{README.name}: no '## Tools' section")
    names = []
    for row in re.findall(r"^\|[^|\n]*\|([^\n]*)\|\s*$", m.group(1), re.M):
        names += re.findall(r"`([a-z0-9_]+)`", row)
    return names


def main() -> int:
    want = [t["name"] for t in json.loads(MANIFEST.read_text())["tools"]]
    have = readme_tools()
    problems = []
    problems += [f"missing from the README: {n}" for n in want if n not in have]
    problems += [f"not in {MANIFEST.relative_to(root)}: {n}" for n in have if n not in want]
    problems += [f"listed {c} times: {n}" for n, c in Counter(have).items() if c > 1]
    for p in problems:
        print(p)
    if problems:
        print(f"update the Tools table in {README.name} to match {MANIFEST.relative_to(root)}")
        return 1
    print(f"ok: {README.name} lists the {len(want)} tools in {MANIFEST.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
