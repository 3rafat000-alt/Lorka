# 🧠 BRAIN.md — the memory architecture of SOFI v6

> **Design is Truth · few token do trick · big brain small mouth.** 🪨
> The company remembers in three layers. Nothing outside these layers is memory — "not in the brain = not true."
> Owner room: `company/rooms/13-knowledge/` (knw-lead, the Librarian). Laws this file serves:
> `company/constitution/00-operating-system.md` (read/write contract) · `02-grounding.md` (cite the brain, never memory) ·
> `04-reflection.md` (LESSONS distillation) · `05-token-economy.md` (grep-first, compress, never dump).

## 1. Three layers, three lifetimes

| Layer | Lives at | Scope | Lifetime | Committed? |
|---|---|---|---|---|
| **Org brain** | `company/brain/org/` | the company itself — doctrine evolution, ADRs, personas, distilled lessons | permanent | yes, on `main` |
| **Project brain** | `projects/<PRJ>/_context/` | one project — state, facts, decisions, tickets, lessons, foundations, locks | life of the project | yes, in the project's OWN repo on `prj/<PRJ>` |
| **Session memory** | `.claude/memory/*.jsonl` | one runtime — session breadcrumbs, security-block audit | runtime only | **never** (gitignored) |

Radical Isolation (Teaching III) applies between projects; the org brain is the only shared memory, and it holds doctrine + lessons, never project content. Cross-project bleed through any layer is a defect.

## 2. Org brain — `company/brain/org/`

| File | What it holds | Memory type | Writer |
|---|---|---|---|
| `DECISIONS.md` | company-level ADRs (ADR-NNN): architecture of the company itself | procedural | knw-historian (CEO decides, historian records) |
| `EVOLUTION.md` | framework improvement roadmap — Teaching V in writing; oracle-desk critiques triaged into executed/backlog | procedural | brd-chief-of-staff |
| `LESSONS.md` | company-wide distilled lessons (LES-NNN, sig-keyed, idempotent) | procedural | knw-reflector via `/sofi-reflect` |
| `PERSONAS.md` | the humans behind the ids — inherited v5 personas + v6 hires (full specs in `company/rooms/*/agents/`) | semantic | knw-doc-writer |
| `TEAM_STATUS.md` | org health snapshot: roster counts, powers, CLI surface, `sofi doctor` verdict | working | brd-chief-of-staff |
| `HANDOFFS.md` | org-level ticket queue (framework work, not project work) | episodic | gtw-dispatcher |
| `archive-v5/` | the entire v5 law preserved verbatim (DOCTRINE, ROSTER, RUNBOOK, protocols, agents, routing) — read-only history, superseded by `constitution/`, `nexus/`, `rooms/` | archival | nobody — frozen |

## 3. Project brain — `projects/<PRJ>/_context/`

Scaffolded by `company/os/bin/new-project.sh` from the canonical templates in `company/brain/templates/` (the scaffolder substitutes `PRJ-XXXX`, `<title>`, `YYYY-MM-DD`).

| File | Format | Memory type | Contract |
|---|---|---|---|
| `STATE.md` | `key: value` — title · doctrine · gate · active · status · priority · blockers · branch · head_sha · last_route · local_domain · local_port · public_url · created · updated_by | **working** — "where are we", overwritten in place | read FIRST every turn; `head_sha` updated at every checkpoint; parsed by `sofi_tools.brain.read_state` (pure key:value, no frontmatter) |
| `CONTEXT.md` | append-only `- [gate N] fact` bullets | **semantic** — what is true about this project | facts only, cited; the record of truth; never rewritten, only appended |
| `DECISIONS.md` | `## ADR-NNN (date) — title` / why / Reversible? | **procedural** — why we chose | every irreversible act lands here WITH a rollback plan (Teaching VI); auto-increment via `sofi_tools.brain.append_decision` |
| `HANDOFFS.md` | ticket blocks `## TKT-NNN · gate N` (schema: `company/nexus/bus/ticket-schema.md`) | **episodic** — who did what, when, for whom | the bus; room-boundary validated (`validate_room_boundary`); done only with an evidence block |
| `LESSONS.md` | `## LES-NNN` sig/mem/situation/what_failed/rule/source | **procedural** — what we learned | written ONLY by scheduled reflection (`/sofi-reflect`, knw-reflector), idempotent on `sig:`; read on every boot |
| `FOUNDATIONS.md` | the 7 Teachings pinned to THIS project | **semantic** — doctrine, localized | generated at scaffold; every Work Order's Context field points here |
| `LOCKS.md` | claimed paths: `<path> · <agent> · <TKT> · <date>` | **working** | `sofi claim` / `sofi release`; edit a claimed path = rejected |
| `_runlog.md` | one line per tool/script action | working | appended by `sofi_tools.runlog`; state changes are logged, نقطة |
| `../_scratch/` | throwaway scripts `tmp_<role>_<purpose>.py` | **working** | purged at gate exit (`sofi scratch clean`); never a deliverable, never committed |

## 4. Session memory — `.claude/memory/`

