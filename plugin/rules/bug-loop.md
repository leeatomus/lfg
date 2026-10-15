Rule module: bug-loop · LFG · author Varun Singh · adapted from mattpocock/skills/diagnosing-bugs (MIT, © 2026 Matt Pocock)

# Bug loop

The discipline behind `/fix`. Skip a phase only with a stated reason.

## Redact

Write `<REDACTED>` for every secret in commands, output and captured artifacts. Build loops on env vars by name. Quote only the lines that carry the signal. If redacted output isn't enough, say so and ask.

## 1. Feedback loop (the whole game)

Build one command that goes red on *this* bug. Try, roughly in order: failing test at a seam that reaches the bug · curl/HTTP script against the local dev server · CLI with a fixture, diffed against a known-good snapshot · headless browser script · replay of a captured request/event · minimal throwaway harness · property/fuzz loop · `git bisect run` harness (read-only bisect in a worktree; never on the user's branch) · differential old-vs-new run · human-in-the-loop script (last resort).

Tighten it: faster (narrow scope, cached setup), sharper (assert the exact symptom), deterministic (pin time, seed RNG, isolate FS and network). Flaky bugs: raise the reproduction rate (loop 100×, parallelise, stress) until it is debuggable.

**Done when** you have already run one command that is: red-capable on the user's exact symptom · deterministic · seconds not minutes · agent-runnable. Without it, do not hypothesise. If you can't build one, stop, list what you tried, and ask for environment access, a redacted artifact, or permission for temporary local instrumentation.

## 2. Reproduce + minimise

Confirm it is the user's failure, not a nearby one, and it reproduces across runs. Capture the exact symptom. Cut inputs, callers, config and steps one at a time, re-running after each, until every remaining element is load-bearing.

## 3. Hypothesise

Write 3–5 ranked hypotheses before testing any. Each is falsifiable: "If X is the cause, changing Y makes it pass / changing Z makes it worse." Can't state the prediction → discard it. Show the list; the user may re-rank instantly. Don't block if they're away.

## 4. Instrument

One probe per prediction; change one variable at a time. Prefer a debugger/REPL, then targeted logs at the boundaries that separate hypotheses. Never "log everything and grep". Tag every debug log `[DEBUG-<4hex>]`. Performance: baseline measurement first (timer, profiler, query plan), then bisect.

## 5. Fix + regression test

Only at a **correct seam**: one that exercises the real bug pattern as it occurs at the call site. Turn the minimised repro into a failing test there, watch it fail (if you forced red by mutating code or a fixture, diff against a pristine copy to prove it), apply the fix, watch it pass, re-run the original loop. No correct seam → that is a finding: record it and propose an `Issue`.

## 6. Cleanup (required)

- Original loop no longer reproduces.
- Regression test passes, or the missing seam is documented.
- No `[DEBUG-` tags left (grep).
- Throwaway harnesses deleted.
- The confirmed hypothesis is written into `03-fix-<slug>.md` and the dev-graph `Learning`, so `COMMIT_MSG.md` and the next debugger can use it.
