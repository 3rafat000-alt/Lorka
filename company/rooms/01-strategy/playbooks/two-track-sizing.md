# Playbook — Two-Track Sizing (Fast-Track vs Deep-Audit)

> Owner: `str-roadmap-planner` (risk input: `str-risk-analyst`; final declaration: `str-lead`). The room's sharpest recurring judgment call — every milestone, on every project, gets classified into exactly one of two lanes, and that classification decides how many gates the work actually has to pass through.

## When to run this

Every time a milestone enters `docs/<PRJ>_Roadmap.md` — at Gate 0 for the initial roadmap, and again any time a new milestone is added later in the project's life (a Gate-8 SLO breach re-opening Gate 1 often produces a fresh milestone that needs this same classification).

## Why it matters

`company/constitution/10-lifecycle-gates.md` (§Gate discipline, "Two tracks") is binding: **Fast-Track** collapses Gates 1–3 into one Blueprint check for genuinely low-risk work (UI copy, i18n, a single field, non-money validation) — straight to Gate 4 build on a green automated-test path. **Deep-Audit** — anything touching money, credentials, auth, or PII — takes all 9 gates, no exception, no matter how small the change looks. Getting this call wrong in the cheap direction (calling something Fast-Track that touches money) is a security and financial defect, not a process shortcut; getting it wrong in the expensive direction (calling something Deep-Audit that didn't need it) only costs time. The asymmetry is the whole reason the default is "unsure → deep_audit."

## Steps

### 1. Read the milestone against the frozen Risk Register
```bash
sofi brain-query PRJ-XXXX type:risk
```
For each milestone `str-roadmap-planner` is about to sequence, cross-check it against every risk `str-risk-analyst` filed in `docs/PRJ-XXXX_Risk_Register.md`. A milestone that touches a risk flagged money/credentials/auth/PII is an automatic `deep_audit` — this step is a lookup, not a judgment call, once the Risk Register exists.

### 2. Apply the four-question test for anything not already flagged
For a milestone with no directly-matching flagged risk, ask, in order:
1. Does this milestone move money in any direction (pricing, payment, refund, payout, credit)?
2. Does this milestone touch credentials (auth, session, password, token, API key)?
3. Does this milestone touch PII (anything identifying a real person beyond a display name)?
4. Is this milestone reversible at near-zero cost if it ships wrong (a copy edit, a translation string, a non-money form field)?

Yes to 1, 2, or 3 → `deep_audit`, full stop, no further questions needed. No to 1–3 and yes to 4 → `fast_track` is defensible. Any hesitation on 1–3, or "not sure" anywhere → `deep_audit` (Article 00, the binding default).

### 3. Name the collapse explicitly for Fast-Track milestones
A `fast_track` tag isn't just a label — it has to name exactly what it collapses:
```
fast_track: Gates 1-3 collapse into one Blueprint check → prod on green automated tests
```
Write this into the milestone's entry in `docs/PRJ-XXXX_Roadmap.md`, not left implicit. A future reader (including `gtw-gatekeeper` at gate-check time) needs to see the collapse stated, not infer it.

### 4. `str-lead` reviews every Deep-Audit-adjacent call
Any milestone touching money/credentials/auth/PII gets a second look from `str-lead` before the roadmap is signed — this is the one place inside the room where a specialist's call is always double-checked, because the cost of getting it wrong in the cheap direction is categorically higher than anywhere else in Gate 0.

### 5. Forward the Deep-Audit trigger
For every `deep_audit` milestone, `str-lead` forwards the classification to `sec-lead` so `brd-cso`'s posture is set before the milestone reaches its own Gate 3:
```bash
sofi dispatch PRJ-XXXX --agent sec-lead --intent "Deep-Audit milestone declared: <milestone id>, reason: <money/credentials/auth/PII, file:line in Risk_Register>"
```

### 6. Record the classification with its reasoning
Every track tag in the shipped roadmap carries the one-line reasoning that produced it — never a bare label. This is what lets a later reader (or a Gate-1 loop-back) re-evaluate the call against new evidence without re-deriving it from scratch.

## Worked example

```
Milestone M3 — "Add referral credit to user wallet"
  → touches money (question 1: yes)
  → track: deep_audit
  → reasoning: credits a monetary balance; Risk_Register R-04 (fraud via referral abuse) applies directly
  → forwarded to sec-lead: deep_audit trigger filed
```

```
Milestone M7 — "Add Spanish locale strings"
  → no money/credentials/PII (questions 1-3: no) · reversible at near-zero cost (question 4: yes)
  → track: fast_track
  → reasoning: pure i18n string addition, no schema/auth/payment surface touched
  → collapse: Gates 1-3 → one Blueprint check → prod on green tests
```

## Rules

- The four-question test is a floor, not a ceiling — a milestone can fail all four and still get bumped to `deep_audit` on `str-lead`'s judgment (e.g. a "just a UI copy change" that happens to sit on a checkout page).
- Never reclassify a milestone from `deep_audit` to `fast_track` to save time on a deadline — the track exists precisely to resist that pressure.
- Pairs with `playbooks/gate-0-inception.md` (step 4, where `str-roadmap-planner` runs) and `company/constitution/10-lifecycle-gates.md` (the binding law this playbook operationalizes).
