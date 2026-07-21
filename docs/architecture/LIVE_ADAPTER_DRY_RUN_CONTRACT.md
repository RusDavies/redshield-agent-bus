# Live Adapter Dry-Run And Delivery Receipt Contract

## Purpose

Gate 1 requires adapter dry-run behavior before Redshield Agent Bus may perform any live adapter-backed action. This contract defines what a dry-run adapter request looks like, what a dry-run receipt must prove, and what remains forbidden until a later promotion gate.

Dry-run means no external side effect. The adapter boundary is exercised only far enough to validate routing, authorization, destination binding, receipt shape, and audit evidence.

## Non-Negotiable Rule

Dry-run adapters must not post, spawn, send, enqueue, publish, mutate, or call external/runtime services.

Fixture data, envelope data, or command-line flags must not be able to turn a dry-run request into a live action.

## Contract Objects

Gate 1 introduces three local-only contract objects:

- `adapter_capability`: what a dry-run adapter claims it can model.
- `adapter_preview_request`: what the bus asks the adapter to preview.
- `dry_run_delivery_receipt`: what the adapter returns as evidence.

All three are local JSON-compatible objects. They may appear in fixtures, verifier output, or scratch output under `tmp/agent-bus/`.

## Adapter Capability Shape

```json
{
  "schema_version": "adaptercap.v1",
  "adapter_id": "adapter_discord_dry_run_test",
  "adapter_type": "chat",
  "surface": "discord",
  "mode": "dry_run",
  "supports_delivery_expectations": ["visible_chat_reply"],
  "supports_interaction_types": ["notify", "ask", "instruct", "delegate", "handoff", "consult", "escalate"],
  "forbidden_capabilities": ["live_send", "session_spawn", "gateway_call", "queue_publish"],
  "receipt_schema_version": "dryreceipt.v1"
}
```

Rules:

- `mode` must be `dry_run`.
- `forbidden_capabilities` must include every live action the adapter could otherwise be confused with.
- `supports_delivery_expectations` must include the envelope's declared delivery expectation.
- `supports_interaction_types` must include the envelope interaction type.
- Adapter ids are stable identifiers, not display names.

## Preview Request Shape

```json
{
  "schema_version": "adapterpreview.v1",
  "preview_id": "preview_test_0001",
  "message_id": "msg_0001",
  "correlation_id": "corr_0001",
  "idempotency_key": "idem_0001",
  "adapter_id": "adapter_discord_dry_run_test",
  "adapter_type": "chat",
  "surface": "discord",
  "mode": "dry_run",
  "source": {
    "surface": "discord",
    "conversation_id": "channel_test_source",
    "event_id": "event_test_request_0001"
  },
  "destination": {
    "surface": "discord",
    "conversation_id": "channel_test_source",
    "thread_id": null
  },
  "delivery_expectation": {
    "type": "visible_chat_reply"
  },
  "payload_preview": {
    "content_hash": "sha256:test-placeholder",
    "redacted_summary": "Would deliver a status summary."
  },
  "safety": {
    "live_side_effect_allowed": false,
    "external_action_allowed": false,
    "private_data_included": false
  }
}
```

Rules:

- `mode` must be `dry_run`.
- `destination` must match the envelope delivery expectation.
- `source` must match the envelope source provenance.
- `payload_preview` must contain redacted metadata, not raw private content.
- `live_side_effect_allowed` must be `false`.
- The request must include the original `message_id`, `correlation_id`, and `idempotency_key`.

## Dry-Run Receipt Shape

```json
{
  "schema_version": "dryreceipt.v1",
  "receipt_id": "dryreceipt_test_0001",
  "preview_id": "preview_test_0001",
  "message_id": "msg_0001",
  "correlation_id": "corr_0001",
  "adapter_id": "adapter_discord_dry_run_test",
  "adapter_type": "chat",
  "surface": "discord",
  "mode": "dry_run",
  "result": "accepted",
  "reason": "would_deliver",
  "destination": {
    "surface": "discord",
    "conversation_id": "channel_test_source",
    "thread_id": null
  },
  "delivery_expectation": {
    "type": "visible_chat_reply"
  },
  "side_effect_performed": false,
  "payload_hash": "sha256:test-placeholder",
  "created_at": "2026-07-10T22:00:00Z"
}
```

Rules:

- `schema_version` must be `dryreceipt.v1`.
- `mode` must be `dry_run`.
- `side_effect_performed` must be `false`.
- `receipt_id`, `preview_id`, `message_id`, `correlation_id`, `adapter_id`, `surface`, `destination`, and `delivery_expectation` must bind back to the preview request and envelope.
- `result` must be `accepted` or `rejected`.
- Rejected receipts must use a stable reason code.
- Receipts must not include raw private content, secrets, credential material, full chat transcripts, or live platform response bodies.

## Stable Receipt Reason Codes

Accepted:

- `would_deliver`
- `would_record_internal_result`
- `would_record_project_file_update`
- `would_send_followup_bus_message`

Rejected:

- `adapter_capability_missing`
- `adapter_capability_schema_unsupported`
- `adapter_mode_not_dry_run`
- `adapter_identity_missing`
- `adapter_forbidden_capabilities_incomplete`
- `delivery_expectation_unsupported`
- `interaction_type_unsupported`
- `preview_schema_unsupported`
- `preview_binding_failed`
- `preview_adapter_binding_failed`
- `preview_safety_missing`
- `payload_preview_missing`
- `destination_missing`
- `destination_mismatch`
- `source_mismatch`
- `payload_contains_private_data`
- `payload_contains_secret`
- `live_side_effect_requested`
- `receipt_missing`
- `receipt_binding_failed`
- `receipt_claims_side_effect`
- `receipt_schema_unsupported`
- `receipt_result_unsupported`

Reason-code prose can change. Codes should not.

## Validation Requirements

The bus/verifier must reject a dry-run preview or receipt when:

- adapter mode is not `dry_run`;
- adapter identity is missing or display-name-only;
- adapter capability does not support the requested interaction type;
- adapter capability does not support the requested delivery expectation;
- destination does not match the envelope's delivery expectation;
- source does not match the envelope source provenance;
- preview payload includes private data, secrets, credential material, raw chat history, or unrelated context;
- receipt claims `side_effect_performed: true`;
- receipt does not bind to the preview request;
- receipt destination differs from the preview destination;
- receipt schema is unsupported.

## Audit Requirements

Dry-run audit events must record:

- `preview_id`;
- `receipt_id` when available;
- `adapter_id`;
- `adapter_type`;
- `surface`;
- `message_id`;
- `correlation_id`;
- delivery expectation decision;
- destination decision;
- result and reason;
- `side_effect_performed`;
- redaction decisions.

Audit events must not store raw message bodies, private memory, secrets, credential material, or live platform response payloads.

## Required Gate 1 Tests

Before Gate 1 exits, tests must cover:

- accepted visible-chat dry-run receipt;
- unsupported delivery expectation;
- wrong destination;
- missing adapter identity;
- display-name-only adapter identity;
- private-only completion with no valid receipt;
- forged receipt with mismatched `preview_id`;
- forged receipt with mismatched destination;
- receipt claiming `side_effect_performed: true`;
- dry-run preview attempting a live side effect.

## Deferred

Deferred until later gates:

- live Discord posting;
- live session/subagent spawning;
- gateway/runtime calls;
- MCP exposure;
- queue publishing;
- production receipt persistence;
- live platform receipt normalization;
- customer-facing delivery evidence export.
