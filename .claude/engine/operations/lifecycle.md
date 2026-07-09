# Gate Lifecycle — 9 Gates to Production

## The 9 Gates

| Gate | Name | Room Lead | Deliverable | Exit Sign-off |
|------|------|-----------|-------------|---------------|
| 0 | Inception | str-lead (Amara Okafor) | Project Blueprint | str-lead |
| 1 | Discovery | res-lead (Hiroshi Tanaka) | Customer Journey Map | res-lead |
| 2 | Design | dsn-lead (Dan Kim) | Prototype Spec | dsn-lead + CPO |
| 3 | Architecture | arc-lead (Vikram Rao) | Architecture Package | arc-lead + CTO |
| 4 | Build | bck/fnt/mob leads | Working Software | Room leads |
| 5 | Quality | qa-lead (Barb Jensen) | PASS/BLOCK Verdict | qa-lead + CQO |
| 6 | Staging | ops-lead (Linda Schmidt) | Staged Release | ops-lead |
| 7 | Production | ops-lead | Live Deployment | ops-lead |
| 8 | Observe | obs-lead (Naomi Brooks) | SLO Report | obs-lead |

## Flow

```
Start → G0 → G1 → G2 → G3 → G4 → G5 → G6 → G7 → G8 → loop to G0
```

Each gate produces a frozen signed artifact. The next gate consumes it.

## Hard Rules

1. **No gate skip.** Ever. A downstream agent with incomplete upstream -> reject upward.
2. **Adversarial verify.** Gatekeeper (gtw-gatekeeper) checks in CLEAN context — never the implementer.
3. **Evidence over self-report.** "Tests pass" without pasted output -> REJECTED.
4. **Gate exit = signed artifact.** Frozen. No changes without re-entering the gate.
5. **Reject upward.** If upstream deliverable is missing or incomplete -> BLOCKED, escalate to room lead.
6. **Implementer never self-grades.** The one who built it does NOT verify it.
7. **Every gate has a single owner** (room lead), even if multiple people contribute.

## Gate Exit Artifacts

| Gate | Frozen Artifact | Storage |
|------|----------------|---------|
| 0 | `_artifacts/blueprint.md` | Project dir |
| 1 | `_artifacts/journey-map.md` | Project dir |
| 2 | `_artifacts/prototype-spec.md` | Project dir |
| 3 | `_artifacts/architecture-package.md` | Project dir |
| 4 | Code + `_artifacts/ci-report.md` | Codebase |
| 5 | `_artifacts/qa-verdict.md` | Project dir |
| 6 | `_artifacts/staging-report.md` | Project dir |
| 7 | `_artifacts/deploy-report.md` | Project dir |
| 8 | `_artifacts/slo-report.md` | Project dir |

## Fast-Track

Low-risk work (UI copy, i18n, non-money fields) collapses Gates 1-3 into one Blueprint check.

**Eligibility** determined at Gate 0 by str-lead per `governance/fast-track.md`.

## Deep-Audit

Money, auth, PII, integrations -> full 9 gates. No exceptions.

**Triggered** by: str-lead at classification, or gatekeeper if scope changes mid-flight.
