---
name: impact
description: >
  Shows the blast radius of the current diff or a named symbol: callers, dependents,
  affected flows and the tests that cover them, from code-review-graph. Use when the
  user says "what does this touch?", "blast radius?", "is this safe to change?",
  "what will my change break?", "who calls X?", or before editing a widely used symbol.
author: Varun Singh
phase: helper
lanes: [express, standard, full, hotfix]
reads: [diff, code-review-graph, dev-graph]
writes: [impact.md]
auto-trigger: true
preflight: graphs
---

## Step 0: preflight

1. Run `lfg graphs ensure`. If it exits non-zero, stop and show its output (only `--allow-stale` from the user overrides).
2. Run `lfg run path`. If there is a current run, the report goes there; otherwise answer in chat only.

## Steps

1. **Pick the target.**
   - A symbol was named → that node (find it with `semantic_search_nodes_tool` if the name is ambiguous; ask if still ambiguous).
   - Nothing named → the working-tree diff: `detect_changes_tool` (changed nodes + risk score).
2. **Start small:** `get_minimal_context_tool` on the target.
3. **Radius:** `get_impact_radius_tool` → direct callers, transitive dependents, node count, communities crossed.
4. **Flows:** `get_affected_flows_tool` → the execution paths that pass through the target.
5. **Tests:** `query_graph_tool` with `tests_for` on every changed or targeted node. List nodes with **no** test.
6. **Governance:** in dev-graph, look up `Invariant`, `Principle` and open `Gap` nodes on the touched `Component`s.
7. **Lane hint:** run `lfg lane --json` and quote its lane and reasons. Do not pick a lane yourself.

## Output

```
Target: <diff | symbol>      Risk: <score>      Lane hint: <lane> (<reasons>)
Callers (direct):    file:symbol …
Dependents (n=…):    grouped by community
Affected flows:      <flow name> → entry point
Tests to run:        test ids / files
Untested nodes:      file:symbol … (flag)
Invariants/Principles hit: …
```

If a run is active, also write this to `<run>/impact.md`. Keep it under 60 lines; summarise long lists with counts.

## Rules

- Graph tools only; open a file only to confirm a single ambiguous edge.
- Report what the graph says. If the graph has no data for a node, say so; never guess a caller list.
- Read-only on code. No edits.
