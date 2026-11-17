#!/bin/sh
# Print pstack-t3's session-start note, unless the roles file turns it off.
set -eu

roles="${XDG_CONFIG_HOME:-${HOME:-}/.config}/pstack-t3/roles.json"
here=$(dirname "$0")

# A roles file that is missing or that cannot be read counts as absent, so the note stays on.
if [ -r "$roles" ] && grep -Eq '"sessionHook"[[:space:]]*:[[:space:]]*false([[:space:]]*[,}])?' "$roles"; then
  exit 0
fi

if [ -r "$here/session-start-context.md" ]; then
  cat "$here/session-start-context.md"
fi
