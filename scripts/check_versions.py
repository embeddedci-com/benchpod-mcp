"""Fail unless every manifest carries the same version (and, given one, that version)."""
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
versions = {
    "plugins/benchpod/.claude-plugin/plugin.json": json.loads((root / "plugins/benchpod/.claude-plugin/plugin.json").read_text())["version"],
    "plugins/benchpod/.codex-plugin/plugin.json": json.loads((root / "plugins/benchpod/.codex-plugin/plugin.json").read_text())["version"],
    "mcpb/manifest.json": json.loads((root / "mcpb/manifest.json").read_text())["version"],
    "mcpb/pyproject.toml": re.search(r'^version = "([^"]+)"', (root / "mcpb/pyproject.toml").read_text(), re.M).group(1),
}
expected = sys.argv[1] if len(sys.argv) > 1 else next(iter(versions.values()))
bad = {path: v for path, v in versions.items() if v != expected}
for path, v in bad.items():
    print(f"{path}: version {v}, expected {expected}")
sys.exit(1 if bad else 0)
