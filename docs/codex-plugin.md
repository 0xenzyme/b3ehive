# Codex Plugin Publishing

b3ehive is packaged as a Codex plugin in `plugins/b3ehive` and exposed through
the repository marketplace catalog at `.agents/plugins/marketplace.json`.

## Install From This Repository

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

## Install From GitHub

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

Start a new Codex thread after installation so Codex can load the plugin skills.

## Package Layout

```text
.agents/plugins/marketplace.json
plugins/b3ehive/
  .codex-plugin/plugin.json
  skills/
    compete-cron-builder/
    execution-cron-builder/
    learn-cron-builder/
    optimization-cron-builder/
    looper-cron-builder/
  assets/
```

The source-of-truth skill directories still live at the repository root for
portable Codex, Claude Code, opencode, OpenClaw, and Hermes installs. Before a
plugin release, sync those root skill directories into the Codex plugin package:

```bash
scripts/sync_codex_plugin.sh
```

## Current Public Directory Status

This repository marketplace is a public Git-backed distribution path. It is not
an OpenAI official Plugin Directory listing. OpenAI's self-serve public Plugin
Directory publishing flow should be used when that program is available.

## Release Checklist

- Run `scripts/sync_codex_plugin.sh`.
- Validate `plugins/b3ehive/.codex-plugin/plugin.json`.
- Verify `.agents/plugins/marketplace.json` points to `./plugins/b3ehive`.
- Keep `PRIVACY.md`, `TERMS.md`, `LICENSE`, and README install instructions
  current.
- Tag the repository release after plugin metadata and root package metadata
  agree on version.
