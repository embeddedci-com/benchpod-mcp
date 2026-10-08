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

# Every launcher installs the same embeddedci-mcp requirement as the Desktop bundle.
spec = re.search(r'"(embeddedci-mcp[^"]*)"', (root / "mcpb/pyproject.toml").read_text()).group(1)
codex = json.loads((root / "plugins/benchpod/codex.mcp.json").read_text())["mcpServers"]["benchpod"]
specs = {
    "plugins/benchpod/bin/benchpod-mcp": re.search(r"^SPEC='([^']+)'", (root / "plugins/benchpod/bin/benchpod-mcp").read_text(), re.M).group(1),
    "plugins/benchpod/bin/benchpod-mcp.cmd": re.search(r'^set "SPEC=([^"]+)"', (root / "plugins/benchpod/bin/benchpod-mcp.cmd").read_text(), re.M).group(1),
    "plugins/benchpod/codex.mcp.json": codex["args"][codex["args"].index("--from") + 1],
}
bad_specs = {path: s for path, s in specs.items() if s != spec}
for path, s in bad_specs.items():
    print(f"{path}: installs {s}, mcpb/pyproject.toml pins {spec}")

sys.exit(1 if bad or bad_specs else 0)
