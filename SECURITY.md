# Security policy

LFG runs inside your development environment and its guard is a safety boundary, so we treat these as security issues:

- a way for an agent to get past the guard: commit, push or write to GitHub, read a secret file, dump the environment, deploy, write outside the repo, or anything else in the 18 standing rules (`lfg ui` → Settings → Rules)
- a way for a web page or another local process to change settings through the dashboard (`lfg ui`) without the edit key
- LFG changing something outside `~/.lfg` without recording it, or `lfg uninstall` / undo restoring the wrong value
- a secret ending up in a file LFG writes (runs, graphs, logs, backups)

## Reporting

Please report privately through GitHub's **Report a vulnerability** button on the repository's Security tab (https://github.com/varun-singhh/lfg/security/advisories/new). Don't open a public issue. Include the LFG version (`lfg version`), the exact command or tool call, and what happened. We aim to reply within a week.

## Supported versions

Only the latest release gets fixes.

## Scope notes

The guard is a strong safeguard, not a sandbox. It parses shell commands, including wrappers, subshells, `sh -c` and `eval`, but it can't see inside arbitrary programs a command runs. Run untrusted code in a container: the ship check and pentest already do.
