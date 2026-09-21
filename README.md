# BenchPod for Claude and Codex

Plugins that connect Claude and Codex to an [EmbeddedCI BenchPod](https://www.embeddedci.com/docs/benchpod-mcp),
a hardware-in-the-loop tester wired to your board. The agent can flash a build over SWD, power-cycle
the board and wait for its boot log, type into its UART console, pretend to be the I2C sensor it
expects, capture logic and analog signals, drive voltages and talk CAN.

Every plugin here runs the same MCP server, [`embeddedci-mcp`](https://pypi.org/project/embeddedci-mcp/)
([source](https://github.com/embeddedci-com/embeddedci-python/tree/main/packages/embeddedci-mcp)), on
your computer through [`uvx`](https://docs.astral.sh/uv/). It talks to the pod over your network or
USB.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) on your `PATH` (the plugins start the
  server with `uvx`; the Claude Desktop extension brings its own).
- A BenchPod on your network, over USB, or in the embeddedci.com cloud.
- For flashing only: OpenOCD with the `cmsis_dap_tcp` backend (newer than 0.12.0, for example
  `brew install --HEAD open-ocd` or the xPack build).

## Claude Code and the Claude app

Install the [Claude Code CLI](https://code.claude.com/docs/en/setup) if you don't have it (the Claude
app does not add a `claude` command):

```bash
brew install --cask claude-code
```

Then add the plugin, with your pod's address and the board's I/O voltage:

```bash
claude plugin marketplace add embeddedci-com/benchpod-mcp
```

```bash
claude plugin install benchpod@benchpod-mcp --config connection=192.168.1.213 --config la_voltage=3.3
```

It works in terminal sessions and in the Claude app's Code tab, where it appears under **+** →
**Plugins**. For a cloud pod use `connection=embeddedci:<device>` and add `--config api_key=eci_…`.
Change a setting later by running the install command again with `--config`, or with
`/plugin configure benchpod@benchpod-mcp` in a terminal session.

## Codex

```bash
codex plugin marketplace add embeddedci-com/benchpod-mcp
```

Then open `/plugins` in Codex and install **BenchPod**. Codex passes these environment variables
from your shell to the server, so set them before starting Codex:

```bash
export BENCHPOD_CONNECTION=192.168.1.213 BENCHPOD_LA_VOLTAGE=3.3
```

## Claude app chat

To use the bench from a chat instead of a Code session, download `benchpod.mcpb` from the
[latest release](https://github.com/embeddedci-com/benchpod-mcp/releases/latest) and open it. The
app installs the extension and asks for the settings below.

## Settings

| Setting | Environment variable | |
| --- | --- | --- |
| BenchPod connection | `BENCHPOD_CONNECTION` | The pod's IP address or `host[:port]`, `usb`, or `embeddedci:<device>` for a cloud pod. Leave it empty to tell the agent in chat. |
| Board I/O voltage | `BENCHPOD_LA_VOLTAGE` | `3.3` or `1.8`. Leave it empty and the agent sets it before using the pins. |
| API key | `BENCHPOD_API_KEY` | Only for cloud pods and the waveform library. Create one at [embeddedci.com/api-keys](https://www.embeddedci.com/api-keys). |

## Try it

> Connect to the bench and show me its wiring.

> Flash `build/app.elf`, power-cycle the board and tell me if it prints `APP_OK`.

> Pretend to be a BMP280 at 25 °C and check the firmware reads it.

Tools that switch power, flash firmware or drive voltages are marked destructive, so your client asks
before running them. The [MCP server docs](https://www.embeddedci.com/docs/benchpod-mcp) list every tool.

## Privacy Policy

The MCP server runs on your computer and talks directly to your BenchPod. It has no telemetry and no
usage analytics. It sends data to embeddedci.com only when you use a cloud pod, the waveform library or
a saved wiring profile; those requests carry your API key and the commands and data of that request.
Your AI client sees the tool calls it makes and their results, under its own privacy policy.

Full policy: [embeddedci.com/privacy](https://www.embeddedci.com/privacy). Terms:
[embeddedci.com/terms](https://www.embeddedci.com/terms).

## Support

Open an [issue](https://github.com/embeddedci-com/benchpod-mcp/issues) or email
[hello@embeddedci.com](mailto:hello@embeddedci.com).

## Layout

| Path | |
| --- | --- |
| `plugins/benchpod/` | The plugin: `.claude-plugin/plugin.json` (Claude Code), `.codex-plugin/plugin.json` + `codex.mcp.json` (Codex) |
| `.claude-plugin/marketplace.json` | Claude Code marketplace |
| `.agents/plugins/marketplace.json` | Codex marketplace |
| `mcpb/` | Claude Desktop extension, built into `benchpod.mcpb` by the release workflow |

## License

[Apache-2.0](LICENSE)
