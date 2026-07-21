# Fixture And Audit Storage Decision

## Purpose

The first verifier prototype needs local sample inputs and expected audit outputs before it can safely reject bad bus messages. This decision defines where those files live, what formats they use, and what must stay out of the repository.

## Decision

Use versioned JSON fixtures under `tests/fixtures/agent_bus/` and deterministic JSON Lines audit-event expectations under the same fixture tree.

Generated verifier output may be written to `tmp/` during local runs, but only curated fixtures and expected outputs belong in git.

## Repository Layout

The first verifier should use this layout:

```text
tests/
  fixtures/
    agent_bus/
      envelopes/
        valid/
        invalid/
      transitions/
        valid/
        invalid/
      expected_audit_events/
```

Use these roles:

- `envelopes/valid/`: one complete accepted envelope per fixture.
- `envelopes/invalid/`: one rejected envelope per fixture, with the expected rejection reason encoded in the fixture.
- `transitions/valid/`: valid state-transition sequences for an accepted message.
- `transitions/invalid/`: rejected transition sequences, including actorless transitions and invalid state moves.
- `expected_audit_events/`: JSONL files containing normalized expected audit events for the corresponding envelope or transition fixture.

Use `tmp/agent-bus/` only for scratch verifier output during local runs. `tmp/` is already ignored by git.

## Fixture Format

Use strict JSON for first-slice fixtures.

Reasons:

- Python can parse it with the standard library;
- the data model is explicit enough for validation tests;
- fixtures can be reused later by MCP tools, gateway adapters, or other language implementations;
- JSON avoids YAML conveniences that can hide type mistakes.

Each envelope fixture should be one JSON object with these top-level fields:

- `case_id`: stable fixture id.
- `description`: short human-readable purpose.
- `expect`: expected verifier outcome.
- `envelope`: the bus-message envelope under test.

Example shape:

```json
{
  "case_id": "valid-notify-minimal",
  "description": "Accepted notify message with source provenance and visible delivery expectation.",
  "expect": {
    "valid": true,
    "errors": []
  },
  "envelope": {
    "message_id": "msg_0001",
    "correlation_id": "corr_0001",
    "idempotency_key": "idem_0001"
  }
}
```

Invalid fixtures should keep the malformed or unsafe payload visible and put the expected failure in `expect.errors`.

## Transition Fixture Format

Transition fixtures should also be JSON objects:

- `case_id`: stable fixture id.
- `description`: short human-readable purpose.
- `initial_state`: starting message state.
- `events`: ordered transition attempts.
- `expect`: final expected result, including accepted and rejected transitions.

State-transition fixtures are input to the verifier, not authoritative audit logs. They describe what the verifier should accept or reject.

## Audit Event Format

Expected audit events should use JSON Lines: one normalized event object per line.

Use JSONL because audit records are append-only events, and line-delimited records make event order and append behavior obvious without pretending the first prototype has a production database.

Each expected audit event should include:

- `case_id`: fixture id that produced the event.
- `event_type`: `validation`, `state_transition`, `delivery_expectation`, `idempotency`, or `audit_check`.
- `message_id`: message id when available.
- `correlation_id`: correlation id when available.
- `actor_id`: authenticated actor id when available.
- `actor_type`: actor type when available.
- `result`: `accepted` or `rejected`.
- `reason`: stable machine-readable reason, especially for rejections.
- `state_before`: previous state for transition events.
- `state_after`: next state for accepted transition events.
- `delivery_expectation_id`: delivery expectation id when relevant.
- `redactions`: list of redaction decisions made by the verifier.
- `source_fixture`: relative fixture path.

Verifier tests should compare normalized expected events, not wall-clock timestamps, random ids, or host-local paths.

## Data Hygiene Rules

Fixtures must not contain:

- secrets, tokens, API keys, cookies, or credentials;
- private memory;
- unrelated chat history;
- real personal data unless the fixture is explicitly public/test-safe;
- live Discord channel ids except deliberately fake ids;
- production runtime ids or credential ids;
- copied private message bodies.

Use stable fake ids such as `agent_skippy_test`, `runtime_local_test`, `workspace_redshield_test`, `channel_test_source`, and `credential_local_test`.

## Determinism Rules

The verifier should normalize or inject deterministic values during tests:

- timestamps use fixed fixture values;
- hashes are computed from canonical JSON;
- generated ids are fixture-provided;
- object key order is irrelevant;
- audit comparisons use stable reason codes, not prose strings.

## Open Questions Deferred

These are intentionally not decided here:

- production audit storage;
- runtime queue or broker selection;
- live delivery receipt storage;
- cross-runtime credential registry storage;
- evidence-register integration for Class 4E reporting.

Those decisions belong after the local verifier proves the envelope, transition, delivery, and audit semantics.
