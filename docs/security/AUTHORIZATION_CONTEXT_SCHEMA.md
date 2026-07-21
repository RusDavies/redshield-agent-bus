# Authorization Context Schema

## Purpose

Authorization context tells the verifier what the authenticated actor is allowed to request and what the target may do. It is separate from authentication: authentication proves who is speaking; authorization context proves what authority was actually granted.

This schema is for the first local-only verifier prototype. It is not a production policy engine and does not replace future RedshieldWarden or RedshieldArmor integrations.

## Design Goals

- Preserve the concrete source event that granted authority.
- Prevent summarized context, forwarded text, continuation notes, or inferred intent from becoming approval.
- Fail closed for external, public, destructive, sensitive, customer-impacting, or private-data actions.
- Keep authorization explicit enough for fixtures, tests, audit events, and future policy hooks.
- Avoid storing private message bodies, secrets, or unnecessary context in authorization records.

## Envelope Placement

Every verifier fixture envelope must include:

```json
{
  "authorization_context": {
    "schema_version": "authzctx.v1",
    "authorization_id": "authz_test_0001"
  }
}
```

The verifier must reject envelopes with a missing `authorization_context`, missing `schema_version`, unsupported `schema_version`, or missing `authorization_id`.

## Required Fields

The first-slice authorization context object requires:

- `schema_version`: currently `authzctx.v1`.
- `authorization_id`: stable id for the authorization context.
- `requester_id`: stable human or system requester id when known.
- `source_event_ids`: concrete source events that created or approved the request.
- `basis`: why the work is authorized.
- `scope`: workspace, project, surface, and target boundaries.
- `allowed_interaction_types`: interaction types allowed by this context.
- `allowed_action_classes`: action classes allowed by this context.
- `safety_authorizations`: explicit approvals for risky classes.
- `constraints`: limits that narrow the work.
- `expires_at`: timestamp after which authority is stale.

## Field Shape

Example shape:

```json
{
  "schema_version": "authzctx.v1",
  "authorization_id": "authz_test_notify_0001",
  "requester_id": "requester_test_user",
  "source_event_ids": ["event_test_request_0001"],
  "basis": {
    "kind": "direct_request",
    "approval_event_ids": [],
    "summary_is_authorization": false
  },
  "scope": {
    "workspace_id": "workspace_redshield_test",
    "project_slug": "project_agent_bus_test",
    "source_surface": "discord",
    "source_conversation_id": "channel_test_source",
    "target_agent_ids": ["agent_target_test"],
    "target_roles": []
  },
  "allowed_interaction_types": ["notify"],
  "allowed_action_classes": ["read_context", "compose_response"],
  "safety_authorizations": {
    "external_action": false,
    "public_action": false,
    "destructive_action": false,
    "sensitive_data": false,
    "private_data": false,
    "runtime_event": false,
    "customer_impacting": false
  },
  "constraints": {
    "max_duration_seconds": 300,
    "allowed_delivery_expectations": ["visible_chat_reply"],
    "allowed_context_reference_types": ["project_file", "source_event"],
    "allowed_paths": [],
    "denied_paths": [],
    "requires_human_confirmation": false
  },
  "expires_at": "2026-07-10T19:30:00Z"
}
```

## Basis Rules

`basis.kind` must be one of:

- `direct_request`: the source event itself grants the work.
- `explicit_approval`: a concrete approval event grants a risky action.
- `standing_policy`: a future configured policy grants the work.
- `operator_action`: an authenticated operator grants or performs the work.
- `system_rule`: a trusted system rule grants non-human operational work.

First prototype support:

- accept `direct_request` for ordinary safe fixtures;
- accept `explicit_approval` only when `approval_event_ids` is non-empty;
- reject `standing_policy`, `operator_action`, and `system_rule` unless a fixture explicitly marks them as unsupported/deferred test cases.

`summary_is_authorization` must be `false`. If it is missing or `true`, reject with `summarized_context_not_authorization`.

