# Animate Your UI With One Prompt: The Engineering Guide to AI-Built Motion

**Source:** https://www.aiwithmo.com/prompts/ai-ui-animation-engineering

**Note:** The fetch tool returned this content as English-language (not Arabic as expected); content is reported as-fetched.

## Summary
The article argues AI produces good UI animation only when prompted with precise engineering specs, not vague requests like "make it animated." Vague prompts yield janky, generic motion because the model must guess library choice, timing, and performance constraints. The fix is a structured four-part prompt covering persona, library selection, motion specification, and hard performance rules (GPU-accelerated properties only, 60fps target).

## Key Techniques / Patterns
- Library selection framework: Motion (standard React UI), GSAP (complex timelines/scroll sequences), React Spring (physics-based motion), AutoAnimate (list transitions), Lottie/Rive (vector animation)
- Four-part prompt structure: persona → library constraint → motion spec (easing/duration/stagger/trigger) → performance rules
- Performance rule: animate only `transform` and `opacity`; never animate layout-triggering properties (width/height/position)
- Accessibility: respect `prefers-reduced-motion`
- Restraint principle: animate key moments, not everything

## Concrete Examples From the Article
- Prompt template: "Act as a senior front-end engineer specializing in web animation. TASK: Add [animation]. LIBRARY: Use [X]. MOTION SPEC: Easing/Duration/Stagger/Trigger. PERFORMANCE RULES: only transform/opacity, respect prefers-reduced-motion, target 60fps."
- Example ask: "a staggered fade-and-rise entrance for feature cards, triggered on scroll into view"
- Refinement follow-ups: "Make the easing snappier," "Tighten the stagger to 50ms."
- Library stats cited: Motion (~6M weekly downloads), GSAP (15-year standard), React Spring (~18KB)

## Relevance to SOFI
Directly applicable to SOFI's frontend/Blade+Vue3+Tailwind build gate (Gate 4) and the `sofi-design-taste` skill. The four-part prompt structure (persona/library/spec/performance-rules) maps cleanly onto SOFI's RCCF delegation format when briefing `sofi-frontend-react-engineer` or `sofi-ux-researcher` for animation work — it gives a concrete template for the "Command" and "Format" parts of an RCCF block specifically for motion/UI tasks, and the performance rules (transform/opacity only, 60fps, prefers-reduced-motion) are a ready-made checklist item for Gate 4's TTI<2s bar and accessibility requirements.

## Actionable Takeaway
Add a short "Motion Spec" sub-template (library choice + easing/duration/stagger/trigger + performance rules) to the `sofi-design-taste` skill or RCCF delegation template, so any agent briefed on UI animation gets the same structured constraints instead of vague "add animation" instructions.
