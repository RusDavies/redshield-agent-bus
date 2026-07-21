# Credential Capability Providers

## Purpose

This document records the Keyper-inspired credential-provider conclusion for Redshield Agent Bus.

Agent Bus needs authenticated actor, runtime, scope, and credential-status evidence before it can safely route, claim, transition, complete, or deliver work. It should not hard-code that capability to any single product, including Keyper.

## Decision

Agent Bus should depend on a narrow credential capability contract, not on Keyper directly.

Keyper is a strong future provider candidate for SSH-backed machine and agent identity, but it should remain one interchangeable implementation behind a capability boundary. The current `local_runtime_token` format remains the Gate 0 / Gate 1 reference provider for deterministic local verifier and dry-run work.

The goal is swappability where it matters, without creating a giant identity abstraction that tries to normalize every IAM, SSH, certificate, token, and policy system into one sad enterprise pudding.

## Capability Contract

The minimum provider capability is:

> Given an actor claim and credential reference, verify a stable actor/runtime/scope binding, credential status, expiry, revocation state, and audit evidence.

The provider contract should support these logical operations:

- resolve a `credential_id`;
- verify a proof, assertion, or local registry binding;
- return `actor_id`;
- return `actor_type`;
- return `runtime_id`;
- return workspace and project scope bindings;
- return credential status: `active`, `disabled`, `revoked`, `rotated`, or `expired`;
- return expiry and trust-level metadata;
- return an audit/evidence reference;
- fail closed with stable reason codes.

The provider contract should not own bus authorization, routing, state-transition, delivery-expectation, or context-package decisions. Those remain Agent Bus responsibilities.

Provider-contract fixtures live under `tests/fixtures/agent_bus/credential_providers/` and are exercised by `tests/test_credential_provider_contract.py`. They cover accepted local runtime-token evidence and fail-closed cases for unknown credentials, revoked credentials, expired credentials, actor mismatch, runtime mismatch, scope mismatch, missing evidence, provider unavailability, and missing proof.

Initial stable reason codes include:

- `credential_unknown`;
- `credential_revoked`;
- `credential_expired`;
- `credential_proof_missing`;
- `actor_id_mismatch`;
- `actor_type_mismatch`;
- `runtime_id_mismatch`;
- `workspace_scope_mismatch`;
- `project_scope_mismatch`;
- `provider_unavailable`;
- `provider_response_field_missing:<field>`.

## Provider Candidates

### Local Runtime Token Registry

The current reference provider.

Use for:

- Gate 0 local verifier fixtures;
- Gate 1 dry-run preview modeling;
- deterministic provider-contract tests.

Do not treat it as the production distributed-trust answer.

### Keyper

Keyper is a natural future provider for SSH-backed machine, runtime, and agent identity.

Potential strengths:

- SSH certificate lifecycle;
- source-to-destination access policy;
- revocation/KRL posture;
- managed-host trust and drift evidence;
- issuer orchestration across Smallstep, OpenBao, or other backends;
- audit evidence around approvals, issuance, denial, expiry, and revocation.

Agent Bus should consume Keyper evidence and identity/status assertions, not manage SSH private keys or become Keyper-specific.

### Smallstep Direct

Smallstep `step-ca` can be evaluated as a direct provider or issuer/status source.

Strengths:

- mature SSH certificate issuance;
- user and host certificates;
- constrained principals and TTLs.

Limit:

- it does not provide Keyper's broader access-matrix lifecycle, host drift, and evidence model.

### OpenBao Or Vault Direct

OpenBao or Vault SSH secret engines can be evaluated as direct credential or issuer providers.

Strengths:

- established secrets/audit substrate;
- SSH certificate issuer capability;
- operational patterns familiar to security teams.

Limit:

- issuer capability alone does not prove managed-host enforcement, source-to-destination policy intent, or bus-specific authorization.

### SPIFFE/SPIRE

SPIFFE/SPIRE is a strong future candidate for workload identity if Agent Bus becomes multi-runtime infrastructure.

Strengths:

- workload attestation;
- SVID lifecycle;
- mTLS identity;
- rotation and workload-bound identity.

Limit:

- SSH access lifecycle and managed-host evidence remain separate concerns unless paired with Keyper or another SSH-specific layer.

### mTLS Client Certificates

mTLS is a useful service-to-service identity option for runtime-to-bus authentication.

Strengths:

- simple proof-of-possession;
- operationally common for services;
- maps well to runtime identity.

Limit:

- it is less expressive for SSH-specific access lifecycle, KRL posture, managed-host trust, and source-to-destination SSH policy.

### OIDC Or JWT Workload Identity

OIDC/JWT identity is useful upstream for human/operator login, controller API authentication, or cloud workload identity.

Strengths:

- common identity-provider integration;
- useful claim model;
- good for UI/API and operator authentication.

Limit:

- bearer-token style assertions are not enough by themselves for high-trust SSH-backed execution paths unless paired with proof-of-possession, issuer constraints, and revocation/evidence checks.

### Static Service Account Tokens

Static service tokens are acceptable only as bootstrap, compatibility, or low-trust local fixtures.

They should not become the default enterprise posture.

### Hardware-Backed Keys

TPM, HSM, YubiKey, or other hardware-backed signing can be evaluated later for privileged agents, runtimes, or operators.

Strengths:

- stronger key custody;
- proof-of-possession;
- useful for high-risk administrative actors.

Limit:

- operational friction and recovery complexity are high enough that this should be a later capability, not a first-slice dependency.

## Design Rules

- Do not single-vendor Agent Bus to Keyper.
- Do not create a broad IAM abstraction that hides security-relevant provider differences.
- Normalize only the facts Agent Bus needs to make a bus decision.
- Keep provider-specific evidence available as references or redacted attachments.
- Fail closed when provider status, scope, expiry, or evidence is unavailable.
- Keep credential material out of envelopes, fixtures, audit records, receipts, and context packages.
- Use capability tests to compare providers rather than assuming provider equivalence.

## Recommended Path

1. Keep `local_runtime_token` as the reference provider while the verifier remains local-only.
2. Use the provider-contract fixture tests as the comparison harness.
3. Compare Keyper, Smallstep direct, OpenBao/Vault direct, SPIFFE/SPIRE, mTLS, and OIDC/JWT against the same provider contract.
4. Treat Keyper as a bounded design spike, not a hard dependency.
5. Promote a provider only when the threat model, operational boundary, and promotion gate evidence support it.

## Non-Goals

- No Keyper dependency in the first local verifier.
- No production identity-provider selection at Gate 0.
- No implementation of a full OIDC provider inside Agent Bus.
- No implementation of an SSH CA inside Agent Bus.
- No hiding of provider-specific revocation, expiry, trust, or evidence limits behind a misleading "all providers are equal" interface.
