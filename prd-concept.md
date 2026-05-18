# Dual-Mode API Platform

_Source input copied from `/home/nmsadmin/ai_api_idea.md` for use inside the idea folder._

## Pitch + Product Requirements Document (PRD)

### Pitch

#### The Problem
APIs today are built for humans, not for AI.

Human APIs are verbose, descriptive, and easy to debug.
AI agents need compact, deterministic, and efficient data.

Result:
- AI systems waste tokens parsing unnecessary data
- Increased latency due to multiple API calls
- Complex orchestration logic on the agent side

Most companies solve this poorly by:
- building separate APIs
- adding transformation layers
- letting agents "figure it out"

This creates inefficiency, fragility, and cost.

#### The Opportunity
We are entering a world where:
- AI agents are first-class consumers of APIs
- systems communicate machine-to-machine at scale
- token efficiency directly impacts cost and performance

There is no standard yet for APIs optimized for both humans and AI.

This is the gap.

#### The Solution
A Dual-Mode API Platform built on FastAPI:

One backend. Two optimized interfaces.

| Mode | Optimized for |
|---|---|
| Human | Readability, debugging, developer UX |
| Agent | Speed, compactness, determinism |

#### Key Innovation
Instead of choosing between:
- human-friendly APIs
- machine-efficient APIs

Provide both using:
- shared domain model
- profile-based responses
- agent-native endpoints

#### Why This Wins
##### 1. Token Efficiency
- Reduced payload size, lower AI cost
- Faster parsing, better performance

##### 2. Fewer API Calls
- Batch endpoints
- Context endpoints
- Delta synchronization

##### 3. Deterministic Behavior
- Stable schemas
- Predictable responses
- Less agent reasoning overhead

##### 4. Developer Experience
- Clean FastAPI structure
- Strong typing with Pydantic
- Clear OpenAPI documentation

#### Example
##### Human API
```json
{
  "status": "success",
  "data": {
    "asset_id": "ast_123",
    "name": "Bitcoin",
    "symbol": "BTC",
    "current_price": 84250.12
  }
}
```

##### Agent API
```json
{
  "id": "ast_123",
  "n": "Bitcoin",
  "sym": "BTC",
  "px": 84250.12
}
```

#### Target Use Cases
- AI-powered dashboards
- Autonomous trading systems
- Monitoring and observability agents
- Workflow automation agents
- Multi-agent orchestration platforms

#### Competitive Advantage
Most APIs are built for humans first, with AI treated as secondary.

This platform:
- treats AI as a first-class citizen
- reduces cost and complexity of AI systems

#### Vision
Become the standard API pattern for AI-native systems.

## Product Requirements Document

### 1. Objective
Build a scalable API platform that:
- serves both human users and AI agents
- minimizes latency and payload size
- supports high-frequency agent communication

### 2. Core Principles
- single source of truth (domain model)
- multiple representations (human vs agent)
- deterministic outputs
- minimal payload for agents
- batch-first design

### 3. Functional Requirements
#### 3.1 Response Profiles
Support:
- `profile=human`
- `profile=agent`

#### 3.2 Verbosity Control
Query parameter:
- `?verbosity=min|standard|full`

#### 3.3 Pagination
Human:
- `page` / `page_size`

Agent:
- `cursor` / `limit`

#### 3.4 Batch Endpoints
Example:
- `POST /agent/assets/get-many`

#### 3.5 Delta Endpoints
Example:
- `GET /agent/assets/delta?since=timestamp`

#### 3.6 Field Selection
- `GET /agent/assets?fields=id,sym,px`

#### 3.7 Error Handling
Human:
- descriptive messages

Agent:
- compact error codes

### 4. Non-Functional Requirements
- low latency
- high throughput
- idempotent operations
- strong schema validation
- consistent formatting

### 5. Architecture
Layers:
- API Layer (FastAPI)
- Service Layer
- Domain Models
- Data Layer

### 6. Technical Stack
- FastAPI
- Pydantic
- PostgreSQL
- Redis (caching)
- Uvicorn + uvloop

### 7. Performance Strategy
- minimize payload size
- use cursor pagination
- implement caching
- use async processing

### 8. Advanced Features (Future)
- streaming responses (NDJSON)
- gRPC for internal communication
- agent task endpoints
- real-time updates via WebSockets

### 9. Risks
- over-engineering early
- schema inconsistency
- too much compression reducing readability

### 10. Success Metrics
- reduced API calls per workflow
- reduced payload size
- faster agent execution
- improved developer adoption

### 11. MVP Scope
- dual response profiles
- cursor pagination
- batch endpoints
- basic delta support

### 12. Next Steps
- define domain (for example assets or monitoring)
- build FastAPI skeleton
- implement dual schemas
- add agent endpoints
- test with real agent workflows

## Final Note
This is positioned not just as an API, but as a shift from APIs for humans to APIs for humans and AI, and eventually APIs primarily optimized for AI systems.
