# Weirdlabs.ai — Dual-Mode API Platform

A FastAPI platform that serves the same data in two optimized representations:

- **Human mode** (`/alarms`) — verbose TMF-compliant responses for developer readability
- **Agent mode** (`/agent/alarms`) — compact field names, cursor pagination, batch and delta endpoints for AI agent consumption

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

## Run tests

```bash
python -m pytest
```

## Run the server

```bash
uvicorn weirdlabs.main:app --reload --app-dir src
```

API docs available at `http://localhost:8000/docs`.

## Project structure

```
src/weirdlabs/
├── main.py                  # FastAPI app
├── models/alarm.py          # Pydantic domain models
├── store.py                 # In-memory store (PostgreSQL coming later)
└── routers/
    ├── alarms.py            # GET|POST /alarms (human mode)
    └── agent_alarms.py      # GET /agent/alarms (agent mode)

tests/
└── test_alarms.py

docs/
├── adr/                     # Architecture Decision Records
└── agents/                  # Skill configuration (issue tracker, triage labels, domain docs)

CONTEXT.md                   # Domain glossary
```

## Domain

See [`CONTEXT.md`](CONTEXT.md) for the full domain glossary and [`docs/adr/`](docs/adr/) for architecture decisions.
