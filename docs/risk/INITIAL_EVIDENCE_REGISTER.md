# Initial Evidence Register

## Purpose

This register defines public-safe evidence expectations for Redshield Agent Bus
gates, controls, and risks. It says what kind of proof can support a readiness
claim, where that proof should live, what it can demonstrate, and what must stay
out of evidence records.

This is a planning and readiness artifact. It does not approve public release,
package publication, live adapter promotion, shared infrastructure use,
production use, or enterprise security claims.

## Evidence Status

- Current: available in this repository and suitable for the named gate.
- Partial: available, but insufficient for a later gate without more proof.
- Planned: required before a later gate, but not produced yet.
- Blocked: cannot be produced until a named dependency exists.
- Superseded: replaced by newer evidence.

## Evidence Hygiene Rules

Evidence records must not contain:

- secrets, tokens, cookies, private keys, or credential material;
- private memory, private messages, unrelated chat history, or raw customer
  content;
- production runtime ids, live channel ids, or real user identifiers unless the
  record is explicitly approved for that audience;
- private vulnerability details before coordinated disclosure is complete;
- copied payload bodies when a hash, reference, fixture id, or redacted summary
  is enough.

Evidence records should prefer:

- commit hashes, file paths, fixture ids, command lines, and deterministic test
  results;
- hashes or references instead of raw sensitive content;
- explicit approval references that identify scope, duration, allowed behavior,
  and exclusions;
- stable dates and reviewer names or roles where public-safe.

## Evidence Summary

| ID | Evidence | Status | Supports | Gate |
| --- | --- | --- | --- | --- |
| EVD-001 | Open-core profile verification result | Current | CTL-007, CTL-010, CTL-016 | Gate 0 / public release |
| EVD-002 | Local verifier fixture-suite result | Current | CTL-001, CTL-002, CTL-003, CTL-004, CTL-005, CTL-019 | Gate 0 |
| EVD-003 | Adapter dry-run preview and receipt verification | Current | CTL-005, CTL-006 | Gate 0 / Gate 1 |
| EVD-004 | Capability-grant contract verification | Current | CTL-015 | Gate 0 / Gate 1 |
| EVD-005 | Credential-provider contract verification | Current | CTL-002, CTL-014 | Gate 0 / Gate 1 |
| EVD-006 | Warden policy-result contract verification | Current | CTL-012 | Gate 0 / Gate 2 |
| EVD-007 | Armor enforcement-result contract verification | Current | CTL-013 | Gate 0 / Gate 2 |
| EVD-008 | Ecosystem contract example verification | Current | CTL-012, CTL-013, CTL-014, CTL-015, CTL-016 | Gate 0 |
| EVD-009 | Python unit test result | Current | CTL-001 through CTL-016 | Gate 0 |
| EVD-010 | Threat-model review | Current | CTL-017, CTL-018, CTL-019, CTL-020 | Gate 0 / Class 4E planning |
| EVD-011 | Risk-register review | Current | CTL-017 | Class 4E planning |
| EVD-012 | Control-register review | Current | CTL-001 through CTL-020 | Class 4E planning |
| EVD-013 | Release evidence record | Planned | CTL-007, CTL-010, CTL-011, CTL-016 | Public/package release |
| EVD-014 | Approval record | Planned | CTL-001, CTL-006, CTL-007, CTL-008, CTL-009 | Gate 1+ |
| EVD-015 | Live adapter receipt record | Planned | CTL-005, CTL-006 | Gate 2 / Gate 3 |
| EVD-016 | Warden live policy decision record | Planned | CTL-012 | Gate 2 / Gate 3 |
| EVD-017 | Armor live enforcement record | Planned | CTL-013 | Gate 2 / Gate 3 |
| EVD-018 | Rollback or disable test result | Planned | CTL-006, CTL-007, CTL-009 | Gate 2 / Gate 3 |
| EVD-019 | Monitoring and stuck-work evidence | Planned | CTL-005, CTL-009, CTL-020 | Gate 3 |
| EVD-020 | Audit retention and minimization review | Planned | CTL-004, CTL-018 | Gate 2 / Gate 3 |
| EVD-021 | Branch protection and release automation evidence | Planned | CTL-010, CTL-011 | Public/package release |
| EVD-022 | SBOM, artifact hash, and provenance evidence | Planned | CTL-011 | Package release |

## Current Evidence Records

