Rule module: agent-writing · LFG · author Varun Singh · adapted from mattpocock/skills/writing-for-agents (MIT)

# Writing for agents

Applies to anything an agent will read: skills, agent prompts, rule modules, playbooks, `CLAUDE.md`, `Principle` text, reviewer rules. The goal is a predictable *process* every run.

## Pointers (descriptions, "see X" lines)

A pointer names out-of-context material and the condition for reaching it. Its wording, not its target, decides when the agent reaches it.
- Front-load the leading word.
- One trigger per distinct branch; synonyms of one branch are one trigger.
- Skill descriptions: what it does, then `Use when the user says "…"` with the natural phrases people actually type, then auto-trigger conditions.
- Explicit-only skills (`disable-model-invocation: true`): one human-facing line.

## Information hierarchy

1. **Steps** in the file: what the agent does, in order.
2. **Reference** in the file: rules and facts consulted on demand.
3. **Disclosed reference**: a separate file or `lfg rule <name>`, reached by a pointer.

Inline what every branch needs; disclose what only some branches reach. Keep a concept's definition, rules and caveats under one heading. A file that sprawls is cut down the ladder, not trimmed word by word.

LFG limits: skills < 120 lines, rule modules < 80, body order `Step 0: preflight` → `Steps` → `Output` → `Rules` (CONTRACT.md).

## Completion criteria

Every step ends on a checkable, demanding condition: "`lfg gate` exits 0 in this run", "every acceptance criterion maps to a passing test", not "tests look good". Sharpen a fuzzy bound before splitting the sequence.

## Leading words

Use a word the model already knows to anchor a behaviour: *tight* loop, *red* test, *blast radius*, *tracer bullet*, *frontier*. Repeat the token, not the definition. Prefer an existing word over a coined one.

## Say the target

State the behaviour you want ("fix the code at its cause"). A prohibition alone makes the forbidden act more available; use one only as a hard guardrail, paired with the positive target. LFG's hard guardrails live in §14 and `git-guard`; point to them rather than restating.

## Pruning

- **Single source of truth:** one meaning, one place. Point to `CONTRACT.md`, a rule module or the CLI's `--help` instead of copying.
- **The environment is a source of truth:** don't cache what one command or file reveals (scripts, config, layout). Cache only what can't be looked up: reasons, gotchas, unwritten conventions.
- **No-ops:** delete any sentence that doesn't change behaviour versus the default. A word too weak to beat the default gets a stronger word.
- **Sediment:** remove stale lines when behaviour changes; every line must still bear on the task.

## Mechanical vs judgement

A rule a tool can check (banned API, import shape, file location) becomes a linter rule or CI job. Only judgement calls become prose: a `Principle`, a `CODING_STANDARDS.md` line, or a reviewer rule.
