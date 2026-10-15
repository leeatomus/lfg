# The LFG dashboard (`lfg ui`)

A local web page at http://127.0.0.1:7777 that shows what LFG is doing in your repos and lets you control it. It loads nothing from outside your computer. The pages live in `plugin/lib/lfgcore/ui_assets/` and use plain-language labels. Navigation is a side menu, and old view hashes (`#overview`, `#reviews`, `#brain`, …) redirect.

## Pages

| Page | What it shows |
|---|---|
| Home | The current run, the next step, and what needs you |
| Runs | Every run, with a one-paragraph description from its brief (or review summary). Run files (review, security, pentest, tasks, checks, ship check) are shown as readable text, never raw JSON, and failed checks show their output |
| Issues | The dev-graph mirror of Linear |
| Checks | Review, security, ship check, and actions the guard stopped |
| Code | Graph views and architecture health. The code map can be built, updated, rebuilt or its docs refreshed here (see *Code map* below) |
| Docs | Start here (playbooks), From your docs, Parts of the code (areas of 10+ symbols, named by folder) and Decisions, 12 per group with Show all |
| Knowledge | dev-graph and second-brain |
| Usage | Dollars spent today, over 7 and over 30 days, and by model, as `tokensave cost` works them out from Claude Code's session logs at API prices. Shown only when tokensave is installed and its upload counter is off. Also Headroom's own estimate of what compression saved. Both tools run in the background, one process at a time |
| Skills | Every skill Claude Code loads on this computer: personal, personal commands, the selected project's and every installed plugin's (LFG's included). For each skill: how to type it, where it comes from, name clashes (the short name goes to your own skill first, so plugin skills need their full `/plugin:name`), how much context its description costs, and a switch for whether Claude may use it on its own (`disable-model-invocation`; your personal skills are edited in place with a backup, LFG's are saved as overrides). The **Edit LFG skills** tab is the Markdown editor for LFG's skills |
| Settings → Claude Code | Where LFG is on (per repo, or every repo); feature packs, which you can add (installed in the background with a live log; never runs a `curl \| bash` installer) or turn off; the guard and hardened mode; Headroom scope (off / LFG repos / everywhere); the MCP servers LFG brings and whether each is ready; your own Claude Code setup (read-only: version, organisation policy, API endpoint host, hooks, MCP servers, skill name clashes); leftovers from older LFG versions with a Fix for each; and every change LFG made outside `~/.lfg`, with Undo |
| Settings → General | Fields of `~/.lfg/config.json` |
| Settings → Connections | Tools and integrations, with the pack each one belongs to and how to get it |
| Settings → Local AI models | Ollama models for `/lfg:pentest`: installed models, a catalog with how well each fits this computer's memory, and downloads from 127.0.0.1 only (never cloud models) |
| Settings → Disk space | `~/.lfg` disk use against `storage.limit_mb` (default 500; graphs inside repos are shown separately and not counted). Deletable items: runs on branches that were merged or deleted, everything for repos whose folder is gone, graphs not synced for `storage.idle_graph_days` (default 30), generated graph visualisations. The current run and the checked-out and default branches are never offered |
| Settings → Rules | The 18 standing rules (read-only, enforced in code) and the rule modules, which you can change in Markdown or add to (saved in `~/.lfg/overrides/rules/`; undo and delete keep a backup). Any mention of a rule anywhere in the dashboard shows what it means on hover |
| Settings → Your instructions | `~/.claude/CLAUDE.md`, formatted, with an editor. LFG never writes to it otherwise |
| Help | The guide, every skill and agent, the CLI reference and the sharing guide |

The project picker shows each repo's folder name. The branch picker marks the checked-out branch and filters Home, Runs and Checks by the branch each run recorded (`run.json` `branch`). Graphs stay one per repo and follow the checked-out branch.

## Editing and safety

- **Read-only unless unlocked.** `lfg ui` opens the browser with the local edit key in the URL fragment. The key is a 0600 file in `~/.lfg/ui/`, never printed, and the guard keeps agents away from it. `lfg ui --unlock` re-opens a running dashboard unlocked.
- **What every write needs:** the key, the same Origin, the `X-LFG: 1` header and a JSON body. Writes are validated, refused if they look like a secret, backed up to `~/.lfg/backups/`, and audited.
- **Changes to Claude Code go through the change ledger,** exactly like the same change made with the CLI, so `lfg uninstall` can undo them. This covers turning a repo on or off, hardened mode, Headroom scope and packs.
- **Skill edits** live in `~/.lfg/overrides/skills/` and are written to the installed plugin, which Claude Code loads in place. Updates keep them, and pristine copies are in `~/.lfg/defaults/skills/`.
- **Deletes** (Disk space) stay inside `~/.lfg` or a known repo's graph folders.
- **Reading the API** needs the `X-LFG: 1` header, and the Host must be 127.0.0.1 or localhost (guards against DNS rebinding).

## Code map

The code map can be built, updated or rebuilt from scratch, and its docs refreshed, from the side menu, Home and Code. This uses `POST /api/save/graphs_build`, the same background job the hooks start. It needs no edit key, but it does need the same Origin, Host and header checks.
