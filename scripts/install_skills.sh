#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILLS=(
  debating-cron-builder
  execution-cron-builder
  research-cron-builder
  optimization-cron-builder
  migration-cron-builder
)

usage() {
  cat <<'USAGE'
Usage: scripts/install_skills.sh [--target codex|claude|both] [--scope user|project] [--project-dir PATH] [--dry-run]

Installs b3ehive's five portable SKILL.md directories for Codex, Claude Code, or both.

Defaults:
  --target both
  --scope user
  --project-dir .

Install roots:
  Codex user:        ~/.codex/skills
  Claude Code user:  ~/.claude/skills
  Codex project:     <project-dir>/.codex/skills
  Claude project:    <project-dir>/.claude/skills
USAGE
}

target="both"
scope="user"
project_dir="."
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      target="${2:?missing value for --target}"
      shift 2
      ;;
    --scope)
      scope="${2:?missing value for --scope}"
      shift 2
      ;;
    --project-dir)
      project_dir="${2:?missing value for --project-dir}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$target" in
  codex|claude|both) ;;
  *)
    echo "--target must be codex, claude, or both" >&2
    exit 2
    ;;
esac

case "$scope" in
  user|project) ;;
  *)
    echo "--scope must be user or project" >&2
    exit 2
    ;;
esac

install_root() {
  local platform="$1"
  if [[ "$scope" == "user" ]]; then
    case "$platform" in
      codex) printf '%s\n' "${HOME}/.codex/skills" ;;
      claude) printf '%s\n' "${HOME}/.claude/skills" ;;
    esac
  else
    case "$platform" in
      codex) printf '%s\n' "${project_dir}/.codex/skills" ;;
      claude) printf '%s\n' "${project_dir}/.claude/skills" ;;
    esac
  fi
}

install_for_platform() {
  local platform="$1"
  local root
  root="$(install_root "$platform")"

  if [[ "$dry_run" -eq 1 ]]; then
    echo "[dry-run] mkdir -p ${root}"
  else
    mkdir -p "$root"
  fi

  for skill in "${SKILLS[@]}"; do
    local src="${ROOT_DIR}/${skill}"
    local dst="${root}/${skill}"
    if [[ ! -f "${src}/SKILL.md" ]]; then
      echo "Missing skill source: ${src}/SKILL.md" >&2
      exit 1
    fi
    if [[ "$dry_run" -eq 1 ]]; then
      echo "[dry-run] install ${src} -> ${dst}"
    else
      rm -rf "$dst"
      cp -a "$src" "$dst"
      echo "Installed ${platform}: ${dst}"
    fi
  done
}

if [[ "$target" == "codex" || "$target" == "both" ]]; then
  install_for_platform codex
fi

if [[ "$target" == "claude" || "$target" == "both" ]]; then
  install_for_platform claude
fi
