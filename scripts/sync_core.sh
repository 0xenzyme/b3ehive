#!/bin/bash
# Copy the shared core files into every skill so each skill stands alone.
# --check reports drift without writing.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS=(compete-cron-builder execution-cron-builder learn-cron-builder optimization-cron-builder looper-cron-builder)
FILES=(core.md substrate-cron.md)
check=0; [[ "${1:-}" == "--check" ]] && check=1
drift=0
for skill in "${SKILLS[@]}"; do
  mkdir -p "${ROOT_DIR}/${skill}/references"
  for f in "${FILES[@]}"; do
    src="${ROOT_DIR}/core/${f}"; dst="${ROOT_DIR}/${skill}/references/${f}"
    if cmp -s "$src" "$dst"; then continue; fi
    if [[ $check -eq 1 ]]; then echo "DRIFT: ${skill}/references/${f}" >&2; drift=1; else cp "$src" "$dst"; echo "Synced ${skill}/references/${f}"; fi
  done
done
exit $drift
