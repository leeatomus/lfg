# LFG review and plan: safe install, UI control, open-source readiness

> **Status (v0.2.0, 2026-10-14): phases 0–3 done, most of 4 and 5 done.** Implemented: per-repo enable (`defaultEnabled:
> false` + `--scope local`, checked against the real Claude Code 2.1.299 CLI), the change ledger and single writer
> (`claudecfg.py`), `lfg setup` (scan, plan, apply) with rollback, `lfg uninstall`, migration from 0.1.0, feature packs,
> plugin `.mcp.json` with stubs, `${CLAUDE_PLUGIN_ROOT}` hooks with narrow matchers and fast exit, Headroom opt-in and
> scoped, the dashboard's Settings → Claude Code tab and Skills page, namespaced skill docs, CI, and the community
> files. Still open: Linux support, a Homebrew tap, screenshots in the README, sidecar skill metadata, and getting the
> off-repo hook under 20 ms (it is about 64 ms now, mostly Python start-up and imports). The review below is
> kept as written.

Reviewed 2026-10-14 against the source in this folder (v0.1.0). Tests (73) pass and `ruff` is clean.
`shellcheck` wasn't installed on the review machine, so `bootstrap.sh` wasn't linted.

## 1. Summary

The engineering is good. The guard is a real shell parser with a self-test that fails closed. The dashboard
checks the edit key, Origin and Host. Saves are backed up, nothing is sent as telemetry, and the CLI uses only
the Python standard library. The problem is **scope**. Today LFG changes Claude Code **for every session in
every repo on the machine**, and some of those changes go into files the user owns:

| What bootstrap changes | Where | Effect on someone's existing setup |
|---|---|---|
| 33 `permissions.deny` rules, incl. `Bash(git commit:*)`, `Bash(git push:*)`, `Bash(gh pr create:*)` | `~/.claude/settings.json` (global) | Claude can no longer commit or open PRs **anywhere**, including inside other tools. Example from this machine: gstack's `/ship` and `/land-and-deploy` would stop working. |
| `env.ANTHROPIC_BASE_URL` → Headroom on 127.0.0.1:8787 | `~/.claude/settings.json` (global) | **All** Claude Code traffic goes through a third-party PyPI proxy that rewrites the conversation (`token` mode). If the launchd agent dies mid-session, Claude Code stops working. This also breaks Bedrock and Vertex setups. |
| PreToolUse and PostToolUse hooks with matcher `*` | plugin, enabled globally | About 210 ms of Python startup is added to **every** tool call in every repo (measured: about 105 ms pre plus 105 ms post). The guard blocks `git commit` even when the user asks for it. |
| SessionStart graph build | every git repo opened | Writes `.code-review-graph/` and `graphify-out/` into **every** repo the user opens and uses CPU in the background. Also runs `gh auth status`, which needs the network, in every session. |
| LFG block | `~/.claude/CLAUDE.md` | The global instructions file is edited. |
| `core.excludesFile` + 8 ignore lines | global git config | Changes global git config when it isn't already set. |
| 5 user-scope MCP servers (code-review-graph, linear, headroom, dev-graph, second-brain) | `~/.claude.json` | They show up in every session and use context. A `code-review-graph` server the user already registered is silently reused. |
| 3 launchd agents | `~/Library/LaunchAgents` | They run at login permanently. |
| About 13 brew formulas, plus Docker Desktop, LuLu (a system-extension firewall), Ollama and Strix (`curl \| bash`) | system | About 10 GB is installed up front, mostly for `/pentest`, which many users will never run. |
| Skills named `ship`, `health`, `learn`, `plan`, `build`, `fix`, `check`… | plugin | Name collisions, checked on this machine: `ship`, `health` and `learn` already exist in `~/.claude/skills` (gstack). Personal skills win the bare name, so typing `/ship` runs gstack's, and the docs tell users to type `/ship`. Broad auto-trigger descriptions ("how does X work?", "it's broken") take over ordinary requests in repos that don't use LFG. |