### EVD-001: Open-Core Profile Verification Result

Accepted evidence:

- exact command line;
- clean repository state;
- profile result and required-check count;
- commit hash under review.

Current command:

```sh
python3 scripts/verify_repo.py open-core
```

Current expected result: `OK: redshield-agent-bus open-core profile contains
80 required checks`.

Scope: proves the current open-core repository includes the required public-safe
files and fixtures for Gate 0 review. It does not prove branch protection,
release automation, public visibility readiness, or package provenance.

### EVD-002: Local Verifier Fixture-Suite Result

Accepted evidence:

- exact command line;
- fixture path;
- case count;
- accepted/rejected expectation status.

Current command:

```sh
python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty
```

Current expected result: `ok: true`, `case_count: 21`.

Scope: proves local envelope and transition fixtures cover current Gate 0
semantics for source provenance, actor identity, credential evidence, expiry,
idempotency, delivery expectations, authorization laundering, private-data
leakage, Warden/Armor bindings, and runtime-event misuse.

### EVD-003: Adapter Dry-Run Preview And Receipt Verification

Accepted evidence:

- exact command line;
- fixture path;
- case count;
- proof that `side_effect_performed` remains false for dry-run records.

Current command:

```sh
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
```

Current expected result: `ok: true`, `case_count: 6`.

Scope: proves local dry-run preview and receipt validation. It does not prove
trusted live delivery receipts or live surface delivery.

### EVD-004: Capability-Grant Contract Verification

Accepted evidence:

- exact command line;
- fixture path;
- valid and invalid grant cases.

Current command:

```sh
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
```

Current expected result: `ok: true`, `case_count: 3`.

Scope: proves the public capability-grant proof adapter shape for local
fixtures. It does not prove issuer trust or live grant issuance.

### EVD-005: Credential-Provider Contract Verification

Accepted evidence:

- exact pytest command or fixture-verifier result;
- provider fixture paths;
- accepted and rejected credential evidence cases.

Current command:

```sh
python3 -m pytest tests/test_credential_provider_contract.py
```

Scope: proves local runtime-token and Keyper-style SSH certificate evidence
fixtures. It does not prove a live credential registry, secret rotation, or
provider availability.

### EVD-006: Warden Policy-Result Contract Verification

Accepted evidence:

- exact command line;
- fixture path;
- allow, deny, require-review, and invalid policy cases.

Current command:

```sh
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
```

Current expected result: `ok: true`, `case_count: 6`.

Scope: proves the open-core Warden policy-result contract for local fixtures.
It does not prove live Warden policy enforcement.

### EVD-007: Armor Enforcement-Result Contract Verification

Accepted evidence:

- exact command line;
- fixture path;
- allow, block, sanitize, require-review, and invalid enforcement cases.

Current command:

```sh
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
```

Current expected result: `ok: true`, `case_count: 7`.

Scope: proves the open-core Armor enforcement-result contract for local
fixtures. It does not prove live Armor enforcement.

### EVD-008: Ecosystem Contract Example Verification

Accepted evidence:

- exact command line;
- fixture path;
- public example ids.

Current command:

```sh
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
```

Current expected result: `ok: true`, `case_count: 4`.

Scope: proves public-safe neighboring contract examples remain parseable and
downstream-agnostic. It does not prove private or commercial implementation
behavior.

### EVD-009: Python Unit Test Result

Accepted evidence:

- exact pytest command;
- pass/fail count;
- warning summary where relevant;
- commit hash under review.

Current command:

```sh
python3 -m pytest
```

Current expected result: all tests pass.

Scope: proves the repository's current local test suite passes. It does not
prove behavior outside the tested contracts.

### EVD-010: Threat-Model Review

Accepted evidence:

- reviewed threat-model file path;
- review date;
- reviewed evidence list;
- open findings;
- explicit approval scope and exclusions.

Current evidence:

- `docs/security/THREAT_MODEL.md`

Scope: proves Gate 0 local-verifier and open-core preparation review only. It
does not approve public release, package publication, live adapter promotion,
production use, enterprise claims, or customer-facing security posture.

### EVD-011: Risk-Register Review

Accepted evidence:

- reviewed risk-register file path;
- risk ids, owners, treatment, status, and stop conditions;
- accepted-risk owner and expiry if any risk is accepted.

Current evidence:

- `docs/risk/INITIAL_RISK_REGISTER.md`

