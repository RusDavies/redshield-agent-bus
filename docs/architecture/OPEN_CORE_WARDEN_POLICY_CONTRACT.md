# Open-Core Warden Policy Contract

## Purpose

The open-core Warden contract lets Agent Bus consume policy decisions without
requiring a deployed or private RedshieldWarden service. It is a local fixture
contract for baseline decisions only.

The contract answers one question: should the requested bus action continue,
fail closed, or require human review?

## Decision Values

Supported decisions:

- `allow`: the request satisfies the baseline policy contract.
- `deny`: the request must fail closed.
- `require_review`: the request needs a named approver role before it can
  continue.

Decision prose can change. Decision values and reason codes should remain
stable once fixtures depend on them.

## Policy Check Request

```json
{
  "schema_version": "redshield_warden.policy_check_request.v1",
  "request_id": "warden_request_allow_test_0001",
  "message_id": "msg_0001",
  "correlation_id": "corr_0001",
  "action_class": "compose_response",
  "actor_id": "agent_target_test",
  "target": {
    "target_agent_id": "agent_target_test",
    "target_role": null
  },
  "delivery_expectation": {
    "type": "visible_chat_reply",
    "surface": "discord",
    "conversation_id": "channel_test_source"
  },
  "safety_flags": {
    "external_action": false,
    "public_action": false,
    "destructive_action": false,
    "private_data": false
  }
}
```

## Policy Result

```json
{
  "schema_version": "redshield_warden.policy_result.v1",
  "decision_id": "warden_decision_allow_test_0001",
  "decision": "allow",
  "reason_codes": ["action_class_allowed"],
  "risk_class": "low",
  "policy_refs": ["policy:open-core:local-safe-notify"],
  "required_approver_roles": [],
  "evidence_refs": ["evidence:warden:test-allow-0001"],
  "applies_to": {
    "request_id": "warden_request_allow_test_0001",
    "message_id": "msg_0001",
    "correlation_id": "corr_0001",
    "action_class": "compose_response",
    "actor_id": "agent_target_test",
    "target": {
      "target_agent_id": "agent_target_test",
      "target_role": null
    },
    "delivery_expectation": {
      "type": "visible_chat_reply",
      "surface": "discord",
      "conversation_id": "channel_test_source"
    }
  },
  "evidence": {
    "privacy_classification": "internal",
    "content_hash": "sha256:test-allow"
  },
  "evaluated_at": "2026-07-20T21:10:00Z"
}
```

## Rules

- `applies_to` must bind back to request id, message id, correlation id,
  action class, actor, target, and delivery expectation.
- `allow` must not name required approver roles.
- `require_review` must name at least one required approver role.
- `deny` and `require_review` are fail-closed results until the caller records
  appropriate review or stops the work.
- Policy results must use references and hashes for evidence. They must not
  embed private memory, secrets, raw chat transcripts, credential material, or
  customer data.

## Local Verification

Run:

```sh
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 6
}
```
