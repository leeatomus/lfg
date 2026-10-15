---
name: health
description: >
  Scans the codebase for deepening opportunities (shallow modules, leaky seams,
  hard-to-test areas) using the graphs, and renders a self-contained HTML report for
  the "Arch health" viewer in lfg ui. Use when the user says "where is the
  architecture rotting?", "architecture health", "what should we refactor?",
  "find shallow modules", or on the Friday health routine.
author: Varun Singh
phase: helper
lanes: [standard, full]
reads: [code-review-graph, graphify, dev-graph, GLOSSARY.md, docs/adr, git log]
writes: [~/.lfg/ui/static/arch-health/<repo-id>.html, health.md]
auto-trigger: true
preflight: graphs
adapted-from: mattpocock/skills/improve-codebase-architecture (MIT, © 2026 Matt Pocock)
---

## Step 0: preflight

1. Run `lfg graphs ensure`. If it exits non-zero, stop and show its output (only `--allow-stale` overrides).
2. `lfg run path`. If it exits 1, run `lfg run new health-<yyyymmdd>`. Call the path `<run>`.
3. `<repo-id>` = `basename "$(dirname "$(lfg repo docs)")"`. Load vocabulary: `lfg rule module-design` (module, interface, depth, seam, adapter, leverage, locality; the deletion test).

## Steps

1. **Scope first (YAGNI).** If the user named an area, use it. Otherwise find hot spots: `git log --oneline --name-only -n 200` (read-only) and weight recently churned files.
2. **Read the domain:** `GLOSSARY.md` and ADRs from `lfg repo docs`. ADRs are not re-litigated unless the friction is real; then mark the card.
3. **Scan with graphs**, not by browsing:
   - `get_hub_nodes_tool`, `get_bridge_nodes_tool`, `list_communities_tool`, `find_large_functions_tool`, `get_surprising_connections_tool`, `get_knowledge_gaps_tool`;
   - `graphify query "god nodes and HACK/WHY notes in <area>" --graph "$(lfg repo graph)"`;
   - `query_graph_tool tests_for` on candidates (untested = friction);
   - dev-graph open `Gap`s and `Learning`s on the same `Component`s.
4. **Judge** with a subagent if the area is large; else inline. Look for: concepts split across many tiny modules, interfaces nearly as big as their implementation, extracted pure functions whose bugs live in the call sites, seams that leak. Apply the deletion test: deleting it would *concentrate* complexity → candidate.
5. **Write the report** to `~/.lfg/ui/static/arch-health/<repo-id>.html`, one self-contained file: inline CSS and inline SVG only, **no CDN or external requests** (the viewer works offline). Header: repo, date, legend (box = module, dashed = seam, red arrow = leak, dark box = deep module). One card per candidate:
   - title naming the deepening; badge `Strong` / `Worth exploring` / `Speculative`; dependency tag (`in-process`, `local-substitutable`, `ports & adapters`, `mock`);
   - files (monospace), linked graphify community id;
   - before/after diagram side by side (the centrepiece; vary the style);
   - Problem (one sentence), Solution (one sentence), Wins (bullets ≤ 6 words), ADR callout if any.
   End with **Top recommendation** and why.
6. Write `<run>/health.md`: the candidate list (title, strength, files) and the report path. Tell the user to open `lfg ui` → Arch health, or the file directly.
7. Ask: "Which one do you want to explore?" Do not propose interfaces yet. On a pick, hand over to `/grill` (record rejected-with-reason candidates as ADRs only if the user agrees).

## Output

`~/.lfg/ui/static/arch-health/<repo-id>.html` and `<run>/health.md`.

## Rules

- Use glossary terms for the domain and module-design terms for architecture; not "service", "component", "boundary".
- Read-only on code. No refactors from this skill.
- No external scripts, fonts or images in the HTML.
- Overwrite only this repo's report file.
