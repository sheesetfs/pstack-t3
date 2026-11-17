#!/bin/sh
# Print pstack-t3's session-start note, unless the roles file turns it off.
set -eu

roles="${XDG_CONFIG_HOME:-${HOME:-}/.config}/pstack-t3/roles.json"
here=$(dirname "$0")

# Only a top-level "sessionHook": false turns the note off. A missing, unreadable, or invalid roles file keeps it on.
if [ -r "$roles" ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if isinstance(d, dict) and d.get("sessionHook") is False else 1)' "$roles" 2>/dev/null; then
  exit 0
fi

if [ -r "$here/session-start-context.md" ]; then
  cat "$here/session-start-context.md"
fi
