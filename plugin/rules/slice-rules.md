Rule module: slice-rules · LFG · author Varun Singh · adapted from mattpocock/skills/to-tickets (MIT, © 2026 Matt Pocock)

# Slice rules: tracer-bullet tickets

Used by `/plan` (and `/map`) to turn a design into `tasks.json` tickets.

## Vertical slices

- Each ticket cuts a **narrow but complete** path through every layer it needs (schema, API, UI, tests). Never one layer on its own.
- A finished ticket is demoable or verifiable by itself: its `verification` names the acceptance criterion and the seam that proves it.
- Each ticket fits one fresh context window: small `graph_scope`, a handful of files.
- **Prefactor first:** "make the change easy, then make the easy change". A prefactor is its own ticket that blocks the rest and changes no behaviour.

## Blocking edges

- `depends_on` lists only tickets that genuinely gate this one (it needs their code or their interface). No edge "just to be safe": every edge costs parallelism.
- Tickets with no edge between them share a `parallel_group` letter; `/build` runs a group's frontier together.
- Two tickets that edit the same symbol in `graph_scope` either get an edge or are merged, to avoid patch conflicts.
- No cycles. Order the list blockers first.

## Wide refactors: expand → migrate → contract

When one mechanical change (rename a column, retype a shared symbol) fans across the codebase so no vertical slice can stay green:

1. **Expand:** add the new form beside the old; nothing breaks.
2. **Migrate:** move call sites in batches sized by blast radius (`get_impact_radius_tool`, per package or directory), one ticket per batch, each blocked by the expand.
3. **Contract:** delete the old form, blocked by every migrate batch.
If batches can't stay green alone, keep the order and add a final integrate-and-verify ticket that all batches block; green is promised only there.

## Ticket text

- Title: short, in glossary terms. "What it delivers": end-to-end behaviour from the user's side, not a layer-by-layer list.
- Acceptance criteria as checkboxes, each mapping to a brief criterion number.
- No file paths or code snippets in Linear text (they go stale); `file:symbol` pointers belong in `graph_scope`.

## Review the breakdown with the user

Show: title · blocked by · what it delivers · seams. Ask: granularity (too coarse / too fine)? edges correct? merge or split any? Iterate until approved.