The uninstall steps in `docs/sharing.md` undo less than half of this. They leave the deny rules, the CLAUDE.md
block, the gitignore lines, `core.excludesFile` and three of the MCP servers in place.

**Guiding principle for the fix: LFG is a guest on the user's machine.** It should do nothing outside
`~/.lfg` unless the user opts in, and it should work only in repos where it was turned on. Every change it
makes outside `~/.lfg` should be recorded so it can be undone exactly.

## 2. Target install flow

### 2.1 One command, three steps: scan, show the plan, apply

```
lfg setup            # or: ./install.sh, which only copies files and then runs `lfg setup`
```

1. **Scan (read-only).** Check the Claude Code version and plugin support. Read settings at every scope: managed,
   user, project, local, plus `~/.claude.json` MCP servers. Also check existing hooks and plugins, all skills
   (to find name collisions), `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK` and `CLAUDE_CODE_USE_VERTEX`,
   ports in use (7777, 8787, 47181, 47182), installed tools and free disk space.
2. **Plan.** Print or render the exact changes in three groups, each with a diff:
   - **LFG's own files** in `~/.lfg`. Always applied.
   - **Claude Code**: register the plugin, enable it in the chosen repos, and any optional features the user picks.
   - **System**: brew packages and launchd agents. Only for the packs the user picks.

   Conflicts are listed before anything changes. Examples: "`ANTHROPIC_BASE_URL` is already your company gateway;
   Headroom would chain to it", "Bedrock detected: Headroom unavailable", "skill `ship` already exists (gstack);
   LFG's will be `/lfg:ship`".
3. **Apply as a transaction.** Before each step, back up the target and write a ledger entry. If any step
   fails, roll back the steps already applied. Finish with `lfg doctor` and a "What changed" summary that
   includes the uninstall command.

`lfg setup` with no TTY, or `lfg setup --ui`, opens the same plan as a first-run page in the dashboard with
checkboxes. Both paths run the same backend.

### 2.2 Feature packs, all optional except Core

| Pack | Installs | Enables |
|---|---|---|
| **Core** (default) | `uv`, `code-review-graph`, `graphify` | The plugin, the guard in enabled repos, graphs, runs, dashboard, `/lfg:*` skills |
| **Security** | `gitleaks`, `semgrep`, `osv-scanner`, `trivy`, `hadolint`, `actionlint`, `zizmor` | `/secure`, the full gate |
| **Ship check** | Docker (or Colima, if the user picks it) | `lfg shipcheck` |
| **Pentest** | Ollama + model, Strix, LuLu | `/pentest` |
| **Knowledge** | Omnigraph + 2 launchd agents | dev-graph, second-brain |
| **Linear** | Linear MCP | `/inbox`, issue reads |
| **Headroom** (off by default, marked experimental) | `headroom-ai` + launchd agent | Proxy routing, **scoped to LFG repos by default** |

Install packs lazily. When a skill needs a missing tool, it should say "`/secure` needs the Security pack: run
`lfg add security` or turn it on in Settings", not fail with a raw error.

### 2.3 Scope LFG to the repos that opt in

- `lfg enable` (or a dashboard toggle) turns LFG on for the current repo. It writes
  `enabledPlugins: {"lfg@lfg": true}` to that repo's `.claude/settings.local.json`, which is the file Claude Code
  designed for this. Claude Code already keeps that file out of git. The plugin is installed at user scope but
  **left disabled**, so other repos see no LFG skills, hooks or MCP servers.
- Ignore entries go in that repo's `.git/info/exclude`, not in global git config.
- `lfg enable --everywhere` is the explicit opt-in for users who want the current behaviour.
- **Fallback** if a repo can't use `settings.local.json` (for example, the team commits it): the hooks check a
  marker file `~/.lfg/repos/<rid>/enabled` first and `exit 0` within a few milliseconds when it's missing. Do
  this check before importing anything heavy.

