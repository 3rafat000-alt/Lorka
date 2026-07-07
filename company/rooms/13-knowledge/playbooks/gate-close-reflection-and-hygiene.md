# Playbook — gate-close reflection & hygiene

> Owner: `knw-lead`. This is the room's core procedure — how `13-knowledge` moves at every gate close (any gate, any room) from a batch of closed tickets to a distilled, compressed, correctly-dated brain. Run at the close of every numbered gate, and on-demand whenever a room's Lead requests it (`/sofi-reflect`, a compression request, an ADR to file). Never solo-triggered mid-task — the sequence below only starts once a gate has actually closed or an explicit on-demand request lands. Every step names the real `sofi` command; nothing here is aspirational.

## Phase A — orient, confirm the trigger is real

1. **`knw-lead` orients — never blind.** Runs `sofi sync <PRJ>` and reads `STATE.md` (branch + `head_sha`) and `HANDOFFS.md` for the closing gate's tickets.
   ```bash
   sofi sync <PRJ>
   sofi brain <PRJ>
   ```
2. **Confirm the trigger.** A gate actually closed (its exit bar was met, `sofi gate-check <PRJ> --gate <N>` passed) — or an explicit on-demand request exists (`/sofi-reflect`, a named compression request, an ADR with a real date attached). `knw-lead` does not run this playbook on a hunch that "it's probably time."
   ```bash
   sofi gate-check <PRJ> --gate <N>
   ```

## Phase B — reflect first, always before compressing

3. **Dispatch `knw-reflector` before anyone else in the room.** This ordering matters: a lesson worth distilling should never be compressed away by the curator before it's written down. `knw-reflector` runs the mechanical locate pass at zero model tokens.
   ```bash
   python3 company/os/agents/ceo/reflection_engine.py scan --prj <PRJ>
   ```
4. **`knw-reflector` distils each surviving candidate into exactly one lesson** — `situation · what-failed · rule`, citing the source ticket. No batching, no re-summarizing, no skipping the citation.
   ```bash
   python3 company/os/agents/ceo/reflection_engine.py write --prj <PRJ> \
     --sig "<kind-subject-ticket>" --situation "<S>" --failed "<F>" --rule "<R>" \
     --source "<TKT-NNN>" --date <YYYY-MM-DD>
   ```
5. **Any promotion candidate (2+ correction rounds, or a ≥3× recurring pattern) is flagged, not applied.** `knw-reflector` hands it to `knw-lead`, who carries it to `brd-ceo` — reflection proposes, the CEO decides.

## Phase C — curate, only after reflection is written

6. **Dispatch `knw-memory-curator` next**, and only on files that actually crossed the ~300-line threshold, or that the gate close otherwise flags. He never compresses speculatively.
7. **Backup before touching anything.** `.original.md` is written before the live file is edited — no exceptions, no "quick fix first."
8. **Compress only the compressible categories** (CONTEXT bullets, ticket prose, status chatter, TEAM_STATUS-shaped content) — code, commits, security warnings, ADR rationale + rollback plans, evidence blocks, and LESSONS rules are left byte-for-byte untouched, per `company/brain/BRAIN.md` §8.
9. **Frontmatter pass.** Any `type:`/`mem:`/`status:`/`sig:` field missing or malformed on a touched file gets corrected as part of the same pass — cheap now, expensive for `knw-brain-query` to discover broken later.

## Phase D — log the history, with a real date

10. **Dispatch `knw-historian` for any decision the gate produced.** She confirms the date came from `brd-ceo`'s actual Work Order before doing anything else — no date supplied, the request is returned blocked, not logged as "today."
    ```bash
    # via sofi_tools.brain.append_decision — auto-increments ADR-NNN
    ```
11. **Irreversible decisions get a rollback plan confirmed present**, not merely implied, before the entry is called complete (Teaching VI).
12. **Project-scoped and org-scoped ADRs are filed in their own ledgers** — never mixed. A company-wide decision goes to `company/brain/org/DECISIONS.md`; a project decision stays in `projects/<PRJ>/_context/DECISIONS.md`.

## Phase E — checkpoint and close

13. **`knw-lead` checkpoints the room's work as one unit** — reflection + hygiene + history logging together, not three scattered uncommitted edits.
    ```bash
    sofi checkpoint <PRJ> "knw: gate <N> close — reflection + hygiene + ADR pass"
    ```
14. **Close.** `/sofi-handoff` on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. An uncommitted memory pass is invisible to the next session — never leave one open.

## Bar (mechanical, checked before any self-report is trusted)

- Every new `LESSONS.md` entry carries `sig:` + a cited source ticket, and no already-distilled sig was re-surfaced.
- Every compression ships with an intact `.original.md` sibling; no never-compressed category was touched.
- Every new ADR entry carries a real date from the actual Work Order, and every irreversible one carries a rollback plan.
- `MEMORY.md` still resolves every pointer and sits under 200 lines after the pass.
- The whole pass is one checkpoint, not several scattered uncommitted edits.
