# Current Alternatives Review

## Purpose

Redshield Agent Bus should not become a new distributed system merely because cross-agent coordination feels awkward. This review compares the available approaches and records the first build-vs-use decision for the initial safe bus-message slice.

## Decision

Build a narrow local `agent-bus` verifier and envelope/state model first. Use existing OpenClaw mechanisms as execution and delivery adapters, not as the source of truth for bus semantics.

The first implementation path is:

- define local bus-message envelopes, validation rules, state transitions, delivery expectations, and audit records in repository-owned code and fixtures;
- keep live routing, broadcast, subscription, and production queue/broker choices deferred;
- integrate native OpenClaw sessions, subagents, chat tools, gateway tools, MCP, or queues later through adapters after the verifier can reject unsafe or ambiguous messages offline.

This is a build decision for the bus semantics, not a build decision for every transport. The first prototype should deliberately avoid live chat posting, external network access, or production runtime routing.

## Alternatives Considered

### Native OpenClaw Sessions And Subagents

Native sessions and subagents already support delegation and multi-agent work. They are the closest existing execution substrate and should be reused for target-agent work once routing is safe.

Strengths:

- already fit the current agent operating model;
- can execute bounded work without inventing a new worker runtime;
- preserve useful session state and tool access;
- support same-machine/local experimentation.

Limitations:

- do not by themselves provide a typed cross-surface message envelope;
- do not make source authorization, privacy classification, delivery expectations, and idempotency explicit enough for Class 4E use;
- can blur the difference between a human command, a summarized instruction, and runtime continuation text unless constrained by a separate verifier;
- are execution sessions, not durable audit records.

Use as: execution adapter after a bus message has passed validation.

Do not use as: the authoritative bus state model or authorization boundary.

### Chat Surfaces, Channels, Threads, And Messages

Chat is the visible place where much OpenClaw work starts and finishes. It is also where delivery failures are most obvious to humans.

Strengths:

- provides human-visible provenance for many requests;
- supports receipts, message ids, channel ids, and thread ids;
- matches the current requirement that substantive Discord answers be visibly posted;
- gives operators a familiar place to spot stuck or privately answered work.

Limitations:

- chat text is not a reliable authorization model;
- forwarded, quoted, summarized, or compacted text can look command-like without being fresh approval;
- channel membership and privacy expectations vary by surface;
- chat history alone is not enough to prove target identity, runtime identity, state transitions, or idempotency.

Use as: source provenance, delivery target, and receipt surface.

Do not use as: the canonical queue, policy engine, or private-context transport.

### Local Project Files And Backlog Records

Project repositories already carry durable requirements, TODOs, decisions, verification scripts, and evidence. They are a good place to build the first offline prototype.

Strengths:

- auditable through ordinary git history;
- easy to review, test, and revert before touching live routing;
- fits the current project workflow and Class 4E evidence discipline;
- avoids external infrastructure while the schema and verifier are still moving.

Limitations:

- not suitable as the long-term production queue for active routing;
- file-based coordination can race or become stale without locking and ownership rules;
- project-local state does not naturally cover cross-workspace or cross-runtime delivery;
- manual git workflows are too slow for runtime message delivery.

Use as: first prototype home, fixtures, design evidence, and local verifier inputs.

Do not use as: the final runtime broker for live multi-agent traffic.

### Runtime Event Routing And Gateway Tools

The runtime and gateway layer can eventually provide controlled ingress, egress, credential checks, and protocol translation.

Strengths:

- sits near the trusted runtime boundary;
- can enforce adapter identity and delivery receipts;
- can integrate with existing OpenClaw routing and tool access;
- is a natural later home for Agent Gateway responsibilities.

Limitations:

- unsafe to wire in before bus-message semantics are testable offline;
- runtime continuation events are explicitly not project work and must not be laundered into instructions;
- gateway behavior alone does not define the product-level envelope, state model, or audit evidence;
- production gateway changes increase blast radius.

Use as: later controlled ingress/egress and adapter layer.

Do not use as: the first place to discover the message model.

### MCP Tools And Resources

MCP can expose bus operations to agents and tools in a structured way.

Strengths:

- provides a well-known tool/resource surface for agents;
- can expose verifier, create-message, claim, transition, and audit lookup operations;
- can keep bus operations explicit rather than free-form chat instructions;
- supports future integration with multiple agent clients.

Limitations:

- MCP is an API surface, not the underlying authorization or state model;
- exposing tools too early can create unsafe production-like behavior around an immature schema;
- still needs authenticated actor context, route policy, idempotency, and delivery checks.

Use as: future API/tool surface over already-defined bus operations.

Do not use as: a substitute for the verifier or policy model.

### General Queues Or Pub/Sub Systems

General-purpose queues and pub/sub systems are useful once the product needs reliable runtime delivery.

Strengths:

- mature delivery, retry, fan-out, and backpressure patterns;
- useful for production operation when message volume and multiple workers appear;
- can support later `broadcast` and `subscribe` behavior better than ad hoc files.

Limitations:

- selecting a broker now would be premature;
- queues move bytes, not authority;
- pub/sub can hide wrong-destination delivery and privacy mistakes behind successful transport;
- production queue operations would require monitoring, retention, incident, backup, and access-control work before Class 4 use.

Use as: future transport candidate after local semantics are validated.

Do not use as: the first prototype or the product decision itself.

## Build-Vs-Use Rationale

The reusable existing parts are execution, surfaces, local project evidence, runtime boundaries, API exposure, and future transport. The missing product value is the typed safety contract between them:

- authenticated actor identity;
- source and requester provenance;
- explicit authorization context;
- privacy classification and context redaction;
- target resolution;
- idempotency;
- state-transition validity;
- delivery expectation and receipt recording;
- audit evidence that does not leak secrets or private memory.

No current alternative provides that full contract. Therefore the first slice should build the contract locally and keep every transport replaceable.

## Consequences

- The next architecture step should compare first buildable paths for implementing the local verifier and storing fixtures/audit records.
- `broadcast` and `subscribe` remain deferred until one-source to one-target semantics are proven.
- Live chat posting, gateway routing, MCP exposure, and queue selection remain out of scope for the first prototype.
- The verifier must reject messages that rely on summarized context, display-name-only identity, ambiguous target claims, wrong-destination delivery, private-data leakage, expired messages, or idempotency conflicts.
- Class 4E artifact backfill remains required, but it should not displace the verifier proof unless the product owner explicitly accepts that risk.

## Selected Next Path

Proceed with a repository-local verifier for sample bus-message envelopes and state transitions. The verifier should use static fixtures first, then later become the policy core behind OpenClaw session/subagent execution and chat-visible delivery adapters.
