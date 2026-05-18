# Weirdlabs.ai – Dual-Mode API Platform

A telecom-internal API platform that serves the same data in two optimized representations: a verbose TMF-compliant form for human consumers and a compact form for AI agents.

## Language

### Core

**Alarm**:
A structured event indicating a fault, violation, or threshold breach on a managed entity. Follows the TMF642 Alarm Management base structure. Every alarm has a shared base plus a category-specific extension.
_Avoid_: alert, event, incident (unless referring to ITSM incidents specifically)

**AlarmCategory**:
The classification of an alarm by the type of system it originates from. One of: `network`, `security`, `application`, `infrastructure`, `database`, `service`, `storage`, `kubernetes`, `host`.
_Avoid_: alarm type (overloaded with TMF's `alarmType` field), domain, class

**ManagedObject**:
The entity an alarm is raised against. Currently identified by a combination of `label` (human-readable name), and one or more loose identifiers: hostname, IP address, or a source-system-specific ID. No enforced global uniqueness exists yet — a future CMDB integration will add a `ci_id`.
_Avoid_: resource, target, source (overloaded), device

**SourceSystem** _(future)_:
The monitoring tool or system that emitted an alarm (e.g. Zabbix, Prometheus, a custom tool). Will carry at minimum an `id` and `name`. Not in MVP scope — the ingestion layer will assign this when source system tracking is implemented.
_Avoid_: reporter, origin system

**Score**:
A named scoring entry used on vulnerability advisories. Contains `method` (the scoring system name, e.g. `cvss` or a company-internal identifier), `value` (numeric), and optional `scale` (e.g. `0-10`). Stored as a list so multiple scoring methods can coexist without schema changes.
_Avoid_: severity score (conflicts with **Severity**), risk score

**ImpactedService**:
A reference to an entry in the internal service catalogue. Contains `id` (catalogue ID) and `label` (display name). Appears as a list on alarm extensions where downstream business services are affected.
_Avoid_: affected service (TMF field name clash), downstream dependency

### Alarm extension fields (category-specific)

**AlarmExtension**:
The category-specific block attached to an alarm. Every category has its own extension shape; all share the base `Alarm` fields.

Known extension fields by category:
- **service**: `reason` (string — why the service alarm was raised)
- **database**: `impacted_services` (list of `ImpactedService`)
- **host**: `metric` (string — e.g. `disk_usage`, `cpu_load`, `memory`, `temperature`), `current_value` (number), `threshold` (number), `unit` (string — e.g. `%`, `°C`, `GB`)
- **kubernetes**: `cluster` (string), `namespace` (string), `resource_kind` (open string — standard k8s kinds plus OpenShift-specific kinds such as `Route`, `DeploymentConfig`, `Project`), `resource_name` (string). Applies to both vanilla Kubernetes and OpenShift clusters.
- **network**: `interface` (string — e.g. `GigabitEthernet0/1`), `topology_element` (string — `link`, `node`, `interface`, `site`), `protocol` (optional string — e.g. `BGP`, `OSPF`, `MPLS`)
- **security**: two subtypes sharing the base `Alarm`:
  - _Detection event_: `attack_type` (string — e.g. `brute_force`, `port_scan`, `ddos`, `policy_violation`), `source_ip` (optional), `target_ip` (optional), `affected_user` (optional)
  - _Vulnerability advisory_: `cve_id` (string), `affected_software` (string), `affected_version` (string), `scores` (list of **Score**)
- **storage**: `storage_type` (open string — `san`, `nas`, `filesystem`, `s3`, `pvc`), plus type-specific fields:
  - _Traditional (san/nas/filesystem)_: `volume` (string), `capacity_used_pct` (optional float)
  - _Object storage (s3)_: `bucket` (string), `endpoint` (string — region or URL)
  - _Container storage (pvc)_: `pvc_name` (string), `namespace` (string), `storage_class` (string)
  - Note: PVC alarms belong to `storage`, not `kubernetes` — kubernetes alarms are about workloads, storage alarms are about storage resources
- **infrastructure**: cloud/virtualisation infrastructure alarms. `platform` (open string — `openstack`, `vmware`, or future public cloud providers), `datacenter` (string — on-prem location identifier), `resource_type` (open string — `vm`, `virtual_network`, `load_balancer`, `subnet`), `resource_id` (string — platform-native ID). On-prem for MVP; schema designed to accommodate public cloud providers without changes.
- **application**: two subtypes sharing the base application fields (`application_name`, `version`, `environment`):
  - _Generic application_: error rate spikes, latency breaches, unhealthy health checks
  - _Pipeline failure_: `pipeline_tool` (string — e.g. `airflow`, `n8n`, `prefect`), `pipeline_name` (string — DAG or workflow name), `run_id` (string — specific execution instance), `failed_task` (optional string — task or node that caused the failure), `reason` (string). Each pipeline run failure is its own **Alarm**; two pipelines failing = two independent alarms, each with their own **ManagedObject**.

### Severity

**Severity**:
The canonical urgency level of an alarm. Always one of the TMF642 values: `critical`, `major`, `minor`, `warning`, `indeterminate`, `cleared`. This is the internal representation regardless of what label any team uses.
_Avoid_: priority (separate concept), level

**SeverityLabel**:
A team-specific display name mapped to a canonical **Severity** (e.g. `P1` → `critical`, `high` → `major`). Normalised to canonical severity at ingestion; the original label is stored for auditability but is not used in queries or filters.
_Avoid_: severity alias, priority label

### Alarm states

**AlarmState**:
The lifecycle state of an alarm. One of: `raised`, `acknowledged`, `escalated`, `suppressed`, `in_maintenance`, `cleared`.
_Avoid_: status, condition

State meanings:
- `raised` — active and unacknowledged
- `acknowledged` — ownership taken by an operator
- `escalated` — raised in priority or visibility
- `suppressed` — manually muted on the individual alarm; no defined end time
- `in_maintenance` — the **ManagedObject** is in a planned maintenance window; time-bounded
- `cleared` — condition has resolved; terminal state

`suppressed` and `in_maintenance` are distinct: `in_maintenance` is tied to a planned window on the **ManagedObject**; `suppressed` is applied to a specific alarm instance with no schedule.

### Alarm correlation

**RootCauseAlarm**:
An alarm with no parent — the originating fault that triggers downstream alarms. Identified by the absence of a `parent_alarm_id`.
_Avoid_: parent alarm, originating alarm, source alarm

**CorrelatedAlarm**:
An alarm caused by a **RootCauseAlarm**. Carries a `parent_alarm_id` pointing to its root cause. Every alarm has at most one parent (tree structure, not a graph).
_Avoid_: child alarm, dependent alarm, correlated event

### Agent-mode concepts

**HumanMode**:
The API surface under `/alarms` — TMF642-compliant, verbose field names, page/page_size pagination, descriptive error messages. Optimised for developer readability and debugging.
_Avoid_: human profile, human endpoint

**AgentMode**:
The API surface under `/agent/alarms` — compressed field names, cursor pagination, compact error codes, plus agent-native endpoints (delta sync, batch, field selection). Optimised for AI agent consumption.
_Avoid_: agent profile, agent endpoint

**BatchQuery**:
A filter-based request to the agent surface that returns multiple alarms matching a set of criteria (severity, category, state, etc.) in one call. Submitted via `POST /agent/alarms/get-many`. Agents use this to ask "what's critical and raised right now?" without knowing IDs upfront.
_Avoid_: bulk fetch, multi-get, get-many by ID

**DeltaSync**:
A changelog of all alarm changes since a given timestamp — new alarms, any field updates, state transitions, and clearances. Consumed via `GET /agent/alarms/delta?since=<ts>`. Agents use this to stay in sync without full fetches.
_Avoid_: incremental sync, diff, patch feed

## Relationships

- An **Alarm** has exactly one **AlarmCategory**
- An **Alarm** has exactly one **ManagedObject** (the entity it is raised against)
- An **Alarm** has exactly one **AlarmExtension** whose shape is determined by its **AlarmCategory**
- An **AlarmExtension** for `database` category contains zero or more **ImpactedService** references
- A **RootCauseAlarm** has zero or more **CorrelatedAlarms**; a **CorrelatedAlarm** has exactly one **RootCauseAlarm** as parent (tree, not graph)

## Example dialogue

> **Dev:** "We have a network link down in Amsterdam and it's caused 30 alarms to fire. How do we model that?"
> **Domain expert:** "The link failure is a **RootCauseAlarm** with **AlarmCategory** `network`. Its **ManagedObject** is the link, identified by interface and topology element. The 30 downstream alarms are **CorrelatedAlarms** — each carries the `parent_alarm_id` of that root cause."
>
> **Dev:** "One of those is a database alarm. The billing dashboard is down because of it. Where does the dashboard go?"
> **Domain expert:** "The dashboard is an **ImpactedService** on the database alarm's **AlarmExtension** — it comes from the service catalogue with an `id` and a `label`. It does not become a **ManagedObject**; it's what suffers, not what the alarm is raised against."
>
> **Dev:** "The ops team calls critical alarms 'P1'. Should we store P1?"
> **Domain expert:** "No — P1 is a **SeverityLabel**. It gets normalised to **Severity** `critical` at ingestion. Store the canonical value; the label is just for display."
>
> **Dev:** "An Airflow DAG and an n8n workflow both fail at the same time. One alarm or two?"
> **Domain expert:** "Two — one per pipeline run failure. Each is an **Alarm** with **AlarmCategory** `application`, pipeline subtype. The **ManagedObject** of the first is the Airflow DAG; the **ManagedObject** of the second is the n8n workflow. They are independent: different reasons, different run IDs, different on-call owners."

## Future concerns

**Alarm storm** _(not yet designed)_:
A burst of thousands of alarms in a short window, typically triggered by a large network outage. The correlation tree and suppression states partially mitigate this at the domain level. The ingestion architecture will need a message queue (e.g. Kafka) in front of the API to buffer volume — the HTTP endpoint alone cannot absorb this without backpressure. Alarm aggregation (grouping N alarms of the same type on the same segment into one grouped alarm) is a domain-level concept that may also be needed. To be designed when the ingestion layer is scoped.

**Alarm flapping** _(not yet designed)_:
An alarm that repeatedly transitions between `raised` and `cleared` in rapid succession (e.g. a bouncing network link). Distinct from an alarm storm — it is one alarm cycling rather than many alarms firing. Needs flap detection and damping logic. To be designed when the state machine is implemented.

## Flagged ambiguities

- "source" was considered for the entity an alarm is about — resolved: use **ManagedObject** to avoid collision with source system (the monitoring tool that emitted the alarm).
