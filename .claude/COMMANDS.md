# ⚡ SOFI AI — Quick Command Cheat-Sheet

Keep it nearby. Full detail in `USER_GUIDE.md`.

## 🚀 Start
```
Use the sofi-ceo agent
New project: <idea>. Start onboarding
```

## ▶️ Flow control
| Command | Does |
|---------|------|
| `continue` | advance to the next gate |
| `assume reasonable answers and proceed to gate 4` | run straight through, no pauses |
| `where are we?` | read STATE.md (don't re-explain) |
| `revisit the decision` | loop back to the right gate |
| `give me the project summary` | state + tickets + ADRs |

## 🎯 Ideal request format
```
Goal:     <one sentence>
Project:  PRJ-XXXX | new
Limits:   <stack / platform / deadline>
Priority: CRITICAL | HIGH | MEDIUM | LOW
Success:  <when it's done>
```

## 🧑‍💼 Direct agent call (rare)
```
Use the sofi-<role> agent: <task>
```
Common: `sofi-security-compliance-architect` (security) · `sofi-qa-sre-lead` (quality) · `sofi-principal-system-architect` (architecture) · `sofi-backend-blade-engineer` (code).

## 🛠️ Tooling (Bash-holding roles)
```
engine/tooling/bin/sofi doctor            self-check
engine/tooling/bin/sofi route <role>      cheapest clearing route
engine/tooling/bin/sofi brain <PRJ>       STATE + next open ticket
engine/tooling/bin/sofi gate-check <PRJ>  validate gate order + artifacts
engine/tooling/bin/sofi dispatch <PRJ>    delegation prompt for the open ticket
```

## 🪨 Tokens
```
/caveman lite|full|ultra
normal mode
/caveman-stats
```

## 🗂️ Gates
`0 Inception → 1 Discovery → 2 Design → 3 Architecture → 4 Build → 5 Quality → 6-7 Deploy → 8 Observe`

## ✅ Remember
- Talk to the CEO, not the individuals.
- Goal + limits + success = best context.
- One project per PRJ.
- Code / security are never compressed.
- `where are we?` before any big request.
