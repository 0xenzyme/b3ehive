# Project Checklist

## Checkbox State Protocol

Use this three-state, dual-cursor protocol for execution, research, and
migration checklists:

- `[ ]` = not done / not researched / not migrated. Work is still available
  for a worker claim.
- `[_]` = worker self-tested. A worker produced output and local validation
  evidence, but the master lane has not accepted and integrated it.
- `[x]` = master accepted. The master lane validated, integrated, reconciled,
  and accepted the item.

Workers may advance `[ ]` to `[_]` only. The master lane is the only actor that
may advance `[_]` to `[x]`. Cleanup requires zero `[ ]` and zero `[_]` items.
Generated todos, ledgers, indexes, progress tables, and status commands must
preserve these exact marks as the source of truth. Queue labels such as `live`,
`finished`, `curating`, or `failed` may add operational detail, but they do not
replace the checkbox state.

## ✅ Done List
_Recently completed items - celebrate progress!_

- [x] Initial project setup
- [x] Core architecture defined
- [x] Basic implementation complete

## 🧪 Worker Self-Tested
_Worker output exists; master validation/integration is still pending._

- [_] Worker-completed item waiting for master acceptance

---

## 🎯 To Do List
_Immediate next steps - do these now!_

### High Priority
- [ ] [Task 1 - most urgent]
- [ ] [Task 2 - blocking others]

### Medium Priority  
- [ ] [Task 3 - important for current sprint]
- [ ] [Task 4 - quick wins]

---

## 📅 Later List
_Mid-term goals - important but not urgent_

### Week 2-4
- [ ] [Feature enhancement 1]
- [ ] [Performance optimization]

### Month 2-3
- [ ] [Major feature addition]
- [ ] [Architecture refactoring]

---

## 🔬 Watch List
_Requires deep research before execution_

### Research Needed
- [ ] [Complex problem requiring investigation]
  - _Research questions: [what to learn]_
  - _Potential approaches: [options to explore]_
  
- [ ] [Technology evaluation]
  - _Options: [A vs B vs C]_
  - _Decision criteria: [how to choose]_

### Blocked / Waiting
- [ ] [Task waiting for external dependency]
  - _Blocked by: [what's needed]_
  - _Expected resolution: [when]_

- [ ] [Task needing stakeholder input]
  - _Questions to resolve: [what to ask]_

---

## 📊 Progress Summary

| List | Total | Done | Progress |
|------|-------|------|----------|
| Not Done `[ ]` | - | - | - |
| Worker Self-Tested `[_]` | - | - | - |
| Master Accepted `[x]` | - | - | - |
| Done | - | - | - |
| To Do | - | - | - |
| Later | - | - | - |
| Watch | - | - | - |

**Last Updated:** [Date]

---

## 🔄 Review Schedule

- **Daily:** Check To Do List
- **Weekly:** Review Later List, move items to To Do
- **Bi-weekly:** Deep dive Watch List, convert to actionable items
