---
name: sofi-report
description: Synthesize a professional, evidence-backed report from audit, security, or fix runs — executive summary, severity-ranked findings with file:line proof, remediation status, and next actions. Bilingual-ready (EN/AR). Written to the project brain, not lost in chat. Use to hand stakeholders or the next session a clean record. Triggers — "report", "write it up", "summary of findings", "security report", "audit report", "status writeup", "document what we found".
---

# /sofi-report — turn a run into a durable, professional record

> A report lives in the project, not the chat. Findings/security text = normal prose,
> never compressed (routing law). Structure over volume — big brain, small mouth.

**Usage:** `/sofi-report [kind] [PRJ-ID]` — kind ∈ `audit · security · fix · status`.
No kind → infer from the last run. Writes to `projects/<PRJ>/_context/reports/<kind>-<date>.md`
(date passed in — no `Date.now()`).

## Report shape (fill only sections with content)

```
# <Kind> Report — <PRJ> — <date>
## 1. Executive summary        # 3–5 lines: scope, top risk, verdict
## 2. Scope & method           # layers/targets swept, tools/skills used
## 3. Findings                 # table: SEV · file:line · defect · proof · fix · status
## 4. Remediation              # what was fixed (commit sha), what's deferred + why
## 5. Risk posture / gate      # is the quality/security bar met? gate advance? (/sofi-gate)
## 6. Next actions             # ranked, each → owning agent
```

## Rules

- **Every finding cites `file:line`** and a concrete fix — no vague filler.
- **Severity legend** consistent with audit/secure: 🔴 🟠 🟡 ⚪.
- **Secrets:** reference location, never print the value.
- **Bilingual:** if the project is EN/AR ([[web-design-premium-bilingual]]), add an AR الملخص التنفيذي block.
- **Traceability:** link the commit sha(s) from `/sofi-fix` and the `head_sha` in STATE.
- **Review desk (standing):** push the report through the desk before handoff — `sofi gemini review --prj <PRJ> --json --text "<report body + ask>"` (inline, no extra `.md`) → analyze + EXECUTE the reply, loop till done, don't ask. `engine/protocols/external-review-desk.md`.
- **Close the loop:** write the file → `sofi checkpoint <PRJ> "docs(report): <kind>"` → note it in `CONTEXT.md` → `/sofi-handoff`.

**Bar:** a reader who wasn't in the session can act from this report alone. No conclusions without evidence.
