---
name: handoff
description: >
  Writes a compact handoff note into the run folder (state, next step, which skills
  to use) and updates progress.md, so a fresh session can continue cold. Use when
  the user says "wrap up", "hand this to the next session", "I'm stopping for
  today", "save where we are", or when the context window is nearly full.
author: Varun Singh
phase: helper
lanes: [express, standard, full, hotfix]
reads: [progress.md, tasks.json, 0*-*.md, git status]
writes: [HANDOFF.md, progress.md]
auto-trigger: true
preflight: graphs
adapted-from: mattpocock/skills/handoff (MIT, © 2026 Matt Pocock)
---

## Step 0: preflight

1. Run `lfg graphs ensure`. If it exits non-zero, stop and show its output (only `--allow-stale` overrides; suggest it here, since a handoff only reads the run folder).
2. `lfg run path`. If it exits 1, run `lfg run new handoff-<slug>`. Call the path `<run>`.

## Steps

1. **Gather state** (read-only): `ls <run>`, `tasks.json` (which `passes` are true), `git status --short`, `git diff --stat`, `lfg graphs status`, and `ready.json` if present.
2. **If the user gave an argument**, treat it as what the next session will focus on and tailor the note to it.
3. **Write `<run>/HANDOFF.md`** (≤ 40 lines). Reference artifacts by path; never restate what a spec, ADR, ticket or diff already holds.
4. **Update `<run>/progress.md`**: goal (unchanged), current status, "Next up" (the single next step), and a dated one-line log entry. Create it if missing.
5. Tell the user the path and the exact first command for the next session.

## Output

`<run>/HANDOFF.md`:
```
# Handoff — <run-id> — <date>
Goal: <one line>          Lane: <lane>        Graphs: <fresh|stale>
## State
- Done: <task ids / files>         - In progress: <task id, where it stopped>
- Uncommitted changes: <n files> (left unstaged for the human)
- Gates: <from ready.json, or "not run">
## Next step
<one concrete action>
## Skills to use next
/which → /build <task> → /check …   (with why, one line each)
## Open questions / blockers
## Pointers
01-brief.md · 02-design.md · tasks.json · <other run files>
```

## Rules

- Redact: no keys, tokens, passwords, connection strings or personal data. Use `<REDACTED>`.
- Never commit to "save" state. Run folder + `progress.md` + `tasks.json` are the memory; the human commits.
- Don't flip any `passes` flag here; only verified work does that.
