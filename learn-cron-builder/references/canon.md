# Canon

A canon is a pinned subset of outside knowledge that governs decisions: specs,
datasheets, official guides, source code, documentation MCP answers, and
curated wikis. Learn builds it; every skill cites it.

## Layout

```text
canon/manifest.tsv          one row per entry
canon/excerpts/<id>.md      excerpt or synthesis, when the license allows
ref/raw/                    original snapshots, git-ignored
instruments.tsv             measurement tools, kept apart from knowledge
```

## Manifest Columns

| Column | Meaning |
|---|---|
| `id` | stable short id: `A2`, `SPEC-12§4.4`, `PTX-ISA§9.7` |
| `locator` | URL, repository path, or `mcp:<server>:<tool>?q=<query>` |
| `version` | document version, release tag, or commit |
| `retrieved` | retrieval date |
| `sha256` | hash of the snapshot or excerpt; detects drift |
| `mode` | `verbatim`, `extracted`, or `derived` |
| `level` | `V` primary source, `F` forum or community, `I` inference awaiting a gate |
| `license` | `excerpt-ok`, `pointer-only`, or the SPDX id |
| `governs` | item or decision ids this entry constrains |

## Building

1. Lock the scope: which decisions need outside facts.
2. Query domain MCP servers first, then official sources, then community.
3. Snapshot each answer; MCP output changes between calls.
4. Write one row per fact cluster; split rows that govern unrelated decisions.
5. Mark inferences `I` and add the gate that would confirm them.
6. Submit rows as `[_]`; the master accepts after checking locators and hashes.

## Using

- Cite by id in evidence rows and `DECIDE` lines: `canon: [A2]`.
- Read the entry a decision needs; never paste the whole canon into a prompt.
- An `I` entry blocks acceptance of dependent items until its gate passes.
- Measure the canon's value by ablation; drop entries that change no decision.

## Auditing

- Re-hash snapshots; a changed hash reopens the entry.
- Track upstream corrections and newer versions.
- Prune wrong or unused entries; record each removal in the manifest history.
- Enforce licenses with a generated check, not a note.