### 2.4 Replace the global changes with scoped ones

| Today | Replace with |
|---|---|
| Global `permissions.deny` | Drop them. The guard hook already enforces every rule and fails closed. Offer **Hardened mode** for users who want deny rules as a second layer. It writes them to the enabled repos' `settings.local.json`, never to user scope. |
| `env.ANTHROPIC_BASE_URL` in user settings | Off by default. When turned on, the default is per repo (`env` in that repo's `settings.local.json`), with "everywhere" as an explicit choice. Refuse when Bedrock or Vertex is in use. |
| LFG block in `~/.claude/CLAUDE.md` | Inject the same text from the SessionStart hook (`additionalContext`) in enabled repos. On upgrade, remove the old block only if it is byte-identical to a block LFG shipped (`SHIPPED_SECTIONS` already supports this check). |
| User-scope MCP servers | Ship them in the plugin's `.mcp.json` so they exist only where the plugin is enabled. Tool names become plugin-namespaced, so update the `tools:` lists in `plugin/agents/*.md`. If the user already has a server with the same name, reuse it and record that in the ledger. Don't register a duplicate. |
| `$HOME/.lfg/bin/lfg` hard-coded in `hooks.json` | `${CLAUDE_PLUGIN_ROOT}`. Move `bin/` and `lib/` inside `plugin/` so that installing the plugin is the whole install. `lfg setup` only adds the `~/.local/bin/lfg` shim. |
| Writing into `~/.claude/plugins/cache/...` when a skill is edited (`settings.py` `_install_skill`) | Rebuild `~/.lfg/plugin` from defaults + overrides, bump a local version (`0.2.0+local.N`), then run `claude plugin marketplace update lfg && claude plugin update lfg@lfg`. The cache belongs to Claude Code and is wiped on update. |

### 2.5 Change ledger, uninstall and drift

`~/.lfg/state/ledger.json` gets one entry per change outside `~/.lfg`:
`{id, ts, kind: json-key|file-block|mcp|launchd|brew|symlink, target, key, before, after, backup}`.

- **Writes use compare-and-swap.** Re-read the file and check its hash immediately before writing. If it changed
  since the scan, re-plan. This matters because Claude Code itself rewrites `settings.json` and `~/.claude.json`.
- **`lfg uninstall [--dry-run] [--keep-data]`** replays the ledger in reverse. A key is restored only if its
  current value still equals what LFG wrote. If the user changed it since, leave it and report it. Brew
  packages are listed but never removed automatically, because other tools may use them.
- **`lfg doctor`** reports drift. Example: "`ANTHROPIC_BASE_URL` points at Headroom but the agent is unloaded:
  your Claude Code is offline. Fix: `lfg headroom off`."
- **One writer.** All writes to Claude Code files go through a single module (`lib/lfgcore/claudecfg.py`):
  backup, compare-and-swap, ledger, `0600`. `headroom.py`, `settings.py`, `omnigraph.py` and the bootstrap's
  inline Python all write `settings.json` separately today.

## 3. Dashboard: one control center

### 3.1 Settings → Claude Code (new tab)

Show only what matters to LFG. For each item, show the **effective value and the scope it comes from**. Lock
anything set by managed (enterprise) settings and say so.

- **Where LFG is on**: the list of enabled repos with toggles, plus the "everywhere" switch.
- **Guard**: on in LFG repos (default) or everywhere. Show the 18 rules with how each is enforced (this exists
  today), plus a "blocked recently" list from `audit.log`.
- **Hardened permissions**: on or off, with the exact rules LFG would add and where they would go.
- **Headroom**: off, LFG repos, or everywhere. Show the upstream, live status and savings. The Bedrock/Vertex
  refusal is explained in place.
- **MCP servers**: the servers LFG uses, whether each is connected, whether it's LFG's or the user's own, and
  sign-in status for Linear.
- **Hooks**: LFG's hooks, plus any other hooks the user has (read-only), so conflicts are visible. This machine
  already has a user `Stop` hook.
- **Agent models**: exists today; move it here.
- **Background services**: the launchd agents, with start, stop and logs.
- **Changes LFG made**: the ledger as a readable list. Each row has **Undo**, plus **Uninstall LFG** with a
  preview.
- **Your instructions** (`~/.claude/CLAUDE.md`): read-only by default. "Edit" needs the unlock key, which is how
  it works today.

### 3.2 Skills (new top-level page, not a Settings sub-tab)

List **every** skill Claude Code will load, not only LFG's. That includes personal (`~/.claude/skills`),
project (`.claude/skills`), each enabled plugin's skills, and legacy `commands/`. For each skill, show:

- **Source** badge and how to invoke it (`/ship` vs `/lfg:ship`).
- **Collisions** flagged: same bare name in two sources, with which one wins.
- **Auto-invoke** on or off. This edits `disable-model-invocation`: in an override for plugin skills, and in the
  file (with a backup) for personal skills.
- **Context cost**: description length, plus a total against Claude Code's skill-listing budget. This machine
  has 225 personal skills, so the budget matters.
- **View, edit and reset** for LFG skills (exists today) and personal skills. **Disable** without deleting: use
  a settings-based mechanism if the installed Claude Code version supports one (check the current docs for
  `Skill(...)` permission rules), or move the folder to `~/.lfg/disabled-skills/` and record it in the ledger.
- **Filters**: source, auto-invoke, collisions, recently used. The last one comes from transcripts, which
  `hooks.stop` already parses.

### 3.3 First-run and everyday UX

- **First-run page**: scan results, feature-pack checkboxes, conflict explanations, Apply. Then a checklist:
  `gh auth login`, Linear sign-in, enable your first repo, try `/lfg:which`.
- **Home** gets a "Health" strip with the doctor results, so nobody has to remember to run `lfg doctor`.
- **Every error message names a fix** that can be clicked or copied.

## 4. Skills and agents (Anthropic conventions)

- **Naming**: plugin skills are invoked as `/lfg:<name>`. Document that form everywhere (README, guide,
  `/which` output, wizard tables). Or rename the generic ones so the bare name is unique (`/lfg-ship`).
  Either way, stop telling users to type `/ship`, `/health` or `/learn`.
- **Auto-invocation**: keep the model-invoked set small (`which`, `explain`, `impact`, `secure`, `note`) and make
  the rest explicit only. Narrow the trigger phrases so ordinary requests ("how does X work?", "it's broken")
  aren't taken over. This matters less once the plugin is per-repo, but still applies there.
- **Frontmatter**: keys Claude Code doesn't know (`author`, `phase`, `lanes`, `reads`, `writes`, `auto-trigger`,
  `preflight`) are ignored and only cost bytes. Move them to a sidecar `skills.json` that the dashboard reads.
  Add the keys Claude Code does use: `argument-hint`, and `allowed-tools` where it removes permission prompts
  (for example, `Bash(lfg *)`).
