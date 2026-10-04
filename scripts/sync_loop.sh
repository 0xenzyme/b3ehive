#!/bin/bash
# Copy looper's loop module into the other four skills. Looper owns the source.
# --check reports drift without writing.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT_DIR}/looper-cron-builder/loop.md"
check=0; [[ "${1:-}" == "--check" ]] && check=1
drift=0
for skill in compete-cron-builder execution-cron-builder learn-cron-builder optimization-cron-builder; do
  dst="${ROOT_DIR}/${skill}/references/loop.md"
  if cmp -s "$SRC" "$dst"; then continue; fi
  if [[ $check -eq 1 ]]; then echo "DRIFT: ${skill}/references/loop.md" >&2; drift=1; else mkdir -p "$(dirname "$dst")"; cp "$SRC" "$dst"; echo "Synced ${skill}/references/loop.md"; fi
done
exit $drift
