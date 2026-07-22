# Agent Operation Boundaries

## Purpose

These boundaries define what agents may do through Redshield Agent Bus as the
project moves toward Class 4E use. They prevent a verified bus envelope from
being mistaken for permission to perform arbitrary work.

This document is public-safe and implementation-agnostic. It does not approve
live adapters, production use, public release, customer-facing security claims,
or enterprise operations.

## Boundary Model

Every bus operation must be bounded by:

- authenticated actor and runtime identity;
- concrete source event or approval event;
- target agent, role, project, workspace, and surface;
- allowed interaction type;
- allowed action classes;
- allowed context references;
- delivery expectation;
- expiry and idempotency key;
- Warden policy result where policy is required;
- Armor enforcement result where payload or action enforcement is required.

If any boundary is missing, ambiguous, stale, or wider than the source approval,
the bus must fail closed.

## Operation Classes

### Class A: Local Verification

Allowed:

- read versioned fixtures;
- validate envelopes, transitions, dry-run previews, receipts, Warden results,
  Armor results, credential-provider responses, and capability grants;
- run local tests and repository-profile checks;
- write local scratch output that contains no secrets or private message bodies.

Forbidden:

- live delivery;
- runtime, gateway, or agent-session calls;
- external/public/destructive actions;
- production queue, database, or broker access;
- private-memory transfer.

### Class B: Project-Local Work

Allowed only with a concrete source event and matching authorization context:

- read public-safe or project-authorized files;
- edit scoped project files;
- run local tests and verification commands;
- create commits in the scoped repository;
- report results to the declared source surface.

Required controls:

- verify repository top-level before git operations;
- keep unrelated files out of the change;
- preserve public/private repository boundaries;
- record verification results;
- deliver visible completion or failure to the declared source surface.

### Class C: Dry-Run Adapter Modeling

Allowed:

- create adapter previews;
- validate synthetic target resolution;
- produce dry-run receipts;
- record redacted metadata for what would have happened.

Forbidden:

- live posting;
- live session spawning;
- gateway or runtime side effects;
- external API calls;
- queue publication;
- claims that delivery occurred.

### Class D: Owner-Only Live Trial

Allowed only after Gate 2 approval:

- one-source to one-target live delivery in a verified owner-only context;
- explicitly approved session or subagent spawning in an owner-controlled
  runtime;
- adapter receipts that bind source, destination, actor, preview, and result;
- fail-closed recovery reporting to the source or ops context.

Required approval must name:

- adapter or runtime;
- source and destination surfaces;
- allowed interaction types;
- allowed action classes;
- scope and duration;
- rollback or disable path;
- evidence to retain.

### Class E: Shared Or Production Use

Allowed only after Gate 3 approval and Class 4 production-readiness evidence.

Required before use:

- satisfied production readiness gates in
  `docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md`;
- operations runbook for start, stop, disable, logs, receipt inspection,
  incident response, rollback, and recovery;
- risk, control, evidence, and policy registers;
- monitoring and stuck-work detection;
- audit retention and data-minimization policy;
- human approval for the shared or production scope.

Enterprise or customer-facing use also requires Class 4E evidence support and
approved customer-facing security posture.

## Human Approval Boundaries

The bus must require explicit human approval for:

- external or public actions;
- destructive actions;
- access to private memory or private context;
- customer-impacting work;
- production infrastructure changes;
- live adapter promotion;
- release publication or repository visibility changes;
- enterprise/compliance claims.

Approval must come from a concrete source event or policy reference. Summaries,
continuation notes, inferred intent, copied chat history, or stale approvals are
not authorization.

## Context And Data Boundaries

Agents must use scoped references by default. They must not copy raw private
message bodies, secrets, private memory, customer data, production runtime ids,
or live channel ids into fixtures, audit records, public docs, or cross-agent
context packages.

When context must cross a boundary:

- prefer references, hashes, and redacted summaries;
- include only the minimum needed fields;
- preserve source project/workspace ownership;
- mark private or sensitive references explicitly;
- reject the operation when redaction is ambiguous.

## Delivery Boundaries

Every chat-visible request must declare a visible delivery expectation. A
private completion does not satisfy a visible source request.

Receipts must bind:

- source event;
- destination surface and conversation;
- adapter identity;
- actor identity;
- preview or request id;
- delivery result;
- timestamp.

Wrong-destination delivery, missing receipts, forged receipts, or private-only
completion must fail closed.

## Runtime-Event Boundary

Runtime-event continuation text is operational incident material, not ordinary
project authorization. It must route to the incident or recovery path rather
than becoming project work.

The bus must reject runtime-event operations unless:

- the action class includes `runtime_event_action`;
- the matching safety authorization is true;
- the basis is an approved operator action, standing policy, or system rule;
- the destination is an approved incident or recovery context.

## Audit Evidence

Audit evidence must record decisions and references, not raw secrets or private
content.

Required evidence:

- actor and runtime identity;
- source and approval event references;
- authorization result and reason;
- Warden policy result reference when applicable;
- Armor enforcement result reference when applicable;
- delivery receipt or failure reason;
- idempotency key and expiry decision;
- rollback or disable reference for live operations.

## Fail-Closed Triggers

Stop or reject the operation when:

- actor, runtime, source, target, or authorization cannot be verified;
- scope or destination is ambiguous;
- requested action class exceeds authorization;
- approval is missing, stale, summarized, or inferred;
- context contains private data without explicit matching authorization;
- Warden or Armor evidence is required but missing;
- receipt binding fails;
- rollback or disable path is missing for live behavior;
- the operation crosses into public release, production, enterprise, customer,
  external, or destructive territory without explicit approval.
