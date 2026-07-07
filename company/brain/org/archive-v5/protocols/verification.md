# ✔ Verification Protocol — outcome over self-report (SOFI v5)

> **Foundation:** Serves Teaching **VI (Reversibility)** — nothing advances that can't be shown correct — and Teaching **II (Hierarchical Flow)** — a gate is a checkpoint, not a rubber stamp. Read `grounding.md` (this is G3 made mechanical) and `engine/DOCTRINE.md` first.

The single highest-value agentic-QA lever in the 2025-2026 research: **never trust the acting agent's word that it succeeded — check the actual outcome.** An agent saying "tests pass / booking confirmed / migration applied" is exactly the *execution hallucination* that propagates into a shipped bug. SOFI already has the enforcement point (gate bars); v5 makes the discipline explicit and adds the missing adversarial layer.

## V1 — Outcome over self-report (mechanical, `sofi gate-check`)
A ticket marked `done` / `passing` must carry an **evidence block**: the command that was run + its output/exit code, OR a `file:line` proof that the artifact exists, OR the git diff/SHA. `sofi_tools.gates.validate_evidence()` scans done-tickets and **rejects any that assert completion without pasted evidence** — the same fail-closed shape as the no-skip and tier-boundary checks. Self-report is not evidence; the mechanical gate is. (Anthropic's #1 repeated finding across their eval + harness posts.)

## V2 — Fresh-context adversarial verify (before a gate advances)
Before advancing a gate, the work is checked by a **separate agent that sees only the diff/output + the original ticket criteria — not the reasoning that produced it.** This removes the implementer-grades-itself blind spot (Claude Code's `/code-review` pattern, and SOFI's own `cavecrew-reviewer`). Rules from the judge-bias research:
- **Fixed role, not free-form debate.** One pass argues "this is wrong/incomplete," a defender responds, a decider rules — roles are assigned, not emergent. Free-form multi-agent debate measurably *homogenizes toward confident-but-wrong* claims (arXiv:2606.03032, 2606.10296); role-fixed structure resists it. SOFI's tier isolation already gives this for free — the Advisor/next-tier reviewer is a different, differently-scoped agent.
- **"Unknown / insufficient evidence" is a valid verdict.** The reviewer is never forced into pass/fail; forcing a binary makes judges fabricate justifications for whichever output reads more fluently (verbosity bias). "Needs human / can't tell from the evidence" routes to `sofi escalate`, not a coin-flip.
- **Prefer family/prompt diversity for the judge.** A Claude agent judging another Claude agent's work carries self-enhancement bias (the largest, most consistent judge bias). Where a genuinely different model is available (the **Gemini review desk** is exactly this), route high-stakes verdicts there. Otherwise use an adversarially-framed fresh-context prompt as the minimum.

## V3 — Reliability over capability at Gate 5/6 (pass^k)
Gates check a single pass of `sofi_verify.py`. For anything money/auth/PII-touching heading to Staging/Prod, capability (pass@1 — it worked once) is not enough; **reliability (pass^k — it works every time across k runs)** is the bar. At Gate 5 (Quality) and Gate 6 (Staging/UAT), re-run the critical-path check k times; flaky/non-reproducible correctness is exactly what "plausible but wrong" looks like statistically and must block the gate.

## V4 — Never gate an irreversible action on verbalized confidence
Verbalized confidence ("I'm 90% sure this is safe to deploy") is proven miscalibrated and self-serving once the agent has committed to an action. Route ship/rollback/merge/irreversible decisions through **behavioral proxies** — did the mechanical check exit 0, does the artifact exist, did k runs all pass — never the model's self-rated certainty.

## V5 — Judges drift; sample the transcripts
An LLM-as-judge (SOFI's `/sofi-spec-review` Fable "hard gate") is a biased instrument, not a free lunch. A 0% pass rate usually means a broken grader, not incapable work. Periodically spot-check the full trajectory behind a PASS (and any suspicious 0%) against CEO/human review — a grader nobody audits silently drifts false-lenient or false-strict.

## Where this wires in
- `sofi_tools.gates.validate_evidence()` → `sofi gate-check` (V1, mechanical).
- `01-delegation-rccf.md` Format block requires the evidence block on completion (V1).
- `/sofi-spec-review` gains an `UNKNOWN` verdict + a note to prefer the Gemini desk for family-diverse judging (V2, V5).
- `/sofi-secure` gains an adversarial self-verify pass (one agent refutes each finding before it's ranked) + a per-finding execution plan (V2).
- `handoff-and-interconnection.md` gate sign-off references V1/V2 as the bar for `accepted`.
