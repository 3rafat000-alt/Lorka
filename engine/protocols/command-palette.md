# SOFI Command Palette — the only `/` shortcuts the team uses

> Doctrine: **few token do trick.** One tight palette, each command flexible (takes an
> arg + fans out). No 47-skill clutter. The CEO and every agent learn these and nothing else.

## The 10 SOFI commands (nothing else is "the team's")

### Spine — the universal contract (`CLAUDE.md`)
| Command | Arg | Job | When |
|---------|-----|-----|------|
| `/sofi-boot` | `[PRJ]` | git sync + load brain (STATE/CONTEXT/HANDOFFS); report gate·branch·head_sha·next ticket | **start of every session — never blind** |
| `/sofi-team` | `<need>` | map task → the right agent (tier·gate·route) + spawn name | deciding who does the work |
| `/sofi-delegate` | `<agent> "<task>"` | build the paste-ready **RCCF** brief (Role·Context·Command·Format) | before every spawn |
| `/sofi-gate` | `[N]` | check the gate exit-bar; advance exactly one gate (no skip) | moving 0→8 |
| `/sofi-handoff` | — | write artifact → checkpoint → CONTEXT/DECISIONS → STATE(head_sha) → next ticket | **end of every unit of work** |

### Power tools — flexible, grep-first, cheapest-clears-bar
| Command | Arg | Job |
|---------|-----|-----|
| `/sofi-audit` | `ui·blade·css·js·db·api·integration·agents·all` | comprehensive **layer** inspection; static sweep, cite `file:line`, severity-ranked. **Reads, never writes.** |
| `/sofi-spec-review` | `"<feature>"` | architect + UX-principal **feature** review via fixed 4-pillar matrix (Data&Logic · Admin&Ops · UI/UX&Taste · Edge-cases). Python-scanned, token-frugal. **Reads, never writes.** |
| `/sofi-feature` | `"<feature>"` | **the big one** — full loop on one feature in a single command: Python scan → 4-pillar review → route fixes → verify → report → gate → handoff. Reads via Python, writes only through delegated specialists. |
| `/sofi-secure` | `threat·pentest·scan·verify` | the security squad; OWASP-driven; reads the cyber KB in `engine/superpowers/cybersecurity-skills/` |
| `/sofi-fix` | `<finding·layer·report>` | route each finding → cheapest specialist agent → RCCF → **commit each** (CEO never writes) |
| `/sofi-report` | `audit·security·fix·status` | durable evidence-backed writeup to `projects/<PRJ>/_context/reports/`, EN/AR |
| `/sofi-design-taste` | `<view>` | kill generic AI-UI; set 3 dials + brand preset; a11y always wins |
| `/sofi-reflect` | `[PRJ]` | **v5:** scheduled "dreaming" — distil HANDOFFS history into `_context/LESSONS.md` procedural memory (grounded lessons); run at gate-close, never per-turn. `reflection.md` |

Plus two CLI queries (not slash commands): `sofi brain-query <PRJ> status=blocked type=security` (v5 structured-brain filter) and `python3 engine/tooling/agents/ceo/reflection_engine.py scan --prj <PRJ>` (locate learning signals, 0 model tokens).

## The standard loop (the main session orchestrates *as* the CEO; specialists execute)

> Flat topology (`engine/protocols/01-delegation-rccf.md` §0): the **main session** is the only context that can spawn — `sofi-ceo` and the tier-advisors are personas it *wears*, not live orchestrators. Every step below runs from the main session, one hop to a leaf specialist.

```
/sofi-boot            # orient — never blind
   ↓
/sofi-audit <layer>   # or /sofi-secure <mode> — inspect, don't fix yet (free, grep-first)
   ↓
/sofi-fix <target>    # route findings → specialists → checkpoint each
   ↓
/sofi-secure verify   # (security only) confirm closed, no regression
   ↓
/sofi-report <kind>   # durable record to the brain
   ↓
sofi gemini review    # STANDING second opinion — push report → analyze + EXECUTE reply → loop till done (§ below)
   ↓
/sofi-gate            # bar met? advance one gate
   ↓
/sofi-handoff         # record head_sha + next ticket — uncommitted = invisible
```

## External review desk — STANDING on every report/verdict (binding)

Every command that ends in a report, verdict, or design decision — `/sofi-spec-review`,
`/sofi-audit`, `/sofi-secure`, `/sofi-feature`, `/sofi-fix`, `/sofi-report` — routes that output
through the external review desk **before handoff**, automatically. This is not optional and not a
separate command the user asks for; it is the closing move of every report-producing command.

