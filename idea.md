# Idea: Dual-Mode API Platform

Tags: #idea #promising #api #ai

## Status
- Promising

## One-line idea
- Build an API platform that serves both human-friendly and agent-optimized representations from one shared backend and domain model.

## Why it is interesting
- It directly targets a real gap: most APIs are designed for humans first, while AI agents increasingly need compact, deterministic, low-token, low-latency interfaces.
- If the concept works, it could reduce agent cost, simplify orchestration, and become a reusable API pattern rather than a one-off product.

## Problem / opportunity
- Human-oriented APIs are often too verbose and inefficient for AI agents.
- Agents waste tokens parsing fields and wrappers they do not need.
- Multi-call orchestration adds latency and complexity.
- There is an opportunity to define a cleaner API pattern that treats AI systems as first-class consumers instead of an afterthought.

## Early shape
- One backend with a shared domain model.
- Two optimized representations:
  - human mode for readability and debugging
  - agent mode for compactness, determinism, and lower token cost
- Likely implemented with FastAPI, typed schemas, and profile-based or endpoint-based response shaping.
- Early concepts already include:
  - response profiles
  - verbosity controls
  - cursor pagination
  - batch endpoints
  - delta endpoints
  - compact agent-oriented error handling

## Questions to explore
- Is this best positioned as a framework, reference architecture, or product/platform?
- How much response compression is useful before it harms developer trust or adoption?
- Should dual-mode behavior be profile-based on the same endpoint, or should agent endpoints be explicitly separate?
- Which first domain would best validate the idea, for example assets, monitoring, or automation workflows?
- What would make this meaningfully better than just adding GraphQL, field selection, or custom transformation layers?

## Risks / doubts
- Risk of over-engineering the abstraction too early.
- Risk that dual-mode APIs become harder to maintain consistently than expected.
- Compact agent schemas may reduce human clarity or create onboarding friction.
- The “paradigm shift” framing may be stronger than current market demand unless a concrete wedge is proven first.

## Signals that would make this stronger
- A real benchmark showing lower payload size, fewer calls, or lower token usage in agent workflows.
- A convincing first domain where the difference is obvious and valuable.
- Evidence that teams actually struggle with current human-first API design in agent systems.
- A strong MVP proving shared-domain dual representations can stay maintainable.

## Possible next steps
- Decide the first validation domain.
- Turn the existing PRD into a lighter first-sprint validation plan.
- Define the narrowest MVP contract for human mode vs agent mode.
- Build a small FastAPI prototype to compare payload size, latency, and agent workflow complexity.

## Related notes / inputs
- Source note: `/home/nmsadmin/ai_api_idea.md`
- Supporting PRD copied into this idea folder as `prd.md`.

## Promotion trigger
- Promote this into `../projects/` when there is a concrete commitment to build and test an MVP in a chosen first domain with defined success criteria.

## Notes
- This idea already has a fairly mature pitch and PRD, so it sits near the boundary between exploratory idea and real project.
- For now it still fits best as an idea because the product form, first wedge, and validation path are not fully nailed down.
