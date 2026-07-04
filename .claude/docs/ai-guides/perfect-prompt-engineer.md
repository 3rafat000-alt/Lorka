# How to Turn Any Raw Idea into a Professional AI Prompt

**Source:** https://www.aiwithmo.com/prompts/perfect-prompt-engineer

## Summary
This is a "Prompts" library entry teaching a meta-prompting workflow: paste a pre-built "Prompt Engineer" persona template into a fresh chat, feed it a raw/messy idea in natural language, and it converts that idea into a polished, professional, copy-paste-ready prompt. The AI may ask clarifying questions first if the raw idea is too vague, then hands back the optimized prompt for use in a separate, clean conversation.

## Key Techniques / Patterns
- **Meta-prompt persona**: assign the model the role "World-Class Prompt Engineer and AI Optimization Specialist" whose only job is to *write* prompts, never execute them.
- **Fixed drafting framework**: structure every output prompt around Context, Objective, Style, Tone, Audience, Response Format.
- **Persona injection**: the generated prompt itself assigns a specific expert persona to the downstream task (e.g., "Senior React Developer").
- **Clarity + constraints + Chain-of-Thought**: explicitly bake reasoning steps and boundaries into the optimized prompt.
- **Language mirroring**: output prompt language must match the input idea's language.
- **Separation of concerns**: use the optimized prompt in a *new* chat, not the same one that generated it, to avoid context contamination.
- **Two-part deliverable format**: (1) the optimized prompt in a code block, (2) optional clarifying questions if the raw input was ambiguous.

## Concrete Examples From the Article
The template names one sample persona to assign in generated prompts — "Senior React Developer" — and specifies the engineer-persona's readiness line: "Ready. Send me your raw idea, and I will engineer the perfect prompt for you." No numerical data, case studies, or before/after prompt transcripts are given.

## Relevance to SOFI
Directly applicable, but as a micro-pattern rather than an architectural one. SOFI's RCCF delegation block (`engine/protocols/01-delegation-rccf.md`) already structurally mirrors this article's framework (Context/Objective/Style/Tone/Audience/Format ≈ Role·Context·Command·Format). The article's real contribution is the *meta-prompt-as-a-tool* pattern: a standing "prompt engineer" persona that only drafts instructions and never executes them — this maps well to `/sofi-delegate`, which already exists to generate paste-ready RCCF blocks rather than do the work itself. The "ask clarifying questions if vague, else draft" behavior is worth reinforcing in `/sofi-delegate` for underspecified tickets.

## Actionable Takeaway
Harden `/sofi-delegate` to explicitly branch: if the task description is underspecified, emit clarifying questions instead of a half-formed RCCF block; only emit the paste-ready block once Role/Context/Command/Format can be filled with real specifics — same gatekeeping the article's template applies before drafting.
