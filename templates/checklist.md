# <Name> Blueprint

> Single authority for this run. States: `[ ]` open, `[_]` submitted, `[x]` accepted.
> Workers submit; the master accepts after re-running each item's oracle.

## Goal

<One paragraph: what done means, measured how.>

## Canon

| id | locator | version | level | governs |
|---|---|---|---|---|
| A1 | <url, path, or mcp:server:tool> | <version> | V | ITEM-001 |

## Checklist

- [ ] [ITEM-000] Build the oracle for this blueprint
  - owned_paths: verify/
  - oracle: review:master-reads-gates
- [ ] [ITEM-001] <title>
  - depends_on: [ITEM-000]
  - owned_paths: src/<area>/, verify/gates/ITEM-001.sh
  - oracle: verify/gates/ITEM-001.sh
  - tier: T0
  - budget: loc<5000
  - canon: [A1]

## Decisions

- DECIDE <param>=<value> because <reason>; else <fallback>
