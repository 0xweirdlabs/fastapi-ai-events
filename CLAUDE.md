# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Weirdlabs.ai is a **Dual-Mode API Platform** built on FastAPI. The core idea: one shared backend and domain model that serves two optimized response representations — a human-friendly interface for developers and a compact, deterministic interface for AI agents.

The project is currently in the **pre-implementation / planning phase**. The authoritative specs are:
- `idea.md` — concept overview, open questions, risks, and promotion criteria
- `prd-concept.md` — full pitch and PRD including functional requirements, architecture layers, and MVP scope

## Planned Tech Stack

- **FastAPI** + **Pydantic** — web framework and schema validation
- **PostgreSQL** — primary database
- **Redis** — caching
- **Uvicorn + uvloop** — ASGI server

No build, test, or run commands exist yet. Establish these when the FastAPI skeleton is created.

## Architecture

Four-layer design:

```
API Layer     → FastAPI routers (human vs agent endpoints)
Service Layer → Business logic, shared across both modes
Domain Models → Single source of truth (Pydantic models)
Data Layer    → PostgreSQL queries, Redis caching
```

**Dual-mode response strategy** — the same domain model produces two representations:

| Feature | Human mode | Agent mode |
|---|---|---|
| Fields | Verbose, descriptive | Short keys (`sym`, `px`, `id`) |
| Errors | Descriptive messages | Compact error codes |
| Pagination | `page` / `page_size` | `cursor` / `limit` |
| Profile param | `?profile=human` | `?profile=agent` |
| Verbosity | `?verbosity=min\|standard\|full` | — |

Agent-specific endpoints: `POST /agent/assets/get-many` (batch), `GET /agent/assets/delta?since=<ts>` (delta sync), `GET /agent/assets?fields=id,sym,px` (field selection).

## MVP Scope

Per `prd-concept.md` §11:
- dual response profiles
- cursor pagination
- batch endpoints
- basic delta support

The first validation domain (e.g., assets, monitoring, or automation workflows) is not yet decided.

## Agent Skills

This repo uses [Matt Pocock's engineering skills](https://github.com/mattpocock/skills), locked in `skills-lock.json`. Available skills via `/skill-name`:

| Skill | Purpose |
|---|---|
| `/tdd` | Red-green-refactor loop, vertical slices (one test → one impl) |
| `/diagnose` | Disciplined debugging workflow |
| `/grill-me` | Brainstorming and exploration |
| `/grill-with-docs` | Documentation-driven design using ADRs and domain glossary |
| `/improve-codebase-architecture` | Deepening and interface design |
| `/prototype` | Throwaway prototypes (logic or UI) |
| `/zoom-out` | High-level codebase exploration |
| `/to-prd` | Convert discussion to PRD |
| `/to-issues` | Convert discussion to tracked issues |
| `/triage` | Issue triage and prioritization |
| `/handoff` | Task handoff documentation |
| `/caveman` | Code simplification review |

**TDD approach** (from `/tdd` skill): integration-style tests through public interfaces only. Vertical slices — one test → one implementation at a time. Do not mock internal collaborators; mock only at system boundaries.

When the codebase is initialized, run `/setup-matt-pocock-skills` to configure `CONTEXT.md` (domain glossary) and `docs/adr/` (Architecture Decision Records), which the skills reference.

## Agent skills

### Issue tracker

Issues live in GitHub Issues (via `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
