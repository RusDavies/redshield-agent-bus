# Policy Index

This index collects the current public-safe policy, boundary, and gate documents
for Redshield Agent Bus. It is an index of open-core rules and verifier-facing
contracts, not a deployed policy service, enterprise policy console, compliance
claim, or live-adapter approval.

## Current Policy Posture

- The open core is local-first: fixtures, verifier commands, dry-run previews,
  and receipt validation are allowed.
- Live posting, live session spawning, runtime/gateway side effects, public
  release, production use, external actions, destructive actions, and
  customer-facing security claims remain blocked until the matching gate and
  approval record exist.
- Warden and Armor are consumed through public contract shapes. The open core
  must not depend on private, commercial, customer-specific, or deployed
  Warden/Armor implementations for baseline validation.
- Evidence should use references, hashes, decisions, receipts, and redacted
  metadata. Fixtures and public docs must not contain private memory, secrets,
  raw chat transcripts, production runtime ids, live channel ids, credential
  material, or customer data.

## Boundary Documents

- [Agent operation boundaries](../operations/AGENT_OPERATION_BOUNDARIES.md):
  allowed and forbidden behavior for local verification, project-local work,
  adapter dry-run modeling, owner-only live trials, and shared/production use.
- [Local verifier to live adapter promotion gate](../operations/PROMOTION_GATE.md):
  staged movement from Gate 0 local verifier through Gate 1 dry-run, Gate 2
  owner-only trial, and Gate 3 shared/production use.
- [Class 4 production-readiness gates](../operations/CLASS_4_PRODUCTION_READINESS_GATES.md):
  operational evidence required before shared or production infrastructure use.
- [Local verifier runbook](../operations/LOCAL_VERIFIER_RUNBOOK.md):
  operator steps for running the local verifier without live side effects.

## Contract Documents

- [Open-core Warden policy contract](../architecture/OPEN_CORE_WARDEN_POLICY_CONTRACT.md):
  baseline policy decision shape for `allow`, `deny`, and `require_review`.
- [Open-core Armor enforcement contract](../architecture/OPEN_CORE_ARMOR_ENFORCEMENT_CONTRACT.md):
  baseline enforcement decision shape for `allow`, `block`, `sanitize`, and
  `require_review`.
- [Live adapter dry-run contract](../architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md):
  preview and receipt model for adapter behavior without live delivery.
- [Deterministic target resolver contract](../architecture/TARGET_RESOLVER_CONTRACT.md):
  ambiguity rejection, route preview, audit evidence, and wrong-destination
  fail-closed behavior.
- [Capability-grant proof adapter contract](../architecture/CAPABILITY_GRANT_PROOF_ADAPTER_CONTRACT.md):
  public capability-grant proof shape used by the verifier.
- [Credential capability providers](../architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md):
  provider contract for local runtime token and Keyper-style credential
  evidence examples.

## Security And Release Gates

- [Threat model](../security/THREAT_MODEL.md):
  threat, mitigation, and open-finding source for local verification, open-core
  preparation, and future live-adapter risks.
- [Authorization context schema](../security/AUTHORIZATION_CONTEXT_SCHEMA.md):
  source-event and approval-event requirements for bounded authority.
- [Context package rules](../security/CONTEXT_PACKAGE_RULES.md):
  redaction, allowlist, and reference rules for context crossing boundaries.
- [Release security gate](../release/RELEASE_SECURITY_GATE.md):
  required evidence before public visibility, package publication, tagging, or
  customer-facing security claims.
- [Package provenance controls](../release/PACKAGE_PROVENANCE_CONTROLS.md):
  expected protected-source, build, artifact, SBOM, and rollback controls.

## Risk And Evidence Registers

- [Initial risk register](../risk/INITIAL_RISK_REGISTER.md): current
  security, delivery, release, and operations risks.
- [Initial control register](../risk/INITIAL_CONTROL_REGISTER.md): current
  control expectations and evidence links.
- [Initial evidence register](../risk/INITIAL_EVIDENCE_REGISTER.md): current
  evidence inventory for open-core readiness.

## Local Verification

Run the public repository verification profile:

```sh
python3 scripts/verify_repo.py open-core
```

Run the full Python test suite:

```sh
python3 -m pytest
```

Run the policy-adjacent contract verifiers directly when changing Warden, Armor,
adapter, credential, capability, or ecosystem contract material:

```sh
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
```

## Fail-Closed Summary

Stop or reject work when any of these are missing, ambiguous, stale, or outside
the approved scope:

- actor, runtime, source, target, or requester identity;
- concrete source event or approval event;
- authorization context and safety authorization for the requested action class;
- scoped context-package references and redaction status;
- delivery expectation and receipt binding;
- Warden policy result where policy is required;
- Armor enforcement result where enforcement is required;
- expiry and idempotency checks;
- rollback or disable path for live behavior;
- explicit human approval for external, public, destructive, production,
  customer-impacting, release, or live-adapter behavior.
