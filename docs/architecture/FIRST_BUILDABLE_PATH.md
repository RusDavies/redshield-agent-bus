# First Buildable Architecture Path

## Purpose

This document compares first-build options for Redshield Agent Bus and selects the smallest path that can prove the bus contract before live routing, chat posting, queue infrastructure, or cross-runtime execution is introduced.

## Decision

Build the first slice as a repository-local verifier and fixture-driven architecture.

The selected path is:

1. Define the bus-message envelope, validation rules, state-transition rules, delivery-expectation rules, and audit-record expectations in local source code.
2. Validate static sample envelopes and transition sequences without posting to chat, spawning live sessions, using gateway routing, or selecting a production queue.
3. Produce deterministic verification output suitable for tests and later evidence records.
4. Treat every live execution mechanism as a later adapter around the verifier.

The first buildable path is not direct message-tool handoff, not a durable production queue, not gateway-mediated routing, not session-spawn delegation, and not a project-local inbox workflow. Those are integration paths after the contract is testable.

## Option Review

### Option 1: Direct Message Tool Handoff

Directly use chat/message tools to move a request from one agent or channel to another.

Benefits:

- shortest path to visible cross-agent behavior;
- exercises the surfaces humans already use;
- makes delivery receipts and source-channel reporting concrete.

Problems:

- risks creating side effects before validation rules are proven;
- chat text can accidentally become authorization;
- wrong-channel delivery and private-data leakage would be live failures, not fixture failures;
- does not establish durable idempotency, transition validation, or audit semantics.

Verdict: reject for the first build. Use later as a delivery adapter once verifier rules exist.

### Option 2: Durable Queue Or Pub/Sub

Use a real queue, broker, or pub/sub substrate as the initial bus.

Benefits:

- fits eventual retry, backpressure, delayed work, and fan-out needs;
- supports multiple workers and runtimes later;
- gives operations a familiar production pattern.

Problems:

- premature infrastructure choice;
- queues guarantee movement, not authority or safety;
- introduces retention, monitoring, access-control, and incident burdens before the product contract is stable;
- makes the first prototype larger than the first slice requires.

Verdict: reject for the first build. Keep as a future transport option.

### Option 3: Gateway-Mediated Routing

Put the Agent Gateway in front immediately and route messages through controlled ingress/egress.

Benefits:

- aligns with the future boundary-enforcement role;
- can centralize adapter identity, route checks, and delivery receipts;
- is a plausible production shape.

Problems:

- increases blast radius before offline validation exists;
- encourages runtime integration before the envelope and transition model are stable;
- risks mixing runtime-event handling with project work;
- requires more operational readiness than the first verifier needs.

Verdict: reject for the first build. Use the gateway later as the controlled ingress/egress layer.

### Option 4: Session-Spawn Delegation

Use native OpenClaw sessions or subagents as the first bus-like mechanism.

Benefits:

- reuses existing execution primitives;
- validates that target agents can perform bounded work;
- avoids building worker infrastructure too early.

Problems:

- delegation execution is not the same as bus-message validation;
- sessions do not by themselves prove authorization context, idempotency, or delivery expectation;
- easy to blur fresh human commands with summarized context;
- still leaves the audit/state model underspecified.

Verdict: reject for the first build. Use as the later execution adapter after a message is valid and claimable.

### Option 5: Project-Local Inbox Files

Use repository files as an inbox/outbox for bus messages and completions.

Benefits:

- easy to inspect and review;
- local, auditable, and git-friendly;
- avoids network/runtime dependencies;
- close to the selected verifier path.

Problems:

- an inbox implies operational routing, ownership, and stale-message handling;
- git is not a runtime queue;
- file-level inbox semantics could distract from the contract itself;
- exact fixture and audit-record storage still deserves its own decision.

Verdict: reject as a routing path for the first build. Reuse the local-file idea only for static verifier fixtures and expected-output records.

## Selected Architecture Shape

The first architecture should be a local verifier with four boundaries:

- **Fixture boundary:** sample envelopes and transition scenarios are inputs, not live messages.
- **Validation boundary:** the verifier accepts or rejects envelopes before any target work can start.
- **State boundary:** state transitions are checked as append-only events, not mutated ad hoc status.
- **Adapter boundary:** chat, session-spawn, gateway, MCP, and queue integrations are outside the first slice.

The local verifier should eventually expose one command suitable for CI or local use:

```text
agent-bus verify <fixture-or-directory>
```

That command should report validation failures, state-transition failures, delivery-expectation failures, idempotency conflicts, and audit-record expectations without performing external actions.

## First Implementation Implications

- Start with source-code modules for envelope validation, state-transition validation, and delivery-expectation validation.
- Keep sample data under version control, with no secrets or private memory.
- Add tests around valid interaction types and known invalid cases before introducing adapters.
- Keep `broadcast`, `subscribe`, live chat delivery, gateway routing, MCP exposure, and production queue selection out of scope.
- Use the local fixture and audit-record storage shape selected in `docs/architecture/FIXTURE_AUDIT_STORAGE.md`.
- Treat `docs/operations/PROMOTION_GATE.md` as the gate before any live adapter-backed behavior.

## Acceptance For This Decision

This decision is complete when the backlog points to the local verifier path as the next implementation architecture and the architecture overview no longer implies that a live handoff or queue decision is still the first unresolved architecture step.
