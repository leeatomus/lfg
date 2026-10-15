# Changelog

All notable changes to LFG. The version lives in `plugin/.claude-plugin/plugin.json`.

## 0.2.0 (2026-10-14)

LFG no longer changes Claude Code for every session on the machine. It is now installed off, turned on per repo, and every change it makes outside `~/.lfg` is recorded and reversible.

### Added
- `lfg setup`: looks at the machine (read-only), prints a plan, and applies it only after a yes. A failed step rolls back that run's changes. `install.sh` is now a thin wrapper around it.
- `lfg enable` / `lfg disable`: turn LFG on or off for one repo, using Claude Code's per-repo plugin setting (`.claude/settings.local.json`). `--everywhere` is available but not the default.
- Change ledger (`~/.lfg/state/ledger.json`, `claudecfg.py`): every outside change is backed up, written with compare-and-swap, and undoable. Added `lfg changes [undo <id>]`.
- `lfg uninstall [--dry-run] [--keep-data]`: undoes everything, including what older versions did, and lists the tools and repo graph folders it leaves.
- Feature packs (`lfg packs`, `lfg add`, `lfg remove`): security, shipcheck, pentest, knowledge, linear, headroom. Core installs only uv, gh, code-review-graph and graphify.
- Dashboard **Skills** page: every skill from every source, with name clashes, context cost and an auto-invoke switch.
- Dashboard **Settings → Claude Code**: where LFG is on, packs (installed in the background), hardened mode, Headroom scope, MCP status, your setup (read-only), leftovers from older versions, and every change with Undo.
- Migration from older installs. `lfg setup`, the dashboard and `lfg uninstall` detect the old global deny rules, the `CLAUDE.md` block (only if unedited), the user-scope MCP servers, global Headroom routing and the plugin being on everywhere, and offer to remove exactly those.
- Hardened mode: Claude Code deny rules behind the guard, written per repo, never to user settings.
- `lfg mcp <name>`: the plugin's own MCP servers, with a no-tools stub when a pack isn't set up.
- Open-source project files: CI, contributing guide, security policy, code of conduct, issue templates.

### Changed
- `bin/` and `lib/` moved into `plugin/`, so the plugin is self-contained. Hooks call `${CLAUDE_PLUGIN_ROOT}/bin/lfg`.
- Plugin manifest: `defaultEnabled: false`, plus homepage and repository fields. MCP servers moved from user scope into `plugin/.mcp.json`, so agent tool names are now `mcp__plugin_lfg_<server>__*`.
- Hooks exit at once in repos where LFG is off, match only the tools they inspect, and start Python with `-S`. Measured with Anaconda Python, an off-repo hook dropped from about 196 ms to 64 ms. SessionStart caches `gh auth status` for an hour, and Stop reads only the new part of the transcript.
- Headroom is opt-in and scoped (`headroom.scope`: off / repos / everywhere), and refused on Bedrock, Vertex and Foundry.
- The guidance that used to be appended to `~/.claude/CLAUDE.md` is now session context, and only in LFG repos.
- Skill edits from the dashboard no longer write into Claude Code's plugin cache, because the local marketplace loads the plugin in place.
- The guard blocks agents from running `lfg setup|enable|disable|uninstall|add|remove|changes undo|headroom setup|off` and from editing `~/.lfg/state` or `enabled.json`.
- Skills are documented as `/lfg:<name>`, and `/lfg:which` recommends namespaced names.
- Ignore entries go in each repo's `.git/info/exclude` instead of the global gitignore.

### Removed
- Global `permissions.deny` rules, the global `CLAUDE.md` block, user-scope MCP registration, global gitignore and `core.excludesFile` changes, and routing all Claude Code traffic through Headroom by default.
- References to design documents that weren't in the repository.

## 0.1.0

First version.
