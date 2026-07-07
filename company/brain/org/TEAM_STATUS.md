# 📊 SOFI AI — Team Status

Live status is always `sofi doctor` (parity · routes · counts · verdict) + `company/ORG.md`
(roster). This file is only the latest **manual snapshot** for humans; when it disagrees with
`sofi doctor`, doctor wins. Owner: `brd-chief-of-staff`.

## Snapshot — 2026-07-08 (v7 rebuild in progress)
- **105 agents · 15 rooms** — full parity (105 spawnables ↔ 105 room specs), verified read-only.
- **9-gate lifecycle** (0 Inception → 8 Observe → loop), no skipping, `sofi gate-check`.
- **Company brain** per project (`projects/<PRJ>/_context/…`), isolated by PRJ-ID; framework
  brain in `company/brain/org/`.
- **Governed tooling** — `sofi_tools` library + `sofi` dispatcher (`company/os/`), GOVERNANCE
  enforced (scope sandbox · net policy · secret scan · exit-code gating). Shared per-role toolkits
  live in `company/os/toolkit/` (`ceo/` orchestration · `gate/` gate tools · `uiux/` · `devops/`).

## v7 rebuild
In progress — the phased program and its live status are tracked in
`company/brain/org/V7-REBUILD.md`. Pre-v7 recovery point: git tag `v6.1-recovery-pre-v7`.

## Health (read-only)
`sofi doctor` gates 105↔105 agent parity and registry-cited `.claude/skills/*` existence.
⚠️ Known v7 fix pending: `sofi doctor` currently rewrites agent `tools:` frontmatter as a side
effect — use read-only parity counts to verify until that is fixed (see V7-REBUILD.md open items).

## Open / next
Framework work is queued in `V7-REBUILD.md`. Project work is queued per-project in each
`projects/<PRJ>/_context/HANDOFFS.md`.
