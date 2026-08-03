# Deterministic Target Resolver Contract

## Purpose

The target resolver converts a verified bus-message target selector into a
single local route preview before any adapter dry-run or later live behavior is
allowed. It exists to prevent ambiguous target selection, wrong-destination
delivery, and audit gaps.

This contract is core and local-first. It does not approve live delivery,
session spawning, runtime calls, queue publication, production use, public
release, or enterprise routing.

## Resolver Inputs

The resolver consumes only public-safe envelope and adapter-capability metadata:

- `message_id` and `correlation_id`;
- `source.workspace_id` and `source.project_slug`;
- `target.target_agent_id` or `target.target_role`;
- `target.allowed_runtime_ids`;
- `authorization_context.scope.target_agent_ids`;
- `authorization_context.scope.target_roles`;
- `delivery_expectation.type`;
- `delivery_expectation.target_surface`;
- `delivery_expectation.source_conversation_id`;
- `delivery_expectation.thread_id`;
- `adapter_capability.adapter_id`;
- `adapter_capability.adapter_type`;
- `adapter_capability.surface`.

The resolver must not read private memory, raw chat bodies, secrets, credential
material, customer data, production runtime ids, or live channel ids.

## Target Resolution Shape

```json
{
  "schema_version": "targetresolution.v1",
  "resolver_id": "local_deterministic_resolver_v1",
  "resolution_id": "resolution_msg_0001",
  "message_id": "msg_0001",
  "correlation_id": "corr_0001",
  "decision": "resolved",
  "reason_codes": ["target_agent_id_exact", "delivery_destination_bound"],
  "selected_target": {
    "target_agent_id": "agent_target_test",
    "target_role": null,
    "workspace_id": "workspace_redshield_test",
    "project_slug": "project_agent_bus_test",
    "allowed_runtime_ids": ["runtime_local_test"]
  },
  "route_preview": {
    "surface": "discord",
    "conversation_id": "channel_test_source",
    "thread_id": null,
    "adapter_id": "adapter_discord_dry_run_test",
    "adapter_type": "chat",
    "delivery_expectation_type": "visible_chat_reply"
  },
  "audit_ref": {
    "content_hash": "sha256:test-placeholder",
    "privacy_classification": "internal"
  }
}
```

## Decision Values

- `resolved`: exactly one target selector and one destination preview were
  resolved.
- `rejected`: the selector, scope, destination, or adapter binding is missing,
  ambiguous, or mismatched.

## Stable Reason Codes

Resolved path:

- `target_agent_id_exact`: the message names one exact target agent.
- `target_role_exact`: the message names one exact target role.
- `delivery_destination_bound`: the adapter surface matches the declared
  delivery destination.

Rejected path:

- `target_selector_missing`: the message has no target agent or target role.
- `target_selector_ambiguous`: the message names both target agent and target
  role.
- `target_scope_mismatch`: the selected target is outside authorization scope.
- `delivery_destination_missing`: the delivery destination lacks a target
  surface or source conversation reference.
- `adapter_surface_mismatch`: the adapter surface does not match the delivery
  destination surface.

Reason-code prose can change. Codes should not.

## Ambiguity Rejection

The resolver must reject a target when:

- neither `target_agent_id` nor `target_role` is present;
- both `target_agent_id` and `target_role` are present;
- an exact target agent is outside the authorization scope allowlist;
- an exact target role is outside the authorization scope allowlist;
- the delivery destination lacks a surface or conversation reference;
- the selected adapter surface does not match the delivery target surface.

Rejected resolution records are audit evidence. They are not permission to try
another route.

## Route Preview Requirements

A route preview must bind:

- destination surface;
- destination conversation reference;
- optional thread reference;
- adapter id;
- adapter type;
- delivery expectation type;
- selected target agent or role;
- workspace and project scope.

For Gate 1, the route preview is embedded in the adapter dry-run preview. It
must never perform a side effect.

## Wrong-Destination Fail-Closed Handling

The bus/verifier must fail closed when:

- the adapter preview destination differs from the envelope delivery
  expectation;
- the route preview differs from the deterministic resolver result;
- the dry-run receipt destination differs from the preview destination;
- a later live adapter cannot produce a receipt bound to the same route preview.

No resolver implementation may silently rewrite the destination, fall back to a
display name, or pick the first candidate from an ambiguous set.

## Audit Requirements

Audit events must record:

- `resolution_id`;
- `resolver_id`;
- `message_id`;
- `correlation_id`;
- `decision`;
- stable reason codes;
- selected target metadata;
- route preview metadata;
- content hash and privacy classification.

Audit events must not store raw message bodies, private memory, secrets,
credential material, production runtime ids, live channel ids, customer data, or
live platform response payloads.

## Local Verification

Run the resolver-related tests:

```sh
python3 -m pytest tests/test_target_resolver.py tests/test_dry_run.py
```

Run the dry-run fixture verifier:

```sh
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
```
