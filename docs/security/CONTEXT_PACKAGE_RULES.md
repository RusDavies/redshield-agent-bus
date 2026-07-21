# Context Package Redaction And Allowlist Rules

## Purpose

Context packages give a target agent enough information to evaluate or perform a bus-message request. They must not become a private-memory dump, a copied chat transcript, or a way to smuggle unrelated project context across boundaries.

These rules define the first local-only verifier behavior for context-package allowlisting, redaction, and audit evidence.

## Core Rule

Context packages use references by default and copied content only by explicit, narrow exception.

The verifier must reject a context package unless every referenced item is allowed by:

- the envelope source and target scope;
- `authorization_context.constraints.allowed_context_reference_types`;
- privacy classification rules;
- redaction rules;
- fixture-safe test-data rules.

## Envelope Placement

Every verifier fixture envelope should include:

```json
{
  "context_package": {
    "schema_version": "ctxpkg.v1",
    "package_id": "ctx_test_0001",
    "summary": "Short scoped summary for the target agent.",
    "references": [],
    "redactions": []
  }
}
```

The verifier must reject messages with a missing `context_package`, missing `schema_version`, unsupported `schema_version`, missing `package_id`, or a package that contains raw private or secret content.

## Required Fields

The first-slice `context_package` requires:

- `schema_version`: currently `ctxpkg.v1`.
- `package_id`: stable id for the package.
- `summary`: short sanitized summary for the target.
- `references`: allowlisted context references.
- `redactions`: redaction decisions already applied by the source.
- `privacy_classification`: highest classification of the package after redaction.

Optional fields:

- `constraints`: context-specific limits, if narrower than authorization context.
- `notes`: short non-authoritative notes for the target.

`notes` and `summary` must never be treated as fresh authorization.

## Reference Shape

Each reference should be a JSON object:

```json
{
  "ref_id": "ref_test_req_0001",
  "type": "source_event",
  "locator": "event_test_request_0001",
  "privacy_classification": "internal",
  "allowed_use": ["verify_request", "compose_response"],
  "copy_mode": "reference_only",
  "content_hash": "sha256:test-placeholder",
  "redaction_status": "not_required"
}
```

Required reference fields:

- `ref_id`: stable reference id.
- `type`: reference type.
- `locator`: fixture-safe locator, path, event id, or identifier.
- `privacy_classification`: classification of the referenced item.
- `allowed_use`: what the target may use this reference for.
- `copy_mode`: whether content is referenced or copied.
- `redaction_status`: `not_required`, `redacted`, or `rejected`.

Optional reference fields:

- `content_hash`: hash of referenced or normalized content.
- `excerpt`: short sanitized excerpt when explicitly allowed.
- `redaction_notes`: short explanation of what was removed.

## Allowed Reference Types

The first local-only verifier recognizes:

- `source_event`: concrete source request or approval event id.
- `project_file`: project-local file path.
- `requirements_doc`: project-local requirements document.
- `security_doc`: project-local security document.
- `architecture_doc`: project-local architecture document.
- `fixture`: repository-local test fixture.
- `audit_event`: expected audit-event fixture.

The first prototype must reject:

- `private_memory`;
- `raw_chat_history`;
- `credential`;
- `secret`;
- `external_url`;
- `production_runtime_state`;
- `unrelated_project_file`;
- `customer_data`;
- `unknown`.

Later prototypes may add external or production reference types only after separate authorization, privacy, and adapter rules exist.

## Copy Modes

Allowed first-slice copy modes:

- `reference_only`: target gets a locator/reference, not copied content.
- `sanitized_excerpt`: target gets a short redacted excerpt.
- `metadata_only`: target gets metadata such as id, hash, title, or classification.

Rejected copy modes:

- `raw_content`;
- `full_chat_transcript`;
- `private_memory_dump`;
- `secret_value`;
- `credential_material`.

