# Trusted Live-Adapter Receipt Model

## Purpose

Trusted live-adapter receipts define the evidence a live adapter must return
after an explicitly approved Gate 2 owner-only trial or Gate 3 shared/production
operation.

This model does not approve live behavior. It defines the receipt shape that
must exist before live behavior can be considered.

## Receipt Shape

```json
{
  "schema_version": "liveadapterreceipt.v1",
  "receipt_id": "livereceipt_test_0001",
  "preview_id": "preview_msg_0001",
  "message_id": "msg_0001",
  "correlation_id": "corr_0001",
  "adapter_id": "adapter_discord_live_owner_only_test",
  "adapter_type": "chat",
  "surface": "discord",
  "mode": "live",
  "gate": "gate_2_owner_only_live_trial",
  "approval_event_id": "approval_test_gate2_0001",
  "owner_only_access_verified": true,
  "route_resolution": {
    "schema_version": "targetresolution.v1",
    "resolution_id": "resolution_msg_0001",
    "decision": "resolved"
  },
  "destination": {
    "surface": "discord",
    "conversation_id": "channel_test_source",
    "thread_id": null
  },
  "delivery_expectation": {
    "type": "visible_chat_reply"
  },
  "result": "delivered",
  "reason": "delivered_to_declared_destination",
  "side_effect_performed": true,
  "platform_delivery_ref": "platform-message:test-redacted-0001",
  "adapter_actor": {
    "actor_id": "adapter_actor_discord_test",
    "runtime_id": "runtime_local_test",
    "credential_id": "credential_live_adapter_test",
    "authenticated_at": "2026-07-23T15:30:00Z"
  },
  "evidence_refs": ["evidence:live-receipt:test-0001"],
  "created_at": "2026-07-23T15:30:05Z"
}
```

## Binding Rules

- `mode` must be `live`.
- `gate` must be `gate_2_owner_only_live_trial` or
  `gate_3_shared_or_production`.
- `approval_event_id` must name the explicit approval for the live scope.
- Gate 2 receipts must include `owner_only_access_verified: true`.
- `route_resolution` must be a resolved `targetresolution.v1` object.
- Receipt destination must match the resolved route preview.
- Receipt `message_id` and `correlation_id` must match the route resolution.
- Delivered receipts must include `side_effect_performed: true`.
- Delivered receipts must include a redacted `platform_delivery_ref`.
- Rejected or failed receipts must not claim a side effect.
- Adapter actor evidence must bind actor id, runtime id, credential id, and
  authentication time.
- Evidence references must be references, not raw evidence bodies.

## Stable Rejection Codes

- `live_receipt_missing`
- `live_receipt_field_missing:<field>`
- `live_receipt_schema_unsupported`
- `live_receipt_mode_invalid`
- `live_receipt_gate_unsupported`
- `live_receipt_result_unsupported`
- `approval_event_missing`
- `route_resolution_missing`
- `route_resolution_schema_unsupported`
- `route_resolution_not_resolved`
- `live_receipt_route_binding_failed`
- `live_receipt_destination_mismatch`
- `adapter_actor_missing`
- `adapter_actor_field_missing:<field>`
- `delivered_receipt_missing_side_effect`
- `platform_delivery_ref_missing`
- `rejected_receipt_claims_side_effect`
- `owner_only_access_not_verified`
- `live_receipt_evidence_ref_invalid`
- `live_receipt_contains_raw_private_or_platform_data`

## Evidence Hygiene

Live receipts must not store:

- raw platform responses;
- raw message bodies;
- private memory;
- secrets;
- credential material;
- customer data;
- production runtime ids in public fixtures;
- live channel ids in public fixtures.

Use stable references, hashes, redacted ids, and approved evidence-register
entries instead.

## Local Verification

Run:

```sh
python3 scripts/agent_bus_verify.py live-receipt tests/fixtures/live_receipts --pretty
```
