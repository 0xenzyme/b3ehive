# Agent Platform Compatibility

b3ehive skills use the portable `SKILL.md` directory contract. The same skill
directories can be installed for Codex and Claude Code without maintaining two
copies of the skill body.

## Supported Targets

| Target | User install root | Project install root | Invocation |
|---|---|---|---|
| Codex | `~/.codex/skills/<skill>/SKILL.md` | `.codex/skills/<skill>/SKILL.md` | Mention the skill by name, for example `Use execution-cron-builder ...` |
| Claude Code | `~/.claude/skills/<skill>/SKILL.md` | `.claude/skills/<skill>/SKILL.md` | Invoke `/skill-name` or mention the skill by name |

The five portable skill directories are:

- `debating-cron-builder`
- `execution-cron-builder`
- `research-cron-builder`
- `optimization-cron-builder`
- `migration-cron-builder`

The repository root `SKILL.md` is the legacy PCTF debating specification. Keep it
for OpenClaw/package compatibility, but install the five skill directories for
Codex and Claude Code.

## Runner Contract

Cron-oriented skills should describe worker execution in terms of an agent
runner, then select a platform command at installation or repository bootstrap
time.

Default Codex runner:

```bash
codex exec --cd "{workspace}" --model "${CODEX_MODEL:-gpt-5.3-codex}" \
  -c model_reasoning_effort="${CODEX_REASONING_EFFORT:-xhigh}" \
  < "{prompt_file}" > "{output_file}"
```

Default Claude Code runner:

```bash
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "{workspace}" < "{prompt_file}" > "{output_file}"
```

Generated cron guards may expose these settings:

| Shared setting | Codex setting | Claude Code setting |
|---|---|---|
| `B3EHIVE_AGENT_PLATFORM=codex|claude` | `CODEX_MODEL` | `CLAUDE_MODEL` |
| `B3EHIVE_AGENT_RUNNER` | `CODEX_REASONING_EFFORT` | `CLAUDE_EFFORT` |
| `B3EHIVE_AGENT_WORKSPACE` | `CODEX_SERVICE_TIER` | `CLAUDE_PERMISSION_MODE` |

When a user explicitly sets `B3EHIVE_AGENT_RUNNER`, generated cron code should
use it as the authoritative command template and must print it in validate-only
output.

## Skill Authoring Rules

- Keep each skill as a directory containing `SKILL.md` plus optional
  `references/`, `scripts/`, `templates/`, and `agents/` files.
- Keep YAML frontmatter with at least `name` and `description`; both Codex and
  Claude Code can discover that shape.
- Keep platform-specific details in short compatibility sections, references,
  or generated config. Do not fork the main instructions unless the workflow
  truly differs.
- Use "agent runner" for generic orchestration text. Use `codex exec` or
  `claude -p` only when giving platform-specific command templates.
- For cleanup gates, check for a live process matching the selected runner,
  not only for a `codex` process.
