# Shared-Use Controls

## Purpose

Shared-use controls define the minimum rate-limit, quota, claim authorization,
and stale-work monitoring profile required before Redshield Agent Bus can move
toward shared or production use.

This is a local verifier contract. It does not approve live adapters,
production queues, public release, enterprise claims, or customer-impacting
operation.

## Control Areas

- Rate limits prevent one actor, runtime, workspace, project, target, or source
  surface from flooding the bus.
- Quotas cap daily message volume, daily claim volume, and in-flight claims.
- Claim authorization requires actor-bound claims and forbids display-name-only
  claims or actorless transitions.
- Stale-work monitoring requires pending-age, claimed-age, missing-receipt, and
  wrong-destination detection with an alert destination.

## Profile Shape

```json
{
  "schema_version": "shareduse.v1",
  "profile_id": "shareduse_local_test_0001",
  "scope": {
    "mode": "shared",
    "workspace_id": "workspace_redshield_test",
    "project_slug": "project_agent_bus_test"
  },
  "rate_limits": [
    {
      "name": "per_actor_burst",
      "scope": "actor",
      "window_seconds": 60,
      "max_messages": 20
    }
  ],
  "quota_limits": {
    "daily_message_limit": 2500,
    "daily_claim_limit": 1000,
    "max_inflight_claims": 25
  },
  "claim_authorization": {
    "require_actor_binding": true,
    "allowed_claim_modes": ["exact_agent", "role_with_runtime_allowlist"],
    "allow_display_name_claims": false,
    "allow_actorless_transitions": false
  },
  "stale_work_monitoring": {
    "pending_age_threshold_seconds": 900,
    "claimed_age_threshold_seconds": 1800,
    "alert_destination_ref": "ops-channel:redshield-agent-bus-test",
    "missing_receipt_detection": true,
    "wrong_destination_detection": true
  },
  "evidence_refs": ["evidence:shared-use:test-profile-0001"]
}
```

## Stable Rejection Codes

- `shared_use_profile_missing`
- `shared_use_field_missing:<field>`
- `shared_use_schema_unsupported`
- `shared_use_scope_mode_unsupported`
- `shared_use_scope_missing`
- `rate_limits_missing`
- `rate_limit_invalid`
- `rate_limit_name_invalid`
- `rate_limit_scope_unsupported`
- `rate_limit_value_invalid`
- `quota_limits_missing`
- `quota_limit_invalid:<field>`
- `claim_authorization_missing`
- `claim_actor_binding_required`
- `claim_modes_missing`
- `claim_mode_unsupported`
- `display_name_claims_forbidden`
- `actorless_transitions_forbidden`
- `stale_work_monitoring_missing`
- `stale_work_threshold_invalid:<field>`
- `stale_work_alert_destination_missing`
- `missing_receipt_detection_required`
- `wrong_destination_detection_required`
- `shared_use_evidence_ref_invalid`

## Gate Requirements

Before Gate 3 shared or production use, there must be evidence that:

- each deployed/shared scope has a `shareduse.v1` profile;
- rate limits and quotas are enforced or explicitly fail closed;
- claims bind to authenticated actor and runtime identity;
- display-name-only claims are rejected;
- actorless transitions are rejected;
- stale pending and claimed work emit alerts;
- missing receipts emit alerts;
- wrong-destination detection emits alerts;
- operational responders know where alerts arrive and how to disable the shared path.

## Local Verification

Run:

```sh
python3 scripts/agent_bus_verify.py shared-use tests/fixtures/shared_use --pretty
```
