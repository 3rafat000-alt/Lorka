# 🪨 Caveman — Token-Optimization Engine

**Repo:** <https://github.com/JuliusBrussee/caveman> — *"why use many token when few token do trick"*
Claude Code skill: cuts **~65% of output tokens** by stripping filler, keeping 100% technical substance. Code, commands, errors, URLs stay byte-exact.

## Mechanisms
| Tool | Does | Savings |
|------|------|--------:|
| Output compression | drops articles/hedging/pleasantries; keeps signal | ~65–75% output |
| Levels `lite/full/ultra/wenyan` | tune compression strength | configurable |
| `caveman-compress` | rewrite memory files (e.g. `CLAUDE.md`); keeps `.original.md` backup | ~46% input |
| `cavecrew` subagents | Investigator / Builder / Reviewer speak caveman | ~60% smaller results |
| `caveman-shrink` | MCP middleware compresses tool descriptions | variable |
| `caveman-commit` / `caveman-review` | terse commits + one-line review comments | high |
| `caveman-stats` | real tokens-saved from session log | reporting |

## Benchmarks (real Claude API counts)
| Task | Normal | Caveman | Save |
|------|-:|-:|-:|
| Explain React re-render bug | 1,180 | 159 | 87% |
| Fix auth middleware expiry | 704 | 121 | 83% |
| PG connection pool setup | 2,347 | 380 | 84% |
| React error boundary | 3,454 | 456 | 87% |
| **Average** | **1,214** | **294** | **~65%** |

## Install
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
# Windows (PowerShell)
irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 | iex
```
Trigger `/caveman` or "talk like caveman" · stop "normal mode" · level `/caveman lite|full|ultra`. Statusline badge `[CAVEMAN] ⛏ 12.4k`.

## Rules (all agent chatter)
- **Drop:** articles, filler (just/really/basically), pleasantries (sure/happy to), hedging.
- **Keep exact:** code, commands, error strings, terms, numbers, URLs.
- **Pattern:** `[thing] [action] [reason]. [next step].`

| ❌ Normal | ✅ Caveman |
|-----------|-----------|
| "The reason it re-renders is likely because you create a new object reference each render…" | "New object ref each render → re-render. Wrap in `useMemo`." |

## Safety override (caveman OFF → normal prose)
Security warnings · irreversible-action confirmations · multi-step sequences where order risks misread · **all code, commits, PR bodies**. Resume caveman after the critical part is clear.

## Subagents available in this workspace
- `cavecrew-investigator` — locate code, `file:line` table, no fixes.
- `cavecrew-builder` — bounded 1–2 file edit, caveman diff receipt.
- `cavecrew-reviewer` — one line per finding, severity-tagged.
