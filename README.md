# Redshield Agent Bus

Redshield Agent Bus is an open-core protocol and verifier toolkit for safe
agent-to-agent and agent-to-workflow handoffs.

The open core focuses on one job: define and verify safe bus semantics before
work crosses agent, tool, runtime, workspace, or delivery boundaries.

## What It Does

The current open core provides:

- a local `agent-bus` Python package;
- a verifier CLI for static bus-message fixtures;
- a local-only adapter dry-run preview and receipt verifier;
- envelope and state-transition validation;
- checks for source, target, actor identity, credential evidence, expiry,
  idempotency, delivery expectations, and risky authorization patterns;
- context-package redaction and allowlist rules;
- a credential-provider contract with local fixtures;
- public-safe examples for RSK AI Auth-style grants, Keyper-style credential
  evidence, Warden policy decisions, and Armor enforcement results;
- enforced open-core Warden policy-result fixtures for `allow`, `deny`, and
  `require_review`;
- enforced open-core Armor enforcement-result fixtures for `allow`, `block`,
  `sanitize`, and `require_review`;
- architecture, requirements, security, QA, and promotion-gate documentation.

The verifier is intentionally local-first. It does not post messages, call live
runtime tools, spawn agents, publish events, or perform external actions.

## Project Governance

- License: Apache License 2.0. See `LICENSE`.
- Contributions: see `CONTRIBUTING.md`.
- Vulnerability reporting: see `SECURITY.md`.
- Public release readiness: see `docs/release/OPEN_CORE_RELEASE_CHECKLIST.md`
  and `docs/release/RELEASE_SECURITY_GATE.md`.
- Package provenance controls: see
  `docs/release/PACKAGE_PROVENANCE_CONTROLS.md` and
  `docs/release/RELEASE_EVIDENCE_TEMPLATE.md`.
- Policy index: see `docs/policy/POLICY_INDEX.md`.
- Agent operation boundaries: see
  `docs/operations/AGENT_OPERATION_BOUNDARIES.md`.
- Class 4 production-readiness gates: see
  `docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md`.
- Initial risk register: see `docs/risk/INITIAL_RISK_REGISTER.md`.
- Initial control register: see `docs/risk/INITIAL_CONTROL_REGISTER.md`.
- Initial evidence register: see `docs/risk/INITIAL_EVIDENCE_REGISTER.md`.

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

Run the source classification check in the pre-split source repository:

```sh
python3 scripts/check_source_classification_manifest.py
```

Run the standard Python test command after installing test dependencies:

```sh
python3 -m pip install -e '.[test]'
python3 -m pytest
```

## Open-Core Boundary

The open core must remain useful without paid services.

Open core includes:

- protocol vocabulary and envelope semantics;
- local verifier and fixture suite;
- authorization-context and context-package safety rules;
- capability-grant proof adapter contract;
- credential-provider contract;
- baseline Warden policy-result contract;
- baseline Armor enforcement-result contract;
- adapter and promotion-gate documentation.

Commercial or enterprise editions may add scale, governance, deployed
enforcement, visibility, integrations, evidence exports, managed operations,
and support. They must not be required for local validation or the baseline
safety model.

## Neighboring Contracts

Agent Bus stays narrow by consuming neighboring capabilities through contracts:

- RSK AI Auth-style / RedshieldWorks Core capability grants describe workload
  identity and delegated authority.
- Keyper-style SSH certificate evidence can satisfy the credential-provider
  contract without making Agent Bus depend on Keyper.
- Warden policy results answer `allow`, `deny`, or `require_review`.
- Armor enforcement results answer `allow`, `block`, `sanitize`, or
  `require_review`.

The ecosystem verifier enforces those public example shapes without importing
or requiring private or commercial implementations of those systems.

## Safety Model

The verifier should fail closed when a message is missing required identity,
authorization, scope, freshness, idempotency, delivery, or safety information.

Fixtures must use fake identities and references. Do not put real secrets,
tokens, private messages, production runtime ids, live channel ids, or customer
data into fixtures.
