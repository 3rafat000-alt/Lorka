# Toolchain Architect — the zero-token engine doctrine

> Adapted from the *Automation & Toolchain Architect* brief to the **real** SOFI layout.
> Doctrine: **Design is Truth · few token do trick · big brain small mouth.** Python does the
> deterministic heavy lifting (locate · pre-flag · verify); the model spends its expensive
> tokens only on **judgment**. Every tool is flexible across any `PRJ-<id>`.

## 1. Real environment (not `PRJ-{name}/`)
The brief imagines each project as a root `PRJ-{name}/`. Real SOFI:
- Framework repo: `~/Desktop/Lorka/` (this repo).
- Projects: physical root `~/Desktop/projects/<PRJ-ID>/` (single-root, NO symlink; resolve via `sofi_tools.paths.projects_dir()` / `project_repo()`).
- Brain per project: `projects/<PRJ-ID>/_context/{STATE,CONTEXT,DECISIONS,HANDOFFS}.md`.
- Ephemeral scripts: `projects/<PRJ-ID>/_scratch/` (purged at gate exit — never a deliverable).
Every engine resolves the project via `feature_scan._project_dir(prj)` → works unchanged for any PRJ.

## 2. The Python automation core (0 model tokens)
All engines live in `engine/tooling/agents/ceo/` and emit compact JSON or `--md`. Pure stdlib. **Never write source.**

| Engine | Modes / job | Backs |
|---|---|---|
| `sofi_scan.py` | `search feature design flow security wiring **taint taste** all` | audit · spec-review · secure · design-taste |
| `feature_scan.py` | feature file-set + 4-pillar pre-flags | spec-review · feature |
| `sofi_verify.py` | `lint view route flutter assets` — **mechanical gate** | the "declare done" step |

### sofi-scan (static analysis)
- `security` — regex OWASP pre-flags (XSS `{!! !!}`, SQLi, mass-assign, secrets, IDOR) with local
  false-positive guards (`_xss_safe`, `_env_ok`, `_idor_check`, `_weakrand`…). Cuts noise before AI review.
- `taint` — **source→sink taint trace** (the brief's "AST path-tracing", done as intra-file var-flow):
  user input (`$request->`, `$_GET`, `->input()`) reaching a sink (SQLi/XSS/RCE/path-traversal/open-redirect)
  with **no sanitizer between**. Taint clears on `e()/intval/validated/escapeshellarg/…`. Deeper than `security`.
- `design` — flags **any** hardcoded literal (hex, px font-size, `!important`, missing alt/aria, motion w/o reduced-motion, RTL).
- `taste` — **value↔token cross-check**: literal that **duplicates an existing `:root` token value** → "use `var(--x)`".
  Higher signal than `design`. Skips `emails/ seeders/ mail/` (mail clients strip CSS vars).

### sofi-verify (mechanical verification — brief's step 3)
`python sofi_verify.py --prj <ID> [--only lint,view,route,flutter,assets] [--changed] [--md]`
- `lint` → `php -l` (all, or `--changed` = git-diff PHP only).
- `view` → `artisan view:cache` then `view:clear` (compiles every Blade, never leaves cache).
- `route` → `artisan route:list --json` (fails on missing controller/action).
- `flutter` → `flutter analyze` (mobile static gate).
- `assets` → resolve Blade `asset()/@include/src=` local refs → flag ones missing on disk.
- **Exit code GATES the loop**: `0` all pass · `1` a check failed · `2` nothing to run (soft, exits 0).
  Auto-skips any check whose toolchain is absent → runs anywhere.

## 3. Commander interface — single-command loops (already wired as skills)
The brief's shortcuts map 1:1 to real `.claude/skills/`:
`/sofi-boot` `/sofi-spec-review` `/sofi-feature` `/sofi-fix` `/sofi-secure` `/sofi-report` `/sofi-handoff`
`/sofi-audit` `/sofi-gate` `/sofi-team` `/sofi-delegate` `/sofi-design-taste`.
Loop: **boot → scan/verify → fix → report → gate → handoff**.

## 4. Execution protocol (Understand · Verify · Commit)
1. **Understand intent** — map command → engine mode. No fluff.
2. **Scan first (free)** — run the Python engine; the model reads only the ranked `file:line` hints, never the tree.
3. **Mechanical verification** — before "done", `sofi_verify.py` must exit 0. A red gate stops the pipeline.
4. **Isolated tracking** — every fix = one traceable `sofi checkpoint` commit. CEO never authors app code (delegate);
   framework **tooling** is architect work.

## 5. Doctrine boundaries
- Code / commits / security warnings = **normal prose, never compressed**, never token-scanned for taste.
- Engines are HINT generators, not verdicts — a human/agent opens each `file:line`, confirms, ranks.
- One-off scripts → `_scratch/`; promoted tools → `engine/tooling/` + a row in `registry.yaml`.
