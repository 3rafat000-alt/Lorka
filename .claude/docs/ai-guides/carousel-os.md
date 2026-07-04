# Carousel OS: An AI-Powered Instagram Studio That Works With Claude, Codex, or Gemini

**Source:** https://www.aiwithmo.com/prompts/carousel-os

## Summary
Note: the fetched page rendered in English (site has an in-page AR/EN toggle; the crawl captured the English variant), not Arabic as expected — otherwise content matches the target URL, so treated as legitimate. Carousel OS is a paid, platform-agnostic content-creation tool that plugs into whichever AI assistant a user already has (Claude Code, Codex, Gemini CLI, or Claude Cowork) to turn plain-language requests into publish-ready Instagram carousels. It replaces a claimed 60-90 minute manual workflow with a one-time brand onboarding followed by conversational generation and revision.

## Key Techniques / Patterns
- One-time brand onboarding (5-10 min) captures voice, color palette, audience, and content pillars up front so every later output stays consistent.
- Conversational refinement: users edit drafts in plain language ("make slide 3 more direct") instead of re-prompting from scratch.
- Platform-agnostic design: identical product/workflow layered on top of multiple underlying LLM tools (Claude, Codex, Gemini).
- Feedback-learning memory (Pro tier): adapts future outputs to a user's recurring edit patterns across sessions.
- Automated scheduling (Pro tier): generates carousels from trending topics or a content calendar without a fresh prompt each time.

## Concrete Examples From the Article
- Claims manual carousel creation takes 60-90 minutes; the tool collapses this to a single sentence prompt, generating 8-10 slides plus a 150-250 word caption at 1080x1350px.
- Sample prompts: "Make me a carousel about the five biggest AI tools of 2026"; "Write a carousel explaining what a no-code SaaS is, for beginners."
- Sample revisions: "Make slide 3 more direct"; "Change the hook — make it bolder."
- Pricing (launch code LAUNCH70): Lite $45 (reg. $149, single brand, manual export); Pro $75 (reg. $249, multi-brand, auto-scheduling, memory system).

## Relevance to SOFI
Not directly applicable — reference only; no technique to extract. This is a consumer product/pricing announcement for an Instagram content tool, not a teaching article about agent orchestration, delegation, or multi-agent system design. The only loosely transferable idea — onboard durable context once, then converse — is already handled more rigorously in SOFI by the git-backed brain (`STATE/CONTEXT/DECISIONS/HANDOFFS.md`) and RCCF delegation, so there is nothing new to import.

## Actionable Takeaway
None — reference only.
