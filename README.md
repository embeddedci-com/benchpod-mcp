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

- Nothing else to install for the server: the Claude Code and Codex plugins use your
  [uv](https://docs.astral.sh/uv/) if you have it and otherwise install a private copy on first
  start (macOS, Linux and Windows); the Claude Desktop extension brings its own.
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
**Plugins**. For a cloud pod use `connection=embeddedci:<device>`, and either run `benchpod login` once on
this computer or add `--config api_key=eci_…`. The agent can list your cloud pods with
`cloud_list_devices`.
Change a setting later by running the install command again with `--config`, or with
`/plugin configure benchpod@benchpod-mcp` in a terminal session.

## Codex

In the Codex app, open **Settings** → **Plugins**, add the marketplace
`embeddedci-com/benchpod-mcp` and install **BenchPod**. From the Codex CLI:

```bash
codex plugin marketplace add embeddedci-com/benchpod-mcp
```

Then open `/plugins` in Codex and install **BenchPod**.

The plugin starts the server with `bin/benchpod-mcp` (`bin/benchpod-mcp.cmd` on Windows), the same
launcher as the Claude Code plugin. It uses your uv, also when it lives in `~/.local/bin`,
`/opt/homebrew/bin` or `/usr/local/bin` and the app was started without those on its `PATH`.
Without uv it installs a private copy in `~/.local/share/benchpod-mcp` (`%LOCALAPPDATA%\benchpod-mcp`
on Windows) on first start, which takes a minute.

Codex passes these environment variables from your shell to the server, so set them before
starting Codex:

```bash
export BENCHPOD_CONNECTION=192.168.1.213 BENCHPOD_LA_VOLTAGE=3.3
```

`BENCHPOD_API_KEY` (cloud pods) and `BENCHPOD_API_BASE` (another embeddedci server) are passed
through the same way.

## Claude app chat

To use the bench from a chat instead of a Code session, download `benchpod.mcpb` from the
[latest release](https://github.com/embeddedci-com/benchpod-mcp/releases/latest) and open it. The
app installs the extension and asks for the settings below.

## Settings

| Setting | Environment variable | |
| --- | --- | --- |
| BenchPod connection | `BENCHPOD_CONNECTION` | The pod's IP address or `host[:port]`, `usb`, or `embeddedci:<device>` for a cloud pod. Leave it empty to tell the agent in chat. |
| Board I/O voltage | `BENCHPOD_LA_VOLTAGE` | `3.3` or `1.8`. Leave it empty and the agent sets it before using the pins. |
| API key | `BENCHPOD_API_KEY` | For cloud pods and the waveform library. Optional if you have run [`benchpod login`](https://github.com/embeddedci-com/benchpod-cli) on this computer: its session (`~/.config/benchpod-cli/token.json`) is used instead. Create a key at [embeddedci.com/api-keys](https://www.embeddedci.com/api-keys). |

## Try it

> Connect to the bench and show me its wiring.

> Flash `build/app.elf`, power-cycle the board and tell me if it prints `APP_OK`.

> Pretend to be a BMP280 at 25 °C and check the firmware reads it.

Tools that switch power, flash firmware or drive voltages are marked destructive, so your client asks
before running them.

## Tools

The plugin ships every tool of the MCP server. The [MCP server docs](https://www.embeddedci.com/docs/benchpod-mcp)
describe each one with its parameters and defaults.

| Group | Tools |
| --- | --- |
| Connection | `connect`, `disconnect`, `status`, `set_la_voltage` |
| Cloud (embeddedci.com) | `cloud_list_devices` |
| Wiring profile | `wiring`, `set_wiring` |
| Power | `power_on`, `power_off`, `power_status`, `reset_target` |
| Power profiles | `measure_power`, `power_profile_start`, `power_profile_stop` |
| Flash | `flash` |
| SPI flash and SPI devices | `spi_flash_info`, `spi_flash_program`, `spi_flash_read`, `spi_transfer` |
| UART | `capture_uart`, `power_cycle_and_capture`, `uart_open`, `uart_write`, `uart_read`, `uart_close` |
| Emulated I2C sensor (BMP280, BME280, SHT4x, MPU-6050) | `enable_i2c_sensor`, `set_i2c_sensor`, `disable_i2c_sensor`, `i2c_sensor_status`, `i2c_sensor_types`, `i2c_sensor_regs`, `i2c_sensor_capture` |
| Emulated GPS receiver | `enable_gps`, `set_gps`, `disable_gps`, `gps_status` |
| Pull resistors | `set_pull`, `pull_status` |
| GPIO on the LA pins | `la_pins`, `gpio_mode`, `gpio_write`, `gpio_read`, `gpio_wait`, `gpio_pulse`, `gpio_release` |
| Analog | `analog_path`, `dac_output`, `current_out`, `adc_read`, `calibration`, `calibrate` |
| Capture and decode | `capture_adc`, `capture_la`, `capture_correlated`, `decode_la`, `la_timing` |
| DAC | `generate`, `dac_stop`, `replay`, `list_waveforms`, `replay_waveform`, `save_capture_as_recording` |
| Control loop | `control_loop`, `loop_input`, `loop_probe`, `fpga_image` |
| CAN | `can_open`, `can_write`, `can_read`, `can_respond`, `can_status`, `can_close` |
| Other | `la_step`, `command` |

If the pod or embeddedci.com refuses a command, the tool error names why (for example
`PodLockedError`, `PodLeasedError`, `PodBusyError`, `PermissionDeniedError` or `TransportTimeout`)
and adds a one-line hint, so the agent can tell you what to change. `status` lists the pod's
capabilities, so the agent knows which tools that pod supports.

## Privacy Policy

The MCP server runs on your computer and talks directly to your BenchPod. It has no telemetry and no
usage analytics. It sends data to embeddedci.com only when you use a cloud pod, the waveform library or
a saved wiring profile; those requests carry your API key (or your `benchpod login` session) and the commands and data of that
request.
Your AI client sees the tool calls it makes and their results, under its own privacy policy.

Full policy: [embeddedci.com/privacy](https://www.embeddedci.com/privacy). Terms:
[embeddedci.com/terms](https://www.embeddedci.com/terms).

## Support

Open an [issue](https://github.com/embeddedci-com/benchpod-mcp/issues) or email
[hello@embeddedci.com](mailto:hello@embeddedci.com).

## Layout

| Path | |
| --- | --- |
| `plugins/benchpod/` | The plugin: `.claude-plugin/plugin.json` (Claude Code), `.codex-plugin/plugin.json` + `codex.mcp.json` (Codex), `bin/benchpod-mcp` and `bin/benchpod-mcp.cmd` (the launcher both plugins run, for macOS/Linux and Windows) |
| `.claude-plugin/marketplace.json` | Claude Code marketplace |
| `.agents/plugins/marketplace.json` | Codex marketplace |
| `mcpb/` | Claude Desktop extension, built into `benchpod.mcpb` by the release workflow |
| `scripts/gen_tools.py` | Writes the extension's tool list (`mcpb/manifest.json`) from the MCP server itself; CI fails when it is out of date |
| `scripts/check_readme_tools.py` | Checks that the Tools table in this README lists exactly the tools in `mcpb/manifest.json` |

After an embeddedci-mcp release that adds, removes or rewords a tool, regenerate the list:

```sh
uv run --no-project --with "$(python3 scripts/gen_tools.py --spec)" python scripts/gen_tools.py
```

Then add any new tool to the Tools table above; `python3 scripts/check_readme_tools.py` says which.

## License

[Apache-2.0](LICENSE)
