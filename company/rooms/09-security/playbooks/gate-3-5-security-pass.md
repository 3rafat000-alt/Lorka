# Playbook — the Gate 3 / Gate 5 security pass

> Owner: `sec-lead`. This is the room's core procedure — how `09-security` moves from a frozen Gate-2 prototype (via `04-architecture`'s Gate-3 fan-out) through a signed threat model, into the Build rooms as must-fix controls, and back through a Gate-5 pentest/appsec verdict. Run alongside `04-architecture`/`08-data` at Gate 3 and `10-quality` at Gate 5 — never solo, never out of sequence. Every step below names the real `sofi` command; nothing here is aspirational.

## Phase A — Gate 3: threat model + design review

1. **Orient — never blind.** `sec-lead` runs `sofi sync <PRJ>` and reads `projects/<PRJ>/_context/STATE.md` (branch + `head_sha`) and `HANDOFFS.md` for the room's Gate-3 ticket. Confirms `04-architecture` has frozen `Prototype_Spec.md` + `Content_Strings.json` (the Gate-2 tag exists) before dispatching anyone.
   ```bash
   sofi sync <PRJ>
   sofi brain <PRJ> state
   ```

2. **Confirm the squad fan-out.** Gate 3 is a `cross-room` effort-scaling class — `04-architecture`, `08-data`, and `09-security` run in parallel behind the *same* frozen input.
   ```bash
   sofi squad <PRJ> 3
   ```

3. **Dispatch `sec-threat-modeler` first.** Nothing else in the room starts until the STRIDE skeleton exists. `sec-lead` builds the Work Order from the frozen `OpenAPI.yaml` + `Schema.sql` (via `arc-lead`) and any `PII_Map.md` from `dat-lead`.
   ```bash
   sofi dispatch <PRJ> <TKT>
   ```

4. **`sec-threat-modeler` scaffolds STRIDE at zero extra tokens, then fills it.**
   ```bash
   python3 company/os/agents/tier-1-architecture/security-compliance-architect/stride_scaffold.py \
     "<feature-name>" --prj <PRJ> --out docs/<PRJ>_Threat_Model.md
   ```
   Every asset/data-flow row gets a stated mitigation or an explicit accepted-risk note with a named owner — no blank rows survive this step.

5. **`sec-authn-engineer` reviews the implementability of the auth/authz design in parallel** — confirms a real token TTL, rotation schedule, and hashing algorithm are named, not left as placeholders. Findings fold directly into `docs/<PRJ>_Threat_Model.md` before it's called a draft.

6. **`sec-lead` checks the draft against the room bar** — zero unmitigated High risk, every authz rule confirmed server-derivable, `stride_scaffold.py` output fully filled. Anything short of that bar is bounced back inside the room, attempt-counted toward the circuit breaker (3 attempts, then HALT + crash dump).

7. **`sec-lead` signs and forwards to `arc-lead`.** The Gate-3 bundle does not freeze without this signature; an unmitigated High holds the freeze open until `sec-lead`/`brd-cso` clear it.
   ```bash
   sofi checkpoint <PRJ> "sec: threat model + authz design signed for gate 3"
   ```

8. **Gate-3 exit.** `sofi gate-check <PRJ> --gate 3` runs the mechanical validation (artifact existence, evidence blocks, traceability); a fresh-context adversarial verify by `gtw-gatekeeper` follows before the gate actually opens — never the room's own self-report.
   ```bash
   sofi gate-check <PRJ> --gate 3
   ```

## Phase B — the gap: controls land in code (Gate 4, not this room's window)

`09-security` does not build in Gate 4. The must-fix controls named in `docs/<PRJ>_Threat_Model.md` (per-endpoint authz, secret handling, encryption requirements, the token TTL/rotation/hashing choices `sec-authn-engineer` specified) are implemented by the owning Build-room engineers, forwarded verbatim by `sec-lead` through `bck-lead`/`fnt-lead`/`mob-lead`. `09-security` re-enters at Gate 5, once the build is merged.

## Phase C — Gate 5: appsec review + pentest + verdict

9. **Orient again — the build has moved since Gate 3.** `sec-lead` confirms `prj/<PRJ>` carries the full Gate-4 merge (`sofi git-check <PRJ>`) and that `qa-test-architect`'s strategy (including the pass^k plan for Tier-A money/auth/PII surfaces) exists before dispatching.
   ```bash
   sofi git-check <PRJ>
   sofi squad <PRJ> 5
   ```

10. **Dispatch `sec-appsec-engineer`, `sec-pentester`, and `sec-authn-engineer` in parallel** behind the same merged build — each with a Work Order naming the merged commit and the Gate-3 `Threat_Model.md` as baseline.

11. **Zero-token pre-flag pass first, always.** Every specialist opens with the static scan before reading a single file by hand.
    ```bash
    python3 company/os/agents/ceo/sofi_scan.py security "<target>" --prj <PRJ> --md
    ```

12. **`sec-appsec-engineer` traces flagged patterns to confirmed sinks; `sec-pentester` attempts real exploitation and runs the adversarial self-verify pass on every candidate finding before ranking it** (Article 03 V2 — refute first, report only what survives). `sec-authn-engineer` diffs the shipped implementation against the frozen Gate-3 auth design.

13. **Rank and report.** `CVSS-ish SEV · finding · proof · remediation` per surviving issue, normal prose, `docs/<PRJ>_Pentest_Report.md` + the appsec findings + the authn diff — each finding carries an Execution Plan block (owning agent id, `file:line`, the change, the re-test) so `/sofi-fix` can act without re-deriving the remediation.

14. **Oracle desk, before handoff.** Push the aggregated security verdict through the review desk — the family-diverse second opinion this class of finding calls for (Article 03 V2, money/auth/PII).
    ```bash
    sofi oracle review --prj <PRJ> --json --text "<findings (location-only, no live secrets) + context + ask>"
    ```

15. **`sec-lead` signs the room's Gate-5 contribution** — zero unmitigated Critical/High — and forwards to `qa-lead` for the aggregated PASS/BLOCK verdict.
    ```bash
    sofi checkpoint <PRJ> "sec: gate 5 appsec + pentest verdict signed"
    sofi gate-check <PRJ> --gate 5
    ```

16. **Close.** `/sofi-handoff` on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. An uncommitted security pass is invisible to the next session — never leave one open.

## Bar (mechanical, checked before any human/model self-report is trusted)

- Gate 3: `Threat_Model.md` exists, every row filled, zero unmitigated High, `sec-lead` signature present.
- Gate 5: `Pentest_Report.md` + appsec findings exist, every finding reproducible, zero unmitigated Critical/High, adversarial self-verify pass recorded.
- Both: evidence block present (cmd + exit code | file:line | diff/SHA) — `gate-check` fails closed without it.
