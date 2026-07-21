# Open-Core Armor Enforcement Contract

## Purpose

The open-core Armor contract lets Agent Bus consume enforcement decisions
without requiring a deployed or private RedshieldArmor runtime guard. It is a
local fixture contract for baseline checks only.

The contract answers one question: should the requested payload, adapter
preview, context package, or tool dispatch continue, be blocked, be sanitized,
or require review?

## Decision Values

Supported decisions:

- `allow`: the request may continue with receipt/evidence requirements.
- `block`: the request must fail closed.
- `sanitize`: the request may continue only after named fields are removed,
  redacted, or replaced.
- `require_review`: the request needs review or approval before it can
  continue.

## Enforcement Check Request

```json
{
  "schema_version": "redshield_armor.enforcement_check_request.v1",
  "request_id": "armor_request_allow_test_0001",
  "message_id": "msg_0001",
  "correlation_id": "corr_0001",
  "enforcement_target": "adapter_delivery_preview",
  "action_class": "compose_response",
  "payload_ref": "payload:test:metadata-only",
  "adapter_capability_ref": "adapter-capability:visible-chat-reply:test",
  "safety_flags": {
    "private_data": false,
    "secret_data": false,
    "external_action": false,
    "destructive_action": false
  }
}
```

## Enforcement Result

```json
{
  "schema_version": "redshield_armor.enforcement_result.v1",
  "enforcement_id": "armor_enforcement_allow_test_0001",
  "decision": "allow",
  "enforcement_target": "adapter_delivery_preview",
  "finding_codes": ["payload_metadata_only"],
  "adapter_capability_refs": ["adapter-capability:visible-chat-reply:test"],
  "sanitized_field_refs": [],
  "receipt_requirements": ["delivery_attempt_id"],
  "evidence_refs": ["evidence:armor:test-allow-0001"],
  "applies_to": {
    "request_id": "armor_request_allow_test_0001",
    "message_id": "msg_0001",
    "correlation_id": "corr_0001",
    "enforcement_target": "adapter_delivery_preview",
    "action_class": "compose_response",
    "payload_ref": "payload:test:metadata-only",
    "adapter_capability_ref": "adapter-capability:visible-chat-reply:test"
  },
  "evidence": {
    "privacy_classification": "internal",
    "content_hash": "sha256:test-allow"
  },
  "evaluated_at": "2026-07-20T21:20:00Z"
}
```

## Rules

- `applies_to` must bind back to request id, message id, correlation id,
  enforcement target, action class, payload reference, and adapter capability
  reference.
- `allow` must not name sanitized fields.
- `block` must not name receipt requirements.
- `sanitize` must name the sanitized field references.
- `require_review` must name at least one receipt or review requirement.
- Enforcement evidence must use references and hashes. It must not embed private
  memory, secrets, raw chat transcripts, credential material, or customer data.

## Local Verification

Run:

```sh
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 7
}
```
