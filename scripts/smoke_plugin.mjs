// Start the Claude Code plugin's MCP server the way a client does, and list its tools.
//
// The command is the extensionless path plugin.json declares. On Windows the MCP SDK's stdio
// transport (cross-spawn) resolves it through PATHEXT to bin/benchpod-mcp.cmd; elsewhere it runs
// the sh launcher. SMOKE_HIDE_UV=1 drops every PATH entry holding uvx, so the launcher has to
// install its private uv first.
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
const manifest = JSON.parse(
  fs.readFileSync(path.join(root, "plugins/benchpod/.claude-plugin/plugin.json"), "utf8"));
const server = manifest.mcpServers.benchpod;
const command = server.command.replace("${CLAUDE_PLUGIN_ROOT}", path.join(root, "plugins/benchpod"));

const env = { ...process.env, CLAUDE_PLUGIN_DATA: fs.mkdtempSync(path.join(os.tmpdir(), "benchpod-data-")) };
if (process.env.SMOKE_HIDE_UV) {
  const key = Object.keys(env).find((k) => k.toUpperCase() === "PATH");
  const exe = process.platform === "win32" ? "uvx.exe" : "uvx";
  env[key] = env[key].split(path.delimiter).filter((d) => !fs.existsSync(path.join(d, exe))).join(path.delimiter);
}

const transport = new StdioClientTransport({ command, args: server.args ?? [], env, stderr: "inherit" });
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
console.log(`ok: ${names.length} tools on ${process.platform} via ${command}`);
