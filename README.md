# Redshield Agent Bus

Redshield Agent Bus is a core protocol and verifier toolkit for safe
agent-to-agent and agent-to-workflow handoffs.

The core focuses on one job: define and verify safe bus semantics before
work crosses agent, tool, runtime, workspace, or delivery boundaries.

## What It Does

The current core provides:

- a local `agent-bus` Python package;
- a verifier CLI for static bus-message fixtures;
- a local-only adapter dry-run preview and receipt verifier;
- envelope and state-transition validation;
- checks for source, target, actor identity, credential evidence, expiry,
  idempotency, delivery expectations, and risky authorization patterns;
- context-package redaction and allowlist rules;
- a credential-provider contract with local fixtures;
- examples for
  [RSK AI Auth-style grants](docs/architecture/CAPABILITY_GRANT_PROOF_ADAPTER_CONTRACT.md),
  [Keyper-style credential evidence](docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md),
  [Warden policy decisions](docs/architecture/WARDEN_POLICY_CONTRACT.md),
  and [Armor enforcement results](docs/architecture/ARMOR_ENFORCEMENT_CONTRACT.md);
- enforced Warden policy-result fixtures for `allow`, `deny`, and
  `require_review`;
- enforced Armor enforcement-result fixtures for `allow`, `block`,
  `sanitize`, and `require_review`;
- architecture, requirements, security, QA, and promotion-gate documentation.

The verifier is intentionally local-first. It does not post messages, call live
runtime tools, spawn agents, publish events, or perform external actions.

## Project Governance

- License: Apache License 2.0. See [LICENSE](LICENSE).
- Contributions: see [CONTRIBUTING.md](CONTRIBUTING.md).
- Vulnerability reporting: see [SECURITY.md](SECURITY.md).
- Public release readiness: see
  [docs/release/CORE_RELEASE_CHECKLIST.md](docs/release/CORE_RELEASE_CHECKLIST.md)
  and [docs/release/RELEASE_SECURITY_GATE.md](docs/release/RELEASE_SECURITY_GATE.md).
- Package provenance controls: see
  [docs/release/PACKAGE_PROVENANCE_CONTROLS.md](docs/release/PACKAGE_PROVENANCE_CONTROLS.md)
  and [docs/release/RELEASE_EVIDENCE_TEMPLATE.md](docs/release/RELEASE_EVIDENCE_TEMPLATE.md).
- Public release infrastructure controls: see
  [docs/release/PUBLIC_RELEASE_INFRASTRUCTURE_CONTROLS.md](docs/release/PUBLIC_RELEASE_INFRASTRUCTURE_CONTROLS.md).
- Policy index: see [docs/policy/POLICY_INDEX.md](docs/policy/POLICY_INDEX.md).
- Agent operation boundaries: see
  [docs/operations/AGENT_OPERATION_BOUNDARIES.md](docs/operations/AGENT_OPERATION_BOUNDARIES.md).
- Class 4 production-readiness gates: see
  [docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md](docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md).
- Shared-use controls: see
  [docs/operations/SHARED_USE_CONTROLS.md](docs/operations/SHARED_USE_CONTROLS.md).
- Target resolver contract: see
  [docs/architecture/TARGET_RESOLVER_CONTRACT.md](docs/architecture/TARGET_RESOLVER_CONTRACT.md).
- Trusted live-adapter receipt model: see
  [docs/architecture/TRUSTED_LIVE_ADAPTER_RECEIPT_MODEL.md](docs/architecture/TRUSTED_LIVE_ADAPTER_RECEIPT_MODEL.md).
- Initial risk register: see [docs/risk/INITIAL_RISK_REGISTER.md](docs/risk/INITIAL_RISK_REGISTER.md).
- Initial control register: see [docs/risk/INITIAL_CONTROL_REGISTER.md](docs/risk/INITIAL_CONTROL_REGISTER.md).
- Initial evidence register: see [docs/risk/INITIAL_EVIDENCE_REGISTER.md](docs/risk/INITIAL_EVIDENCE_REGISTER.md).

No public release, package publication, live adapter promotion, production use,
or customer-facing security claim is approved by the presence of these files.
They define the gate; they do not open it.

## Why It Exists

Agent systems often pass work through chat messages, session notes, copied
context, or informal handoffs. That is convenient until the work crosses a
privacy, authorization, delivery, runtime, or audit boundary.

Redshield Agent Bus makes those handoffs explicit:

- who requested the work;
- which actor/runtime is acting;
- what authority is claimed;
- what context is allowed;
- whether the request is fresh and non-duplicated;
- where the result must be delivered;
- which safety checks allowed, denied, blocked, sanitized, or required review.

## Quick Start

Run the local verifier against the fixture suite:

```sh
python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 21
}
```

Run the credential-provider contract verifier:

```sh
python3 -m pytest tests/test_credential_provider_contract.py
```

Expected result: the suite accepts the local runtime token and Keyper-style
SSH certificate evidence fixtures, then rejects unavailable, expired, revoked,
mismatched, missing-proof, and missing-evidence provider responses.

Run the local-only adapter dry-run verifier against preview and receipt
fixtures:

```sh
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 6
}
```

Run the capability-grant proof adapter contract verifier:

```sh
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 3
}
```

Run the Warden policy-result contract verifier:

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

Run the Armor enforcement-result contract verifier:

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

Run the ecosystem contract example verifier:

```sh
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 4
}
```

Run the standard Python test command after installing test dependencies:

```sh
python3 -m pip install -e '.[test]'
python3 -m pytest
```

## Neighboring Contracts

Agent Bus stays narrow by consuming neighboring capabilities through contracts:

- [RSK AI Auth-style / RedshieldWorks Core capability grants](docs/architecture/CAPABILITY_GRANT_PROOF_ADAPTER_CONTRACT.md)
  describe workload identity and delegated authority.
- [Keyper-style SSH certificate evidence](docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md)
  can satisfy the credential-provider contract without making Agent Bus depend
  on Keyper.
- [Warden policy results](docs/architecture/WARDEN_POLICY_CONTRACT.md)
  answer `allow`, `deny`, or `require_review`.
- [Armor enforcement results](docs/architecture/ARMOR_ENFORCEMENT_CONTRACT.md)
  answer `allow`, `block`, `sanitize`, or
  `require_review`.

The ecosystem verifier enforces those public example shapes without importing
or requiring external implementations of those systems.

## Safety Model

The verifier should fail closed when a message is missing required identity,
authorization, scope, freshness, idempotency, delivery, or safety information.

Fixtures must use fake identities and references. Do not put real secrets,
tokens, private messages, production runtime ids, live channel ids, or customer
data into fixtures.
