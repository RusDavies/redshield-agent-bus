# Local Verifier To Live Adapter Promotion Gate

## Purpose

This gate defines when Redshield Agent Bus may move from the local-only verifier to any live adapter-backed behavior. It prevents a working fixture verifier from being mistaken for permission to post messages, spawn sessions, route work, or touch runtime infrastructure.

## Decision

Promotion is staged. The local verifier must pass through explicit gates before any live adapter is allowed.

Stages:

- Gate 0: local verifier only.
- Gate 1: adapter dry-run.
- Gate 2: owner-only live adapter trial.
- Gate 3: shared or production use.

No stage automatically promotes to the next one. Each promotion needs recorded evidence and human approval.

## Gate 0: Local Verifier Only

Current state.

Allowed:

- read versioned fixtures;
- validate envelopes and transitions;
- emit deterministic local JSON results;
- write scratch output under `tmp/agent-bus/`;
- run local tests and scaffold checks.

Forbidden:

- live chat posting;
- OpenClaw session or subagent spawning;
- gateway/runtime calls;
- MCP tool/resource exposure;
- queue, pub/sub, or broker use;
- `broadcast` or `subscribe`;
- external/public/destructive actions.

Exit criteria for Gate 0:

- verifier command exists and runs locally;
- valid and invalid fixtures cover first-slice envelope and state-transition behavior;
- authorization-context and context-package rules are enforced by fixtures/tests;
- idempotency, expiry, wrong-destination delivery, runtime-event misuse, and private-data leakage cases are covered;
- tests are deterministic and require no network or production runtime access;
- threat-model open findings for the first verifier are either mitigated by tests or tracked as explicit backlog.

## Gate 1: Adapter Dry-Run

Adapter dry-run means a live adapter boundary is modeled, but no external side effect is performed.

Allowed:

- construct adapter request previews;
- resolve target adapter identity from synthetic or local configuration;
- validate delivery expectations against adapter capabilities;
- produce dry-run delivery receipts;
- record what would have been sent or spawned as redacted metadata;
- fail closed when target or authorization is ambiguous.

Forbidden:

- posting to Discord or any other chat;
- spawning real agent sessions;
- sending gateway/runtime commands;
- calling external APIs;
- creating real queue messages;
- storing secrets in dry-run output.

Entry criteria from Gate 0:

- all Gate 0 exit criteria are met;
- local runtime credential format is selected;
- delivery adapter dry-run and receipt contract is documented in `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md`;
- adapter dry-run has tests for wrong destination, private-only completion, missing receipt, and forged receipt;
- rollback/disable procedure is documented at least for dry-run configuration;
- human approval is recorded for the dry-run experiment.

Exit criteria for Gate 1:

- dry-run results are deterministic and auditable;
- dry-run receipts bind adapter identity, target surface, source conversation, and delivery expectation;
- dry-run cannot be switched to live behavior by fixture data alone;
- operations notes explain how to identify and disable the adapter path;
- threat model is reviewed against the dry-run adapter boundary.

## Gate 2: Owner-Only Live Adapter Trial

Owner-only live adapter trial means the bus may perform limited live behavior only in a controlled owner-only context.

Allowed:

- one-source to one-target messages;
- explicitly approved live chat-visible delivery in an owner-only or otherwise verified-private surface;
- explicitly approved session/subagent spawning in an owner-controlled runtime;
- delivery receipts recorded by adapter identity;
- fail-closed recovery reporting to the source context or ops context.

Forbidden:

- shared-channel use without approval;
- production infrastructure use;
- public or external posting;
- destructive actions;
- private-memory transfer;
- `broadcast`;
- `subscribe`;
- enterprise/customer-facing claims;
- operation without a rollback/disable path.

Entry criteria from Gate 1:

- all Gate 1 exit criteria are met;
- owner-only access can be verified before live action;
- operations runbook has start, stop, disable, log, receipt, and incident paths for the adapter;
- agent-operation boundaries are documented in
  `docs/operations/AGENT_OPERATION_BOUNDARIES.md`;
- release checklist has been updated for the live trial;
- threat model is reviewed and the relevant mitigations are linked to tests or accepted risk;
- human approval explicitly names the live adapter, surface, scope, and duration.

Exit criteria for Gate 2:

- live trial delivers only to the declared destination;
- delivery receipts are captured and auditable;
- private-only completion and wrong-destination paths visibly fail closed;
- rollback/disable procedure has been tested;
- no unapproved external/public/destructive behavior occurred;
- post-trial review records findings and next risk decisions.

## Gate 3: Shared Or Production Use

Shared or production use is not authorized by the first local verifier.

Entry criteria from Gate 2:

- all Gate 2 exit criteria are met;
- Class 4 production-readiness gates are defined and satisfied;
- agent-operation boundaries in
  `docs/operations/AGENT_OPERATION_BOUNDARIES.md` are satisfied;
- risk, control, evidence, and policy registers exist;
- release security gate is defined;
- operations runbook is usable for production-like incidents;
- monitoring, audit retention, rollback, and backup/restore expectations are documented where applicable;
- human approval explicitly authorizes shared or production use.

Enterprise or customer-facing use also requires Class 4E evidence support and approved customer-facing security posture. No sticker, no claim. Humanity may survive the disappointment.

## Promotion Evidence

Every promotion request must record:

- source commit;
- verifier command and result;
- test command and result;
- adapter or runtime boundary being promoted;
- allowed surfaces and destinations;
- denied actions and out-of-scope behavior;
- rollback/disable procedure;
- threat-model review status;
- open risks and accepted-risk owner;
- human approval event.

## Fail-Closed Rules

The system must stay at the current gate or move backward when:

- verifier or adapter tests fail;
- target resolution is ambiguous;
- delivery destination cannot be verified;
- receipt binding fails;
- private data appears in a context package or audit event;
- summarized context is used as authorization;
- runtime-event continuation text appears in ordinary project flow;
- rollback or disable procedure is missing;
- human approval is missing, stale, or ambiguous.

## Backlog Implications

Before Gate 1:

- decide the first local runtime credential format;
- define the live-adapter dry-run and receipt contract;
- add implementation tests for verifier behavior;
- review and approve the initial threat model against implemented mitigations.

Before Gate 2:

- document agent-operation boundaries;
- update the operations runbook for the specific live adapter;
- document rollback/disable procedure;
- record human approval for the trial.

Before Gate 3:

- satisfy Class 4 production-readiness requirements;
- complete the relevant Class 4E evidence and control artifacts before enterprise/customer-facing use.
