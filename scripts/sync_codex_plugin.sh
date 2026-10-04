#!/bin/bash
# Sync shared units, then copy the five skills into the Codex plugin package.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_SKILLS_DIR="${ROOT_DIR}/plugins/b3ehive/skills"
SKILLS=(compete-cron-builder execution-cron-builder learn-cron-builder optimization-cron-builder looper-cron-builder)

"${ROOT_DIR}/scripts/sync_core.sh" >/dev/null
"${ROOT_DIR}/scripts/sync_loop.sh" >/dev/null
mkdir -p "$PLUGIN_SKILLS_DIR"
for skill in "${SKILLS[@]}"; do
  [[ -f "${ROOT_DIR}/${skill}/SKILL.md" ]] || { echo "Missing skill source: ${skill}" >&2; exit 1; }
  rm -rf "${PLUGIN_SKILLS_DIR:?}/${skill}"
  cp -a "${ROOT_DIR}/${skill}" "${PLUGIN_SKILLS_DIR}/${skill}"
  find "${PLUGIN_SKILLS_DIR}/${skill}" -name '__pycache__' -prune -exec rm -rf {} +
  echo "Synced ${skill}"
done
echo "Codex plugin skills synced: ${PLUGIN_SKILLS_DIR}"
