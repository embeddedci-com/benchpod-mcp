# Contributing

Thanks for helping out. Issues and pull requests are welcome.

This repository only packages the BenchPod MCP server for Claude Code, Codex and Claude Desktop.
The server and its tools live in
[embeddedci-python](https://github.com/embeddedci-com/embeddedci-python/tree/main/packages/embeddedci-mcp);
open tool and behavior changes there.

## Before you open a pull request

- Open an issue first for anything larger than a small fix, so we can agree on the approach.
- Keep the version the same in every manifest; CI checks it:

  ```bash
  python3 scripts/check_versions.py
  python3 scripts/check_codex_plugin.py
  python3 scripts/check_readme_tools.py
  ```

- Install the plugin from your branch in Claude Code or Codex and try a tool against a BenchPod
  (or at least `status` without one). Say how in the pull request.
- Keep commits small and focused, and describe what changed and why.

## Releases

Maintainers bump the version in all manifests and push a `v<version>` tag; the release workflow
attaches `benchpod.mcpb`.

## Security

Report vulnerabilities privately, see [SECURITY.md](SECURITY.md).
