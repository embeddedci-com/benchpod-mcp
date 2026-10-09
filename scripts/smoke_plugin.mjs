// Start the plugin's MCP server the way a client does, and list its tools.
//
// SMOKE_CLIENT unset (Claude Code) runs the command .claude-plugin/plugin.json declares; codex runs
// the one in codex.mcp.json from its cwd (Codex resolves a relative cwd against the plugin root)
// with only the environment Codex passes on. Both are the extensionless bin/benchpod-mcp: on
// Windows the MCP SDK's stdio transport (cross-spawn) resolves it through PATHEXT to
// bin/benchpod-mcp.cmd, as Codex does; elsewhere it runs the sh launcher. SMOKE_HIDE_UV=1 drops
// every PATH entry holding uvx, so the launcher has to find uv elsewhere or install a private copy.
//
//   npm install --no-save --prefix scripts @modelcontextprotocol/sdk
//   node scripts/smoke_plugin.mjs
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const plugin = path.join(root, "plugins/benchpod");
const read = (file) => JSON.parse(fs.readFileSync(path.join(plugin, file), "utf8"));
const codex = process.env.SMOKE_CLIENT === "codex";

let server, command, cwd, env;
if (codex) {
  server = read(read(".codex-plugin/plugin.json").mcpServers).mcpServers.benchpod;
  command = server.command;
  cwd = path.resolve(plugin, server.cwd ?? ".");
  // The variables Codex hands every stdio server (codex-rs rmcp-client DEFAULT_ENV_VARS and
  // WINDOWS_CORE_ENV_VARS), plus the server's env_vars. The data folder comes from HOME or
  // LOCALAPPDATA: Codex has no CLAUDE_PLUGIN_DATA.
  const pass = new Set([
    "HOME", "LOGNAME", "PATH", "SHELL", "USER", "LANG", "LC_ALL", "TERM", "TMPDIR", "TZ",
    "PATHEXT", "COMSPEC", "SYSTEMROOT", "WINDIR", "SYSTEMDRIVE", "USERNAME", "USERDOMAIN",
    "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432",
    "PROGRAMDATA", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP", ...(server.env_vars ?? [])]);
  env = Object.fromEntries(Object.entries(process.env).filter(([k]) => pass.has(k.toUpperCase())));
  const data = fs.mkdtempSync(path.join(os.tmpdir(), "benchpod-home-"));
  if (process.platform === "win32") env.LOCALAPPDATA = data;
  else env.HOME = data;
} else {
  server = read(".claude-plugin/plugin.json").mcpServers.benchpod;
  command = server.command.replace("${CLAUDE_PLUGIN_ROOT}", plugin);
  env = { ...process.env, CLAUDE_PLUGIN_DATA: fs.mkdtempSync(path.join(os.tmpdir(), "benchpod-data-")) };
}
if (process.env.SMOKE_HIDE_UV) {
  const key = Object.keys(env).find((k) => k.toUpperCase() === "PATH");
  const exe = process.platform === "win32" ? "uvx.exe" : "uvx";
  env[key] = env[key].split(path.delimiter).filter((d) => !fs.existsSync(path.join(d, exe))).join(path.delimiter);
}

const transport = new StdioClientTransport({ command, args: server.args ?? [], env, cwd, stderr: "inherit" });
const client = new Client({ name: "benchpod-smoke", version: "1.0.0" });
// The first start downloads uv, Python and the server, which can take a few minutes.
await client.connect(transport, { timeout: 600_000 });
const { tools } = await client.listTools();
const names = tools.map((t) => t.name);
await client.close();

for (const want of ["connect", "status", "cloud_list_devices"]) {
  if (!names.includes(want)) {
    console.error(`missing tool ${want}; got ${names.length}: ${names.join(", ")}`);
    process.exit(1);
  }
}
console.log(`ok: ${names.length} tools on ${process.platform} via ${command}${codex ? " (codex)" : ""}`);