Scope: proves risks are named and tracked for Class 4E planning. No accepted
risk exists in the initial register.

### EVD-012: Control-Register Review

Accepted evidence:

- reviewed control-register file path;
- control ids, status, mapped risks, mapped threats, gate expectations, and
  evidence references;
- clear distinction between current, started, defined, and planned controls.

Current evidence:

- `docs/risk/INITIAL_CONTROL_REGISTER.md`

Scope: proves controls are mapped for Class 4E planning. Planned controls do
not satisfy later gates until their evidence exists.

## Planned Evidence Records

### EVD-013: Release Evidence Record

Required before: public repository visibility approval or package publication.

Expected location:

- candidate-specific copy of `docs/release/RELEASE_EVIDENCE_TEMPLATE.md`.

Required fields:

- release candidate commit;
- source-protection review;
- verifier and test command results;
- vulnerability and risk review;
- rollback path;
- public visibility, package publication, and customer-facing claim approvals.

### EVD-014: Approval Record

Required before: live adapter trial, public release, package publication,
shared infrastructure use, production use, or customer-facing security claim.

Required fields:

- approving person or role;
- source surface or approval event reference;
- exact scope, duration, allowed action classes, and exclusions;
- rollback or stop condition;
- evidence files under review.

Invalid evidence:

- summarized approval;
- stale approval copied from another gate;
- broad approval such as "production" or "go live" without scope.

### EVD-015: Live Adapter Receipt Record

Required before: Gate 2 or Gate 3 live/shared use.

Required fields:

- adapter id and surface;
- source and destination binding;
- message id, correlation id, idempotency key, and preview id where applicable;
- delivery expectation;
- receipt id;
- result and failure reason;
- payload hash or redacted summary only.

Invalid evidence:

- private-only completion for chat-visible work;
- raw message body when a hash is sufficient;
- forged or unbound receipt id.

### EVD-016: Warden Live Policy Decision Record

Required before: risky live action classes that depend on Warden policy.

Required fields:

- policy decision id;
- envelope/action binding;
- decision: `allow`, `deny`, or `require_review`;
- policy version or ruleset reference;
- reviewer or approver when review is required;
- redacted reason and evidence references.

### EVD-017: Armor Live Enforcement Record

Required before: live adapters that process private, sensitive, external,
destructive, or customer-impacting payloads.

Required fields:

- enforcement decision id;
- envelope/action binding;
- decision: `allow`, `block`, `sanitize`, or `require_review`;
- sanitized field references where applicable;
- reviewer or approver when review is required;
- redacted reason and evidence references.

### EVD-018: Rollback Or Disable Test Result

Required before: Gate 2 or Gate 3 live/shared use.

Required fields:

- feature flag, config switch, or adapter disable path;
- command or administrative action tested;
- expected user-visible disabled behavior;
- test result;
- rollback owner;
- restoration path.

### EVD-019: Monitoring And Stuck-Work Evidence

Required before: Gate 3 shared or production use.

Required fields:

- health signal;
- pending-work age signal where queues exist;
- missing-receipt and wrong-destination detection;
- denial/block/review counts;
- alert thresholds and destination;
- manual review cadence.

### EVD-020: Audit Retention And Minimization Review

Required before: Gate 2 or Gate 3 live/shared use and evidence export.

Required fields:

- audit fields retained;
- fields never retained;
- redaction rules;
- retention duration;
- evidence export approval path;
- access review owner.

### EVD-021: Branch Protection And Release Automation Evidence

Required before: public repository visibility approval or package publication.

Required fields:

- protected branch settings;
- required status checks;
- direct-push controls;
- release workflow review;
- runner and action trust controls;
- maintainer review record.

### EVD-022: SBOM, Artifact Hash, And Provenance Evidence

Required before: package publication.

Required fields:

- build command;
- package artifacts;
- artifact SHA-256 hashes;
- SBOM tool, format, and output path;
- dependency review;
- provenance or trusted-publishing evidence.

## Review Rules

- Review this register whenever a new gate, control, or risk is added.
- Evidence must identify a commit, file, fixture, command, receipt, decision, or
  approval event; unsupported narrative is not evidence. Shocking, I know.
- Planned evidence cannot satisfy a gate.
- Evidence that contains secrets, private content, or unapproved real
  identifiers must be rejected or redacted before review.
- Public, package, live, shared, production, and enterprise approvals must cite
  the current evidence register revision.
