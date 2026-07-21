# First Prototype Scope

## Purpose

This document fixes the first verifier prototype scope so implementation can start without accidentally growing into live routing, chat delivery, runtime integration, broadcast, or subscription behavior.

## Decision

The first prototype is local-only.

It validates static fixtures in the repository and produces deterministic local verification results. It does not post to chat, spawn agent sessions, call gateway/runtime tools, expose MCP tools, use a queue, or route messages across surfaces.

## Scope Included

The first prototype includes:

- one source agent creating one bus-message envelope for one target agent or target role;
- static JSON envelope fixtures under `tests/fixtures/agent_bus/`;
- static JSON transition fixtures for accepted and rejected state moves;
- deterministic expected JSONL audit-event fixtures;
- validation for required envelope fields;
- validation for supported first-slice interaction types;
- validation for source provenance and target presence;
- validation for delivery expectation presence where a result is required;
- validation for expired messages;
- validation for idempotency-key conflicts within a verifier run or fixture set;
- validation for unsafe external, public, destructive, sensitive, or private-data cases when the authorization context is missing or insufficient;
- state-transition validation for the first-slice state model;
- completion validation that records the declared delivery expectation and result location in local audit events;
- fake stable ids for agents, runtimes, workspaces, credentials, conversations, and requesters.

## Scope Excluded

The first prototype excludes:

- `broadcast`;
- `subscribe`;
- live chat-provider posting;
- real runtime session or agent spawning;
- gateway-mediated routing;
- MCP tool or resource exposure;
- production queue, broker, or pub/sub infrastructure;
- production credential storage or rotation;
- production audit database selection;
- cross-runtime authentication beyond fixture fields required by the envelope;
- admin UI or Agent Hub behavior;
- RedshieldWarden policy-engine integration;
- RedshieldArmor runtime-enforcement integration.

## Prototype Mode

The intended first command remains:

```text
agent-bus verify <fixture-or-directory>
```

The command should:

- read local fixtures;
- validate envelopes and transition sequences;
- emit deterministic local results;
- optionally write scratch output under `tmp/agent-bus/`;
- exit non-zero when fixtures fail verification;
- never perform external actions.

## Interaction Types

The local-only prototype should validate these interaction types:

- `notify`;
- `ask`;
- `instruct`;
- `delegate`;
- `handoff`;
- `consult`;
- `escalate`.

`broadcast` and `subscribe` remain deferred even as schema vocabulary. Fixtures using them should be rejected by the first prototype with stable reason codes such as `interaction_type_deferred`.

## Delivery Expectations

The prototype may model delivery expectations, but only as local data. It must not perform delivery.

Allowed local delivery-expectation values for fixtures:

- `visible_chat_reply`;
- `internal_result`;
- `project_file_update`;
- `ops_report`;
- `followup_bus_message`.

For `visible_chat_reply`, the verifier checks that the envelope declares the target surface and source conversation reference, then records the expected delivery obligation locally. It does not post a message.

## Test Data Boundary

All fixture identities are synthetic. Use fake stable ids such as:

- `agent_source_test`;
- `agent_target_test`;
- `runtime_local_test`;
- `workspace_redshield_test`;
- `project_agent_bus_test`;
- `channel_test_source`;
- `requester_test_user`;
- `credential_local_test`.

Fixtures must not include live Discord ids, real credential ids, secrets, private memory, copied private message bodies, or unrelated project context.

## Acceptance Criteria

This scope decision is complete when:

- the backlog points next at schema work for authorization context and context-package rules;
- the first implementation path remains local-only;
- `broadcast` and `subscribe` are explicitly deferred;
- live routing and delivery adapters remain out of scope until the verifier exists.

Promotion beyond the local-only verifier is controlled by `docs/operations/PROMOTION_GATE.md`.
