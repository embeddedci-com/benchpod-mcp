#!/bin/sh
# Checks plugins/emi-analyzer/bin/emi-analyzer-mcp without an EMI Analyzer install: it explains
# a missing app, refuses one older than the MCP server, and runs `mcp` on a recent one.
set -u
launcher="$(cd "$(dirname "$0")/.." && pwd)/plugins/emi-analyzer/bin/emi-analyzer-mcp"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fail=0

fake() { # fake <version>: an emi-local that prints its version, or what it was asked to run
  printf '#!/bin/sh\n[ "$1" = -version ] && echo %s && exit 0\necho "ran $*"\n' "$1" > "$tmp/emi-local"
  chmod +x "$tmp/emi-local"
}
run() { EMI_LOCAL="$1" PATH=/usr/bin:/bin HOME="$tmp" sh "$launcher" </dev/null 2>"$tmp/err"; }

out=$(run "")
if [ -n "$out" ] || ! grep -q "was not found" "$tmp/err"; then echo "missing app: got '$out' / $(cat "$tmp/err")"; fail=1; fi

fake 0.3.0; out=$(run "$tmp/emi-local")
if [ -n "$out" ] || ! grep -q "needs 0.4.0 or newer" "$tmp/err"; then echo "old app: got '$out' / $(cat "$tmp/err")"; fail=1; fi

for v in 0.4.0 0.10.2 1.0.0 dev; do
  fake "$v"; out=$(run "$tmp/emi-local")
  if [ "$out" != "ran mcp" ]; then echo "version $v: got '$out' / $(cat "$tmp/err")"; fail=1; fi
done

[ "$fail" = 0 ] && echo "emi-analyzer launcher: ok"
exit "$fail"
