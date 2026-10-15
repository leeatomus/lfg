## What and why

## Checklist
- [ ] `python3 -m unittest discover -s tests` passes
- [ ] `uvx ruff check plugin/lib plugin/bin/lfg tests` passes
- [ ] Writes outside `~/.lfg` go through `claudecfg.py` and are covered by an undo test (see CONTRIBUTING.md)
- [ ] New guard blocks / allowances have `guard.SELFTEST` cases
- [ ] `CHANGELOG.md` updated for user-visible changes (and the version in `plugin/.claude-plugin/plugin.json` if releasing)
