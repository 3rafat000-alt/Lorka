# 🤖 Autonomous Gemini Loop

**Binding:** Teaching VII. Every agent obeys this. No exceptions.

## The Loop

```
┌────────────────────────────────────────┐
│  1. WORK → 2. FINDING / DECISION       │
│         ↓                              │
│  3. ROUTE TO GEMINI (not user)         │
│         ↓                              │
│  4. EXECUTE GEMINI'S STEPS             │
│         ↓                              │
│  5. COMMIT → LOOP OR DONE             │
└────────────────────────────────────────┘
```

## Banned

- "What should I do?" → route to Gemini
- "I found X" → route to Gemini
- "Which option?" → route to Gemini
- Writing .md and waiting → route to Gemini

## Allowed (no Gemini)

- Typo fix, rename, boilerplate — just do it
- Decision frozen in spec — follow spec
- Test passes — verify, commit, move on

## Push Triggers

| Trigger | Action |
|---------|--------|
| Finding worth acting on | Push: "what's the fix priority?" |
| Multiple paths | Push: "which path wins?" |
| Test fails >3x | Push: "diagnose + fix path" |
| Scope exceeds budget | Push: "cut or extend?" |
| Before destructive act | Push: "safe to X?" + ADR |
| Integration ambiguity | Push: "reconcile shape?" |

## Standing Preamble

Every push includes (auto-injected):

```
[سياق ثابت] أنت مستشار معماري كبير تُوجّه وكيل ذكاء اصطناعي ذاتي التشغيل (SOFI AI)، 
لستَ تخاطب إنساناً. أعطِ توجيهاً مفصّلاً دقيقاً قابلاً للتنفيذ خطوة بخطوة.
```

## Escalation (not Gemini)

For blockers above agent authority:
```bash
sofi escalate <PRJ> <ticket> <to> "<reason>"
```
