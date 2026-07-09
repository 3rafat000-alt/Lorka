# RCCF Block Template

**R**ole · **C**ontext · **C**ommand · **F**ormat — the 4-part delegation contract.

> Every spawn is a filled RCCF block. Missing fields = agent guesses. Don't spawn if you can't fill all 4.

```
╔══════════════════════════════════════════════════════════════╗
║  🎭 ROLE                                                    ║
║  Persona: [room-role] (e.g., bck-api-engineer)              ║
║  Tier:    [mechanical | workhorse | gatekeeper | deep]      ║
║  Route:   [model tag per routing.yaml]                      ║
║                                                              ║
║  📂 CONTEXT                                                  ║
║  Project:  PRJ-XXXX                                         ║
║  Gate:     [N]                                              ║
║  Brain:    projects/PRJ-XXXX/_context/{STATE,CONTEXT,       ║
║            HANDOFFS,DECISIONS}.md                            ║
║  Frozen:   [artifact path] §[section]                       ║
║                                                              ║
║  🎯 COMMAND                                                  ║
║  Build:    [verb + object — one bounded unit]               ║
║  In:       [sub-parts — numbered]                           ║
║  Out:      [what NOT to touch — explicit boundaries]        ║
║  Metric:   [how to measure success]                         ║
║                                                              ║
║  📐 FORMAT                                                   ║
║  Paths:    [file paths to create/modify]                    ║
║  Gate-Bar: [criteria that must pass]                        ║
║  Evidence: [what to paste as proof]                         ║
║  Handoff:  → [next agent / ticket]                          ║
║  Effort:   [trivial-fix | single-role | cross-tier |        ║
║             audit-sweep | arbitration]                       ║
║  Fail-safe: [stop condition — what triggers abort]          ║
╚══════════════════════════════════════════════════════════════╝
```

## Example — Filled Block

```
🎭 ROLE
  Persona: bck-api-engineer
  Tier:    workhorse
  Route:   🔵 sonnet

📂 CONTEXT
  Project:  PRJ-SAKK
  Gate:     4
  Brain:    projects/PRJ-SAKK/_context/STATE.md
  Frozen:   projects/PRJ-SAKK/_artifacts/openapi.yaml §wallets

🎯 COMMAND
  Build:    Create WalletController + tests
  In:       GET /wallets, POST /wallets, GET /wallets/{id}
  Out:      DO NOT touch auth middleware or payment integration
  Metric:   All 3 endpoints pass 422-JSON rule, coverage ≥ 90%

📐 FORMAT
  Paths:    app/Http/Controllers/Api/WalletController.php
            app/Http/Requests/WalletRequest.php
            tests/Feature/WalletTest.php
  Gate-Bar: phpunit green, coverage ≥ 90%, route:list matches spec
  Evidence: Paste phpunit output, route list, coverage report
  Handoff:  → bck-code-reviewer
  Effort:   single-role
  Fail-safe: If any endpoint deviates from OpenAPI spec → abort
```

## Self-Check Before Spawn

1. 🎭 Persona + tier + route? (Y/N)
2. 📂 Brain + one frozen artifact? (Y/N)
3. 🎯 One bounded unit + out-of-bounds? (Y/N)
4. 📐 Gradeable done + gate-bar + evidence? (Y/N)
5. 🎚️ Effort class + fail-safe? (Y/N)
6. ❓ All fields filled with real specifics? (Y/N)

**If any N → DO NOT SPAWN → clarify first.**
لدي سوال للامان فقط سوال اذا خليت الداتابيز ولوحة التحكم ولارفيل كامل كله localhost بس الـ api و صفحة الهبوط ظاهرين