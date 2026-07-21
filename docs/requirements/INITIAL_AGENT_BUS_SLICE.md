# Initial Agent-Bus Messaging Slice

## Purpose

Define the first buildable slice for Redshield Agent Bus: safe typed message exchange between agent participants across chat conversations, workspaces, runtimes, and project contexts.

This slice is intentionally not a full workflow engine, message broker, policy engine, or admin console. It establishes the message envelope, state model, validation rules, and delivery expectations needed before live routing is wired in.

## Scope

The first slice supports one source agent creating one bus message for one target agent or agent role, with optional follow-up completion status back to the source context.

The first prototype scope is defined in `docs/requirements/FIRST_PROTOTYPE_SCOPE.md`. It is local-only: static fixtures in, deterministic verification results out, with no live chat posting, runtime routing, session spawning, MCP exposure, queue infrastructure, `broadcast`, or `subscribe`.

Included interaction types:

- `notify`: information delivery, no response required.
- `ask`: request for information, judgement, or clarification.
- `instruct`: bounded work request under an authorization context.
- `delegate`: task assignment while source ownership remains visible.
- `handoff`: ownership or status transfer for in-flight work.
- `consult`: non-owning request for another agent's view.
- `escalate`: route to ops, security, or human approval.

Deferred interaction types:

- `broadcast`: fan-out to multiple targets.
- `subscribe`: long-running event/status subscription.

## Required Message Envelope

Every bus message must include:

- `message_id`: unique immutable id.
- `correlation_id`: id tying related messages, replies, and completion records together.
- `idempotency_key`: duplicate guard for retries and side effects.
- `interaction_type`: one of the supported interaction types.
- `created_at`: timestamp from the trusted service.
- `expires_at`: expiry after which work must not start without renewal.
- `source`: surface, conversation/workspace id, message id when available, project slug when applicable, and source agent id.
- `target`: target agent id, role, workspace, project slug, or routing selector.
- `requester`: human or system principal that initiated the work, when known.
- `authorization_context`: approvals, limits, and actions explicitly allowed by the originating request, following `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`.
- `delivery_expectation`: where the result or status must be delivered.
- `context_package`: scoped summary, references, file paths, source ids, and known constraints, following `docs/security/CONTEXT_PACKAGE_RULES.md`.
- `privacy_classification`: public/shared/internal/private/sensitive marker.
- `safety_flags`: external action, destructive action, private data, runtime-event boundary, security-sensitive, or approval-required markers.
- `requested_output`: expected response shape, artifact, or action.

## Required State Model

The first slice must support:

- `created`: accepted by the bus but not yet routable.
- `queued`: validated and waiting for a target.
- `claimed`: target agent/runtime has accepted responsibility.
- `in_progress`: target work has started.
- `needs_input`: target cannot continue without extra information or approval.
- `completed`: target produced a result and delivery obligations were recorded.
- `failed`: work ended unsuccessfully with reason and recovery guidance.
- `expired`: message was not claimed or completed in time.
- `cancelled`: source or authorized operator cancelled the message.
- `rejected`: message failed validation or policy checks before execution.

State transitions must be append-only in the audit log.

## Validation Rules

The bus must reject messages that:

- lack source provenance;
- lack a target or have an ambiguous target;
- lack an interaction type;
- request external, public, destructive, or sensitive actions without matching authorization context;
- cite summarized context, forwarded text, continuation notes, or inferred intent as authorization;
- include private memory, secrets, raw chat history, or unrelated project context without an explicit safe basis and matching context-package allowlist;
- have no delivery expectation for interactions that require a result;
- have an expired `expires_at`;
- reuse an idempotency key with incompatible payload;
- try to treat runtime-event continuation text as ordinary project work.

## Delivery Expectations

Each message must declare one result path:

- visible reply to the source chat conversation;
- internal/private result only;
- project-file update;
- ops conversation report;
- follow-up bus message to the source agent.

For chat-visible results, completion must record the target surface and delivery id when available.

Dry-run adapter previews and receipts for future Gate 1 work are defined in `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md`.

## Minimum Audit Record

Each accepted or rejected message must record:

- envelope hash;
- validation result;
- state transitions;
- actor for each transition;
- timestamps;
- delivery receipt or failure reason;
- redaction/safety decisions;
- linked project files or generated artifacts, if any.

The audit record must avoid storing secrets or unnecessary private content.

## First Prototype Acceptance Criteria

- A local verifier validates sample bus-message envelopes.
- Valid samples cover `notify`, `ask`, `instruct`, `delegate`, `handoff`, `consult`, and `escalate`.
- Invalid samples cover missing provenance, ambiguous target, unsafe external action, private-data leakage, expired message, and idempotency conflict.
- State transitions reject invalid moves.
- Completion records the declared delivery expectation and result location.
- Verification runs without live chat, external network, or production runtime routing.

## Out Of Scope For First Slice

- Multi-target broadcast fan-out.
- Long-running subscriptions.
- Live chat posting.
- Cross-runtime authentication design beyond the fields needed in the envelope.
- Full RedshieldWarden policy engine integration.
- Full RedshieldArmor enforcement integration.
- Admin UI / Agent Hub.
- Production queue, broker, or database selection.
