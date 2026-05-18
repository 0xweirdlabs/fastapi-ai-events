# Separate /agent/ URL prefix instead of ?profile= parameter

Agent and human endpoints are separated by URL prefix (`/agent/alarms` vs `/alarms`) rather than a query parameter (`?profile=agent`). A profile parameter was considered but rejected: agent endpoints do fundamentally different things (delta sync, batch, compressed schemas, field selection) that have no human-mode equivalent. Separate prefixes give unambiguous OpenAPI schemas per surface, allow each surface to evolve and be versioned independently, and make it explicit to consumers which mode they are targeting.
