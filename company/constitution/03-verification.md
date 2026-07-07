# ✔ Article 03 — Verification (outcome over self-report)

> **Foundation: serves Teaching VI (Reversibility)** — nothing advances that can't be shown correct — **and Teaching II (Hierarchical Flow)** — a gate is a checkpoint, not a rubber stamp. Read `02-grounding.md` first (this article is G3 made mechanical), then `company/nexus/gates.yaml` for what each gate demands.

The single highest-value quality lever in agentic systems: **never trust the acting agent's word that it succeeded — check the actual outcome.** An agent saying "tests pass / booking confirmed / migration applied" is exactly the execution hallucination that propagates into a shipped bug. v6 wires the discipline into the gateway room: verification is a *role*, not a hope.

## V1 — Outcome over self-report (mechanical)

A ticket marked `done` / `passing` must carry an **evidence block**: the command that was run + its output/exit code, OR a `file:line` proof that the artifact exists, OR the git diff/SHA. `sofi_tools.gates.validate_evidence()` scans done-tickets inside `sofi gate-check` and **rejects any that assert completion without pasted evidence** — fail-closed, the same shape as the no-skip and room-boundary checks. Self-report is not evidence; the mechanical gate is. The Work Order's Format field requires the evidence block on completion (`01-work-order.md`), so producer and gate enforce the same law at two layers.

## V2 — Fresh-context adversarial verify (before a gate advances)

Before any gate advances, the work is checked by **`gtw-gatekeeper` — a separate agent that sees only the diff/output + the ORIGINAL ticket criteria, never the reasoning that produced the work, and never the implementer grading itself.** Rules, each grounded in the judge-bias research:

- **Fixed roles, not free-form debate.** One pass argues "this is wrong/incomplete," a defender responds, a decider rules — roles are assigned, not emergent. Free-form multi-agent debate measurably homogenizes toward confident-but-wrong; role-fixed structure resists it. The Room Isolation Law gives this for free: the gatekeeper is a different, differently-scoped agent in a different room.
- **UNKNOWN is a valid verdict.** The verifier is never forced into pass/fail; forcing a binary makes judges fabricate justifications for whichever output reads more fluently. "Insufficient evidence — can't tell" routes to `sofi escalate`, not a coin-flip. `/sofi-spec-review` carries the UNKNOWN verdict per pillar.
- **Prefer a family-diverse judge for high stakes.** A Claude agent judging another Claude agent's work carries self-enhancement bias — the largest, most consistent judge bias. For money/auth/PII verdicts, route the check through the **oracle desk** (`gtw-external-reviewer`, `sofi oracle review`) — a genuinely different model family. Otherwise the minimum is an adversarially-framed fresh-context prompt.

## V3 — Reliability over capability (pass^k at Gates 5–6)

For anything money/auth/PII-touching heading to Staging/Prod, capability (pass@1 — it worked once) is not enough; **reliability (pass^k — it works every time across k runs)** is the bar. At Gate 5 (Quality) and Gate 6 (Staging/UAT), re-run the critical-path check k times (`qa-test-architect` sets k in the test strategy; `qa-automation-engineer` executes). Flaky, non-reproducible correctness is what "plausible but wrong" looks like statistically — it **blocks** the gate.

## V4 — Never gate an irreversible action on verbalized confidence

"I'm 90% sure this is safe to deploy" is proven miscalibrated and self-serving once the agent has committed to an action. Ship / rollback / merge / migration decisions gate on **behavioral proxies only**: did the mechanical check exit 0, does the artifact exist at its path, did k runs all pass, is the rollback script tested. Never the model's self-rated certainty. (`ops-release-manager` owns the way back; Teaching VI.)

## V5 — Judges drift; sample the transcripts

An LLM-as-judge — the spec-review hard gate, the gatekeeper, a code reviewer — is a biased instrument, not a free lunch. A 0% pass rate usually means a broken grader, not incapable work; a 100% pass rate usually means a lenient one. Periodically spot-check the full trajectory behind a PASS and behind any 0-finding report (`brd-cqo` owns the audit cadence). A grader nobody audits silently drifts false-lenient or false-strict.

## Where this wires in

| Wire | Mechanism |
|---|---|
| V1 mechanical | `sofi_tools.gates.validate_evidence()` → `sofi gate-check`, fail-closed |
| V1 at handover | `01-work-order.md` Format requires the evidence block on completion |
| V2 gate advance | `gtw-gatekeeper` fresh-context adversarial check against original criteria — mandatory before `sofi gate-tag`; `/sofi-gate` runs both layers |
| V2 in-room | `bck-code-reviewer` / `fnt-code-reviewer` review diffs fresh-context before work leaves the room |
| V2 judge diversity | high-stakes verdicts → oracle desk (`gtw-external-reviewer`) — family-diverse judge |
| V3 | pass^k plan in the Gate-5 test strategy; flake quarantine by `qa-regression-warden` |
| V4 | `ops-release-manager` gates ship/rollback on behavioral proxies only |
| V5 | `brd-cqo` transcript spot-checks; `/sofi-secure` adds an adversarial self-verify pass (one agent refutes each finding before ranking) |
| Sign-off | `08-handoff-law.md` — `accepted` requires V1 + V2; a bare "done" bounces |

**The law in one line: a gate advances on pasted mechanical evidence plus a fresh-context adversarial check against the original criteria — never on the implementer's word.**