The first verifier should prefer `reference_only` and `metadata_only`. `sanitized_excerpt` is allowed only when the fixture declares redactions and the privacy classification after redaction is not `private` or `sensitive`.

## Privacy Classifications

Use these classifications:

- `public`;
- `shared`;
- `internal`;
- `private`;
- `sensitive`;
- `secret`.

Rules:

- `secret` content is always rejected.
- `sensitive` content requires `authorization_context.safety_authorizations.sensitive_data` and must be referenced or redacted, not copied raw.
- `private` content requires `authorization_context.safety_authorizations.private_data` and must be referenced or redacted, not copied raw.
- `internal`, `shared`, and `public` content still require type and scope allowlisting.
- Package-level `privacy_classification` must be the highest remaining classification after redaction.

## Redaction Categories

Use stable redaction categories:

- `secret_value`;
- `credential_material`;
- `api_key_or_token`;
- `cookie_or_session`;
- `private_memory`;
- `personal_data`;
- `customer_data`;
- `unrelated_project_context`;
- `live_channel_id`;
- `production_runtime_id`;
- `private_message_body`;
- `unsafe_instruction`;
- `summarized_authorization_claim`.

Every redaction entry should include:

- `category`;
- `ref_id`;
- `action`: `removed`, `replaced`, `hashed`, `summarized`, or `rejected`;
- `reason`;
- `replacement`: optional placeholder such as `[REDACTED:secret_value]`.

## Allowlist Rules

The verifier must reject when:

- a reference type is not in `authorization_context.constraints.allowed_context_reference_types`;
- a reference points outside the authorized project/workspace scope;
- a file path is outside `authorization_context.constraints.allowed_paths` when that list is non-empty;
- a file path matches `authorization_context.constraints.denied_paths`;
- a reference has `privacy_classification` `private`, `sensitive`, or `secret` without matching authorization and copy-mode restrictions;
- `copy_mode` is rejected;
- `summary` or `notes` claim to grant approval;
- a live channel id, real credential id, or production runtime id appears in a fixture context package;
- redaction status is `rejected` but the reference remains usable.

## Rejection Reason Codes

Use stable reason codes:

- `context_package_missing`
- `context_package_schema_unsupported`
- `context_package_id_missing`
- `context_reference_type_not_allowed`
- `context_reference_scope_mismatch`
- `context_reference_path_not_allowed`
- `context_reference_path_denied`
- `context_secret_rejected`
- `context_private_data_not_authorized`
- `context_sensitive_data_not_authorized`
- `context_copy_mode_rejected`
- `context_raw_chat_rejected`
- `context_private_memory_rejected`
- `context_summary_claims_authorization`
- `context_unredacted_private_content`
- `context_live_identifier_rejected`
- `context_redaction_required`

Reason-code prose can change. Codes should not.

## Audit Requirements

Verifier audit events should record:

- `package_id`;
- context validation result;
- rejected reason code when applicable;
- allowed reference ids and types;
- rejected reference ids and types;
- privacy classification decision;
- redaction categories applied;
- copy-mode decisions;
- authorization constraints used for allowlist checks.

Audit events must not store raw secrets, private memory, private message bodies, credential material, or unrelated context.

## Fixture Hygiene

Fixtures must use synthetic locators and ids. They may include obvious fake examples such as:

- `event_test_request_0001`;
- `projects/redshield-agent-bus/docs/requirements/INITIAL_AGENT_BUS_SLICE.md`;
- `fixture://valid/notify-minimal`;
- `channel_test_source`;
- `runtime_local_test`.

Fixtures must not include live Discord ids, real user private messages, real tokens, real cookies, production runtime ids, or private memory.

## Deferred

Deferred beyond the first prototype:

- content scanning implementation details;
- production redaction engine selection;
- retention policy for context packages;
- external URL fetching and caching rules;
- customer-data handling;
- enterprise evidence export for redaction decisions;
- integration with RedshieldArmor data-loss-prevention enforcement.