- **Step 0 of every skill** runs `lfg graphs ensure`, which can take minutes on a first build. Make it
  non-blocking for read-only skills (`/which`, `/explain`, `/note`): use a stale graph and say so.
- **Don't spend tokens on attribution in context.** "LFG 0.1.0 (by Varun Singh) is active" is injected into every
  session, and "Author of LFG: Varun Singh." is in every agent prompt. Keep credit in `LICENSE`, `plugin.json`,
  the README and the dashboard footer.
- **Dangling references**: 16 files cite `PIPELINE.md`, `SKILLS.md` or `ARCHITECTURE.md` (for example "SKILLS
  §6" in `/wizard` and "PIPELINE §14.2" in the guard), and none of those files are in this folder. Either ship
  them or inline the few lines each citation needs.

## 5. Performance

- **Hook matchers**: `PreToolUse` → `Bash|Read|Edit|Write|MultiEdit|NotebookEdit|WebFetch|mcp__.*`. `PostToolUse` →
  the same set. Skip `Glob`, `Grep`, `TodoWrite` and `Task*`. Add the fast "repo not enabled" exit (2.3).
- **`Stop` hook**: it re-reads the whole transcript after every turn, so cost grows with the square of the
  session length. Store the byte offset per session and read only what was appended.
- **SessionStart**: cache `gh auth status` for an hour. Use `matcher: startup|resume` so it doesn't re-run after
  `/clear` and compaction.
- **Graph waits**: the pre-tool hook can block a code-review-graph MCP call for up to 240 s while a sync runs.
  Return quickly with "syncing, retry shortly" or serve the stale graph with a warning.

## 6. Open-source readiness

- This folder is **not a git repo** yet. Run `git init`, push to GitHub, and add CI (GitHub Actions on macOS:
  unit tests, `ruff`, `shellcheck`, `lfg doctor --selftest`, plus a dry-run install test in a temp `HOME` that
  asserts **no file outside `$LFG_HOME` changes** in Core mode).
- One source of truth for the version: currently `common.py`, `plugin.json` and `marketplace.json`. Add a
  `CHANGELOG.md` and tagged releases.
- Add `CONTRIBUTING.md`, `SECURITY.md` (how to report a guard bypass), issue and PR templates, and screenshots or
  a GIF of the dashboard in the README.
- Distribution: make the GitHub repo itself a marketplace, so that
  `claude plugin marketplace add <you>/lfg && claude plugin install lfg@lfg` works, followed by `lfg setup`.
  Optionally add a Homebrew tap (`brew install <you>/tap/lfg`) for the CLI shim.
- `CONTRACT.md` line 64 is a single cell of about 2,500 characters. Move the dashboard description to
  `docs/dashboard.md`.
- `.claude/launch.json` points at an old path (`/Users/varun/Documents/eng-pipeline/lfg`).
- Say "macOS only" near the top of the README. Plan Linux later: systemd user units instead of launchd, apt or
  brew-on-Linux for packages.

## 7. Order of work

| Phase | Scope | Done when |
|---|---|---|
| **0. Hygiene** (about 1 day) | git init and CI, fix dangling refs, remove attribution from context, version source, launch.json | CI is green on a clean macOS runner |
| **1. Do no harm** (main item) | `claudecfg.py` single writer and ledger; `lfg setup` scan, plan and apply; per-repo enable; plugin `.mcp.json`; `${CLAUDE_PLUGIN_ROOT}`; Headroom and deny rules opt-in and scoped; CLAUDE.md block becomes SessionStart context; `lfg uninstall` | Temp-`HOME` test: Core install changes nothing outside `~/.lfg` except the plugin registration and the shim. Install followed by uninstall leaves `~/.claude` byte-identical. |
| **2. Packs and lazy installs** | `lfg add <pack>`, skills point to the missing pack | A fresh Mac with Core only can run `/lfg:which`, `/lfg:explain`, `/lfg:plan`, `/lfg:build` |
| **3. Control center** | Claude Code settings tab, Skills page, first-run page, ledger with undo | Every opt-in in phase 1 can be toggled from the UI, with the same result as the CLI |
| **4. Skills polish and performance** | Naming, auto-invoke set, sidecar metadata, hook matchers, incremental Stop, cached gh | Hook overhead under 20 ms in repos without LFG; no bare-name collisions |
| **5. Distribution** | GitHub marketplace, release tags, README with screenshots, optional brew tap | A stranger installs it in one command and can uninstall it cleanly |

Phase 1 is the one that protects users' machines, and later phases build on its ledger and single writer, so do
it first.
