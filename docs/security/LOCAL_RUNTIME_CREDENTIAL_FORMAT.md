# Local Runtime Credential Format

## Purpose

This document selects the first local runtime credential format for the Redshield Agent Bus verifier and Gate 1 dry-run preparation.

This is not a production credential system. It is a local-only format that lets the prototype model authenticated runtime and agent identity without introducing distributed signing, live secrets, or external runtime dependencies.

## Decision

The first credential format is `local_runtime_token`.

It uses a local credential registry that maps an opaque `credential_id` to a runtime-owned secret hash, allowed actor bindings, scope bindings, status, and expiry metadata.

Bus-message envelopes, transition fixtures, audit events, and dry-run receipts may reference the `credential_id`, but they must never contain raw tokens, token hashes, salts, cookies, API keys, or other credential material.

## Credential Registry Shape

The local registry is repository-external or fixture-synthetic until a real runtime integration exists. A registry record has this logical shape:

```json
{
  "credential_id": "credential_local_test",
  "auth_method": "local_runtime_token",
  "runtime_id": "runtime_local_test",
  "actor_id": "agent_source_test",
  "actor_type": "agent",
  "allowed_agent_roles": ["source"],
  "workspace_ids": ["workspace_redshield_test"],
  "project_slugs": ["redshield-agent-bus"],
  "token_hash": "sha256:<hex>",
  "status": "active",
  "issued_at": "2026-07-14T00:00:00Z",
  "expires_at": "2026-08-14T00:00:00Z",
  "rotated_from": null
}
```

Fixture examples may omit `token_hash` entirely or use a placeholder marker such as `sha256:<fixture-placeholder>`. Real token hashes must not be committed.

## Token Format

The raw local runtime token is an operator-local secret. It should be high entropy and generated outside the message envelope.

Recommended local token presentation:

```text
rab_local_<credential-id-fragment>_<random-secret>
```

Rules:

- `rab_local_` identifies the token family for operators and logs.
- The credential-id fragment is only a routing hint; it is not trusted by itself.
- The random secret must provide at least 128 bits of entropy.
- The bus compares only a stored hash of the token, not the raw token.
- Token verification must be constant-time once both sides have selected a credential record.

## Envelope Fields

When a local runtime token authenticates an actor, the accepted envelope or transition records:

- `auth.actor_id`;
- `auth.actor_type`;
- `auth.runtime_id`;
- `auth.credential_id`;
- `auth.auth_method`: `local_runtime_token`;
- `auth.authenticated_at`.

The envelope must not include the raw token, token hash, registry record, or credential secret source.

## Validation Rules

The verifier or future dry-run adapter must reject:

- unknown `credential_id`;
- credentials whose `auth_method` is not `local_runtime_token` for this first format;
- disabled, revoked, expired, or not-yet-valid credentials;
- actor ids not bound to the credential;
- actor types not bound to the credential;
- runtime ids not bound to the credential;
- workspace or project scopes not allowed by the credential;
- display-name-only identity claims;
- credential material appearing in envelopes, context packages, fixtures, audit records, or receipts.

## Rotation And Revocation

Rotation creates a new `credential_id` and marks the old record as `rotated` or `revoked` for future validations. Historical audit records keep the old `credential_id` so past events remain reconstructable without preserving the old secret.

Minimum local statuses:

- `active`: accepted when all bindings and expiry checks pass.
- `disabled`: rejected until re-enabled by an operator.
- `revoked`: permanently rejected for future use.
- `rotated`: rejected for new messages; retained for historical audit interpretation.
- `expired`: rejected after `expires_at`.

## Audit Expectations

Audit events should record:

- credential id;
- runtime id;
- actor id and type;
- credential status at validation time;
- authentication result;
- failure reason when rejected.

Audit events must not record raw tokens, token hashes, credential files, environment-variable values, or secret material.

## Promotion Boundary

This format is enough for Gate 0 verifier work and Gate 1 dry-run preview modeling.

It is not enough for Gate 2 owner-only live adapter trials or Gate 3 shared/production use without additional review of storage, rotation, runtime trust, access control, and operational disable paths.