- `sessions.jsonl` — one row per session, appended by the Stop hook (`.claude/hooks/stop.py`). Breadcrumbs for the dashboard's Live Observatory, never authority.
- `audit.jsonl` — security blocks recorded by the PreToolUse guard. Input to reflection; security text always normal prose.

Runtime only, never committed, never cited as ground truth — if a fact matters, it graduates to the project brain via the write order below.

## 5. Memory types — the doctrine mapping

Four types, four homes. The `mem:` frontmatter key routes reflection consolidation (`constitution/04-reflection.md`):

| Type | Question it answers | Files |
|---|---|---|
| **semantic** | what is true? | `CONTEXT.md` · `FOUNDATIONS.md` · org `PERSONAS.md` |
| **episodic** | what happened? | `HANDOFFS.md` (project + org) · `_runlog.md` · `sessions.jsonl` |
| **procedural** | how do we act? | `DECISIONS.md` + `LESSONS.md` (project + org) · `EVOLUTION.md` |
| **working** | what is in hand right now? | `STATE.md` · `LOCKS.md` · `_scratch/` — cheap, overwritable, purgeable |

Consolidation flows one way: episodic → (reflection) → procedural. HANDOFFS history is the raw signal; `/sofi-reflect` distils it into LESSONS; recurring lessons may be promoted by the CEO into constitution or templates (proposed → piloted → promoted, never auto-rewritten).

## 6. Querying — frontmatter + grep, no vector DB (deliberate)

The brain is queryable because entries carry structure, not because it is embedded. Tickets and lessons carry `type:` / `mem:` / `status:` / `sig:` fields; `sofi brain-query <PRJ> [--filters]` (backed by `sofi_tools.tickets.query`, case-insensitive substring) answers questions like "all open gate-4 tickets to bck-lead" in one pass, zero model tokens. `sofi brain <PRJ>` reads; knw-brain-query is the retrieval specialist when a human-shaped question needs shaping into a query.

**Why no vector store:** the brain is small, structured, and grep-able; frontmatter + ripgrep beats embeddings on precision, cost, and auditability at this scale. Recorded as doctrine in org `DECISIONS.md` (ADR-009, C3). Python locates, the model judges — the cost lever everywhere.

## 7. Read order & write order — the universal contract, memory half

**Read order (before acting — never blind, never from memory):**
```
sofi sync <PRJ>                        # git orient: fetch, prj/<PRJ> branch, refuse dirty
1. STATE.md          → gate · branch · head_sha · blockers
2. HANDOFFS.md       → MY ticket (TKT-ID, consumes, expected, route)
3. CONTEXT.md        → facts so far        4. DECISIONS.md → binding choices
5. LESSONS.md        → don't repeat known failures (+ org LESSONS.md once per session)
6. the consumed frozen artifact — not frozen → reject upward, stop
```

**Write order (after acting — uncommitted = invisible):**
```
1. artifact at its exact path
2. sofi checkpoint <PRJ> "<type>: ..."   # conventional commit + SOFI: trailer, brain committed
3. append CONTEXT.md  "- [gate N] fact"  (+ DECISIONS.md if irreversible, with rollback)
4. update STATE.md    (head_sha, last_route, gate if advanced)
5. write next ticket in HANDOFFS.md      # with route + expected + evidence requirement
```

`/sofi-boot` is the read order operationalized; `/sofi-handoff` is the write order. Never one without the other.

## 8. Caveman-compress policy

Brain files grow; tokens are sacred (البخل المقدّس). knw-memory-curator owns hygiene:

- **Compressible (caveman lite/full/ultra):** CONTEXT bullets, ticket task prose, status chatter, TEAM_STATUS. Compress in place only at gate close or when a file crosses ~300 lines; meaning preserved, citations intact.
- **NEVER compressed:** code, commits, security warnings, ADR rationale + rollback plans, evidence blocks, LESSONS rules. These are the audit trail — full prose, always.
- STATE.md is not compressed — it is already minimal by format.
- Compression is a curator act, logged to `_runlog.md`, checkpointed like any other write.

## 9. Ingest vs Reach

Two verbs for external knowledge (`constitution/09-research-law.md`):

- **Ingest** — evergreen, decision-bearing knowledge enters the brain: an API's contract shape, a CVE verdict, a pattern that survived verification. Cited (`[source: url, fetched <date>]`), placed by memory type, owned by knw-lead.
- **Reach** — volatile knowledge is fetched fresh every time and NEVER ingested: prices, versions, live status, rankings. Ingesting volatiles poisons the brain with stale truth.
- `MEMORY.md` at the repo root is the routing map — pointers only, under 200 lines, "where do I find X?" — consult it before searching the vault blindly. Search ladder: map → brain → codebase → `sofi brain-query` → web (cite).

## 10. Non-negotiables

- Read the brain every turn; never act on model memory (CEO Covenant, vow 4).
- One artifact uncommitted, maximum. Checkpoint before handoff, نقطة.
- A fact without a citation is `[unverified]` — it does not enter CONTEXT (grounding G1).
- LESSONS writes go through reflection only — no per-turn moralizing.
- Session memory never substitutes for the project brain.
- The word **«تذكّر» / "remember"** is the only trigger for durable doctrine/preference writes outside the contract-driven project-brain writes.