## Allowed Action Classes

Use these first-slice action classes:

- `read_context`: inspect allowed fixture/project references.
- `compose_response`: draft or produce a local result.
- `update_project_file`: modify project files.
- `run_local_verifier`: run local verification code.
- `create_audit_record`: write local audit output.
- `external_action`: call or send to an external/public service.
- `public_action`: publish or post in a public place.
- `destructive_action`: delete, overwrite, reset, revoke, or otherwise destroy state.
- `sensitive_data_action`: access, transform, or disclose sensitive data.
- `private_data_action`: access, transform, or disclose private memory or private context.
- `runtime_event_action`: handle runtime-event continuation or incident routing.
- `customer_impacting_action`: affect a customer, enterprise reviewer, or production user.

The first prototype should treat `external_action`, `public_action`, `destructive_action`, `sensitive_data_action`, `private_data_action`, `runtime_event_action`, and `customer_impacting_action` as risky action classes.

## Safety Authorization Rules

For each risky action class:

- the action class must be present in `allowed_action_classes`;
- the matching boolean in `safety_authorizations` must be `true`;
- `basis.kind` must be `explicit_approval`, `operator_action`, `standing_policy`, or `system_rule`;
- a concrete approval or policy reference must exist.

For the first local-only prototype, risky action fixtures should normally be rejected unless they are deliberately constructed to test explicit approval handling.

Mapping:

| Risky action class | Required safety flag |
| --- | --- |
| `external_action` | `external_action` |
| `public_action` | `public_action` |
| `destructive_action` | `destructive_action` |
| `sensitive_data_action` | `sensitive_data` |
| `private_data_action` | `private_data` |
| `runtime_event_action` | `runtime_event` |
| `customer_impacting_action` | `customer_impacting` |

## Scope Rules

The verifier must reject when:

- the envelope source workspace or project is outside `scope`;
- the envelope target agent or role is outside `scope`;
- the requested interaction type is not in `allowed_interaction_types`;
- the requested delivery expectation is not in `constraints.allowed_delivery_expectations`;
- context references use a type outside `constraints.allowed_context_reference_types`;
- a file path is outside `constraints.allowed_paths` when that list is non-empty;
- a file path matches `constraints.denied_paths`;
- `expires_at` is in the past relative to the verifier's trusted time.

For the first prototype, path checks apply only to fixture-declared paths and must not inspect live filesystem state except for fixture loading.

Detailed context-package redaction and allowlist rules are defined in `docs/security/CONTEXT_PACKAGE_RULES.md`.

## Rejection Reason Codes

The first verifier should use stable reason codes:

- `authorization_context_missing`
- `authorization_context_schema_unsupported`
- `authorization_id_missing`
- `authorization_source_event_missing`
- `authorization_basis_missing`
- `summarized_context_not_authorization`
- `explicit_approval_event_missing`
- `interaction_type_not_authorized`
- `action_class_not_authorized`
- `risky_action_requires_explicit_authorization`
- `scope_workspace_mismatch`
- `scope_project_mismatch`
- `scope_target_mismatch`
- `delivery_expectation_not_authorized`
- `context_reference_type_not_authorized`
- `path_not_authorized`
- `authorization_expired`

Reason-code prose can change. Codes should not.

## Audit Requirements

Audit events should record:

- `authorization_id`;
- `authorization_result`: `accepted` or `rejected`;
- `authorization_reason`;
- source event references used for authorization;
- approval event references used for risky actions;
- allowed interaction type decision;
- allowed action class decision;
- safety authorization decision;
- scope decision;
- expiry decision.

Audit events must not store raw private message bodies, secrets, tokens, private memory, or unrelated context.

## Deferred

Deferred beyond the first prototype:

- production RedshieldWarden policy decisions;
- policy inheritance or group-based permissions;
- enterprise approval workflows;
- long-lived standing authorization registry;
- production credential and authorization revocation store;
- live runtime-event incident routing;
- customer-facing compliance evidence export.