```bash
sofi gemini review --prj <PRJ> --json \
  --ask "Explain in detail and give professional, actionable guidance" \
  --text "<Full description: the problem + context + what we tried + the decision needed>"
```

**The loop (autonomous — the user is NOT a step):** compose the report INLINE (`--text`, never
author a `.md` just to send it) → send → read the reply → **ANALYZE + EXECUTE** the guidance
(delegate/fix/checkpoint) → if a new decision point surfaces, loop again. Don't stop to ask; the
reply IS the direction. Only break out for a genuinely destructive/irreversible action or a real
scope change. `sofi gemini capture` resumes a timed-out capture; `sofi gemini status` probes.
Python sanitizes (redacts secrets/keys/`.env`) and ingests the reply digest into `HANDOFFS.md`.
Full rules: `engine/protocols/external-review-desk.md`. Orientation commands (`/sofi-boot`,
`/sofi-team`, `/sofi-delegate`, `/sofi-gate`, `/sofi-handoff`) don't produce a report, so they cite
the desk as the next step rather than firing it.

## The engine — every command leans on Python (token-frugal law)

The team does NOT read the tree by hand. A unified Python engine does the deterministic
thinking (locate · pre-flag · map) at **0 model tokens**; the model reads the skeleton and
opens only flagged `file:line`. This is *few token do trick* in code.

```bash
python3 engine/tooling/agents/ceo/sofi_scan.py <mode> "<query>" --prj <PRJ> --md
python3 engine/tooling/agents/ceo/feature_scan.py "<feature>" --prj <PRJ> --md   # 4-pillar feature pre-flag
```

| mode | thinks about | backs command |
|------|--------------|---------------|
| `search` | ranked code locator (smart find) | `/sofi-audit`, general "where is X" |
| `feature` | feature file-set + 4-pillar pre-flags | `/sofi-spec-review`, `/sofi-feature` |
| `security` | XSS · SQLi · mass-assign · secrets · IDOR · weak-rand · auth | `/sofi-secure scan` |
| `design` | tokens · motion · density · a11y · RTL · AI-UI smell | `/sofi-design-taste` |
| `flow` | UserFlow: routes→views + orphan/dead-end views | `/sofi-audit ui`, UX journey |
| `wiring` | interconnection: env/config · dead includes · hardcoded URLs · leftovers | `/sofi-audit integration` |
| `taint` | source→sink taint trace: user input → sink unsanitized (deeper than `security`) | `/sofi-secure` |
| `taste` | value↔token cross-check: literal duplicating an existing `:root` token → use `var()` | `/sofi-design-taste` |
| `all` | design+security+wiring+flow merged | full health |

Pre-flags are **static HINTS, not verdicts** — the model confirms, ranks, and adds the
semantic findings heuristics can't see. Engine reads; it never writes.

**Mechanical verify gate** — before declaring any task done, the runner must exit 0:

```bash
python3 engine/tooling/agents/ceo/sofi_verify.py --prj <PRJ> --md [--only lint,view,route,flutter,assets] [--changed]
```

Drives the real toolchain (`php -l` · `artisan view:cache` · `route:list` · `flutter analyze` · asset-resolve),
auto-skips absent tools, **exit code gates the pipeline**. Full doctrine: `protocols/toolchain-architect.md`.

## Rules the whole team obeys
- **Inspect before fix.** `audit`/`secure` never mutate; only `fix` (via agents) writes.
- **Cheapest that clears the bar.** Static grep first; agent only to repair; opus only for security/API/arbitration.
- **Every op = checkpoint.** No uncommitted handoff (`sofi checkpoint` or `/sofi-handoff`).
- **CEO no-write** ([[ceo-orchestrator-no-write-doctrine]]): the leader thinks/routes; specialists author code.
- **Security & code text = normal prose, never compressed** (routing law).
- Non-SOFI global skills (seo-*, deep-research, claude-mem, caveman, ui-ux-pro-max) are **not** the team's palette — ignore them for project work. seo-* are disabled in this project's `.claude/settings.json`.

## Removed / consolidated (was clutter)
- 47 invokable `cyber-*` skills → **removed** from palette; knowledge preserved in `engine/superpowers/cybersecurity-skills/` (817 skills), reached only through `/sofi-secure`.
- 30 `seo-*` user skills + `deep-research` → **disabled** in project settings (still available in other projects).
