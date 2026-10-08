"""Write (or check) the tool list in mcpb/manifest.json from the MCP server's own tool surface.

Run it in a Python environment where the server (the embeddedci-mcp package, at the version the
plugin pins) is importable; uv does that in one line:

    uv run --no-project --with "$(python3 scripts/gen_tools.py --spec)" python scripts/gen_tools.py
    uv run --no-project --with "$(python3 scripts/gen_tools.py --spec)" python scripts/gen_tools.py --check

Each tool's description is the first paragraph of the server's own description, except for the
few in OVERRIDES that the extension listing words differently. --check exits 1 when the manifest
differs from what the server reports (a tool added, removed, renamed or reworded), or when the
Codex tool timeout is shorter than the longest flash the server accepts.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
MANIFEST = root / "mcpb/manifest.json"
PYPROJECT = root / "mcpb/pyproject.toml"
CODEX = root / "plugins/benchpod/codex.mcp.json"

#: Listing texts that say more than the server's first paragraph (kept short for the extension
#: directory). Every key must be a tool the server has.
OVERRIDES = {
    "current_out": "Hold a current on the 4-20 mA output (terminal J9, needs an external floating "
                   "loop supply), in amps, or read the range it can do.",
    "list_waveforms": "The organisation's cloud waveform library (needs a cloud connection, "
                      "BENCHPOD_API_KEY or `benchpod login`).",
    "cloud_list_devices": "The BenchPods registered to your embeddedci.com organisation, and "
                          "whether each is online. Needs no pod connection.",
}


def spec() -> str:
    """The embeddedci-mcp requirement the bundle (and every launcher) pins."""
    m = re.search(r'"(embeddedci-mcp[^"]*)"', PYPROJECT.read_text())
    if not m:
        raise SystemExit(f"{PYPROJECT}: no embeddedci-mcp dependency")
    return m.group(1)


def _list_tools() -> list:
    import anyio
    from embeddedci_mcp.server import mcp

    return anyio.run(mcp.list_tools)


def flash_max_seconds(tools: list) -> float:
    """The longest timeout the flash tool accepts (its input schema's maximum)."""
    for t in tools:
        if t.name == "flash":
            return float(t.inputSchema["properties"]["timeout"]["maximum"])
    raise SystemExit("the server has no flash tool")


def codex_timeout_problem(tools: list) -> str:
    """Codex ends a tool call after tool_timeout_sec: it must cover the longest flash."""
    have = json.loads(CODEX.read_text())["mcpServers"]["benchpod"].get("tool_timeout_sec", 0)
    need = flash_max_seconds(tools)
    if have < need:
        return (f"{CODEX.relative_to(root)}: tool_timeout_sec {have} is below the flash tool's "
                f"maximum timeout of {need:g} s")
    return ""


def server_tools(tools: list) -> list:
    names = {t.name for t in tools}
    unknown = sorted(set(OVERRIDES) - names)
    if unknown:
        raise SystemExit(f"OVERRIDES name tools the server does not have: {', '.join(unknown)}")
    out = []
    for t in tools:
        first = (t.description or "").strip().split("\n\n")[0]
        out.append({"name": t.name, "description": OVERRIDES.get(t.name, " ".join(first.split()))})
    return out


def main(argv: list) -> int:
    if argv == ["--spec"]:
        print(spec())
        return 0
    check = argv == ["--check"]
    if argv and not check:
        raise SystemExit(f"usage: {sys.argv[0]} [--check | --spec]")
    manifest = json.loads(MANIFEST.read_text())
    tools = _list_tools()
    want = server_tools(tools)
    have = manifest.get("tools", [])
    problem = codex_timeout_problem(tools)
    if problem:
        print(problem)
    if check:
        if have == want and not problem:
            print(f"ok: {MANIFEST.relative_to(root)} lists the server's {len(want)} tools")
            return 0
        if have == want:
            return 1  # only the timeout, already reported
        have_by = {t["name"]: t["description"] for t in have}
        want_by = {t["name"]: t["description"] for t in want}
        for name in sorted(set(want_by) - set(have_by)):
            print(f"missing: {name}")
        for name in sorted(set(have_by) - set(want_by)):
            print(f"not in the server: {name}")
        for name in sorted(set(have_by) & set(want_by)):
            if have_by[name] != want_by[name]:
                print(f"description of {name}:\n  manifest: {have_by[name]}\n  server:   {want_by[name]}")
        if set(have_by) == set(want_by) and all(have_by[n] == want_by[n] for n in have_by):
            print("tool order differs from the server's")
        print(f"{MANIFEST.relative_to(root)} is out of date with {spec()}; regenerate it:\n"
              f"  uv run --no-project --with \"{spec()}\" python scripts/gen_tools.py")
        return 1
    manifest["tools"] = want
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(want)} tools to {MANIFEST.relative_to(root)}")
    return 1 if problem else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
