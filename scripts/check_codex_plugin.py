"""Check a Codex plugin against the rules Codex applies when it installs one.

A trimmed copy of the plugin-creator validator in openai/codex: required fields, https URLs,
asset files that exist, at most 3 starter prompts of 128 characters, and an mcpServers path
(the Codex releases we tested reject an inline object).
"""
import json
import re
import sys
from pathlib import Path

plugin = Path(sys.argv[1])
manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
errors = []

for field in ("name", "version", "description"):
    if not manifest.get(field):
        errors.append(f"missing {field}")
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", manifest.get("name", "")):
    errors.append("name must be kebab-case")
if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
    errors.append("version must be strict semver")
if not manifest.get("author", {}).get("name"):
    errors.append("missing author.name")

servers = manifest.get("mcpServers")
if not isinstance(servers, str) or not servers.startswith("./"):
    errors.append("mcpServers must be a ./ path to a JSON file")
elif not (plugin / servers).is_file():
    errors.append(f"mcpServers file {servers} does not exist")
else:
    json.loads((plugin / servers).read_text())["mcpServers"]

ui = manifest.get("interface", {})
for field in ("displayName", "shortDescription", "developerName", "category"):
    if not ui.get(field):
        errors.append(f"missing interface.{field}")
for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
    if not str(ui.get(field, "")).startswith("https://"):
        errors.append(f"interface.{field} must be an https URL")
for field in ("composerIcon", "logo", "logoDark"):
    if field in ui and not (plugin / ui[field]).is_file():
        errors.append(f"interface.{field} {ui[field]} does not exist")
prompts = ui.get("defaultPrompt", [])
if len(prompts) > 3 or any(len(p) > 128 for p in prompts):
    errors.append("interface.defaultPrompt: at most 3 prompts of 128 characters")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
