# Initial Risk Register

## Purpose

This register tracks public-safe product, security, operations, and release
risks for Redshield Agent Bus. It is an initial Class 4E planning artifact, not
a production approval record.

Companion controls are tracked in
`docs/risk/INITIAL_CONTROL_REGISTER.md`. A control listed there is only
sufficient for a gate when its status and evidence satisfy that gate's review
requirements.

Companion evidence expectations are tracked in
`docs/risk/INITIAL_EVIDENCE_REGISTER.md`. Planned evidence does not satisfy a
gate until the evidence exists, is reviewed, and matches the gate scope.

Ratings are deliberately simple until a formal risk process exists:

- Impact: Low, Medium, High, Critical.
- Likelihood: Low, Medium, High.
- Treatment: Mitigate, Avoid, Transfer, Accept, Monitor.
- Status: Open, Started, Blocked, Accepted, Closed.

Accepted risks require a named owner, expiry, compensating controls, and a
rollback or stop condition. No risks are accepted in this initial register.

## Risk Summary

| ID | Risk | Impact | Likelihood | Treatment | Status | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| RSK-001 | Summarized or stale context is treated as fresh authorization. | Critical | Medium | Mitigate | Started | Product owner / maintainer |
| RSK-002 | Work is delivered to the wrong agent, workspace, project, or chat surface. | High | Medium | Mitigate | Started | Maintainer / operator |
| RSK-003 | Private memory, secrets, customer data, or unrelated context crosses a boundary. | Critical | Medium | Mitigate | Started | Maintainer / operator |
| RSK-004 | Chat-visible work completes privately or without a trustworthy receipt. | High | High | Mitigate | Started | Maintainer / operator |
| RSK-005 | Live adapter behavior performs unapproved external, public, destructive, or customer-impacting actions. | Critical | Medium | Avoid | Started | Product owner / maintainer |
| RSK-006 | Production/shared use starts before Class 4 operations, monitoring, incident, rollback, backup/restore, and release-approval gates are satisfied. | Critical | Medium | Avoid | Started | Product owner |
| RSK-007 | Open-source or package release exposes private material or has weak supply-chain provenance. | High | Medium | Mitigate | Started | Maintainer |
| RSK-008 | Enterprise or customer-facing claims overstate Warden, Armor, evidence, or operational readiness. | High | Medium | Avoid | Open | Product owner |
| RSK-009 | Warden policy or Armor enforcement evidence is bypassed, inconsistent, or treated as optional for risky actions. | Critical | Medium | Mitigate | Started | Maintainer |
| RSK-010 | Shared queues or routing are abused, flooded, starved, or claimed by the wrong actor. | High | Medium | Mitigate | Open | Maintainer / operator |
| RSK-011 | Audit evidence stores too much private content, too little useful provenance, or lacks retention rules. | High | Medium | Mitigate | Started | Maintainer / operator |
| RSK-012 | Open-core contracts become coupled to private neighboring products or commercial-only implementations. | Medium | Medium | Mitigate | Started | Maintainer |

## Detailed Risks

### RSK-001: Authorization Laundering

Risk: Summaries, forwarded context, continuation notes, inferred intent, or
stale approvals are treated as fresh authority.

Controls already present:

- `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`
- `tests/fixtures/agent_bus/envelopes/invalid/summarized-context-approval.json`
- `docs/operations/AGENT_OPERATION_BOUNDARIES.md`

Next controls:

- implement complete authorization-context verifier coverage;
- reject stale or missing approval references for every risky action class;
- keep command provenance explicit in runtime/session handoffs.

Stop condition: any live or production promotion where approval cannot be bound
to a concrete source or approval event.

### RSK-002: Wrong Destination Delivery

Risk: Work or results route to the wrong agent, workspace, project, thread, or
chat surface.

Controls already present:

- target and delivery expectation fields in verifier fixtures;
- wrong-destination invalid fixture;
- dry-run preview and receipt contract;
- deterministic target resolver contract;
- local resolver tests for exact target, ambiguous selector, and adapter-surface mismatch;
- dry-run audit events include route resolution metadata;
- agent-operation delivery boundaries.

Next controls:

- implement trusted live-adapter receipts;
- add stuck/wrong-destination operational monitoring before shared use.

Stop condition: ambiguous target resolution or unbound receipt.

### RSK-003: Private Data Leakage

Risk: Private memory, private messages, secrets, customer data, production
runtime ids, or unrelated project context crosses into fixtures, audit records,
public docs, or another agent context.

Controls already present:

- context-package redaction and allowlist rules;
- private-data leakage invalid fixture;
- fixture rules in the local verifier runbook;
- public-release blockers for private data.

Next controls:

- implement content and reference scanning where feasible;
- define audit retention and minimization policy;
- add evidence review before public release or customer-facing use.

Stop condition: any fixture, public doc, audit record, or context package
contains unapproved private or secret material.

### RSK-004: Private-Only Completion

Risk: A user-visible request is marked complete in private or internal state
without visible delivery to the source surface.

Controls already present:

- delivery expectation validation;
- private-only dry-run receipt fixture;
- Discord operational rule requiring visible replies;
- agent-operation delivery boundary.

Next controls:

- implement trusted delivery receipts for live adapters;
- add stuck/private-only completion monitoring;
- define recovery reporting for missing receipts.

Stop condition: chat-visible work lacks a matching visible receipt or visible
failure.

### RSK-005: Unapproved Live Side Effects

Risk: A live adapter posts, spawns, calls a gateway/runtime, publishes, deletes,
or affects customers without explicit approval.

Controls already present:

- Gate 0/Gate 1 forbid live side effects;
- live-side-effect dry-run fixture;
- agent-operation approval boundaries;
- Class 4 production-readiness gates.

Next controls:

- implement hard live-adapter disable path;
- require Warden and Armor evidence for risky live action classes;
- test rollback/disable before Gate 2.

Stop condition: live side effect requested without the named adapter, surface,
scope, duration, rollback path, and evidence requirements.

### RSK-006: Premature Production Use

Risk: Shared or production infrastructure use starts before operational
readiness is evidenced.

Controls already present:

- promotion gate;
- Class 4 production-readiness gates;
- agent-operation Class E boundary.

Next controls:

- create production operations runbook;
- create initial policy index;
- define monitoring, incident, rollback, backup/restore, and review evidence.

Stop condition: any Gate 3 request missing Class 4 evidence or explicit human
approval.

### RSK-007: Release Supply-Chain Or Public-Data Failure

Risk: A public repository or package release exposes private material, ships
from untrusted provenance, or lacks vulnerability intake.

Controls already present:

- `LICENSE`, `CONTRIBUTING.md`, and `SECURITY.md`;
- release security gate;
- package provenance controls;
- release evidence template;
- open-core profile verification.

Next controls:

- implement approved branch protection and CI/release automation;
- generate candidate-specific SBOM and artifact hashes;
- verify public fixtures and docs before any visibility or package release.

Stop condition: missing release evidence, private material in public artifacts,
or unreviewed publishing workflow.

### RSK-008: Enterprise Readiness Overclaim

Risk: Product materials imply enterprise, compliance, customer-facing, Warden,
Armor, or managed-operations readiness before evidence exists.

Controls already present:

- product brief non-goals;
- open-core/commercial split;
- release and production gates block customer-facing claims.

Next controls:

- define Class 4E enterprise-readiness scope;
- create control and evidence registers;
- approve customer-facing security posture before claims.

Stop condition: any public, sales, customer, or enterprise claim that is not
backed by approved evidence.

### RSK-009: Policy Or Enforcement Bypass

Risk: Warden policy decisions or Armor enforcement decisions are missing,
inconsistent, forged, or optional for risky action classes.

Controls already present:

- open-core Warden and Armor contract validators;
- integrated envelope fixtures requiring Warden/Armor bindings;
- threat model links for TH-15 and TH-16.

Next controls:

- define mandatory live policy/enforcement points before Gate 2/Gate 3;
- add adapter-specific Warden/Armor enforcement tests;
- tie denials, blocks, sanitization, and review requirements to audit evidence.

Stop condition: risky live action proceeds without required Warden/Armor
evidence.

### RSK-010: Queue Abuse Or Work Starvation

Risk: Shared routing, queues, or claim paths are flooded, starved, claimed by
the wrong actor, or used for denial of service.

Controls already present:

- Class 4 gates require monitoring, stuck-work detection, and rate/claim
  controls before shared use.

Next controls:

- design claim authorization;
- define rate limits and quotas;
- add pending-work age and stale-claim monitoring.

Stop condition: shared queue or routing use without claim authorization and
stuck-work detection.

### RSK-011: Audit Evidence Failure

Risk: Audit evidence stores secrets/private content, omits key provenance, or
lacks retention and restore expectations.

Controls already present:

- fixture audit storage guidance;
- context-package redaction rules;
- Class 4 backup, restore, and audit-retention gate.

Next controls:

- create evidence register;
- define retention and redaction policy;
- test restore where durable audit state exists.

Stop condition: production/shared use without audit minimization, retention, and
restore evidence.

### RSK-012: Open-Core Coupling Drift

Risk: The open core becomes coupled to Keyper, RSK AI Auth, Warden, Armor,
commercial bundles, downstream products, customer policy, or private management
state.

Controls already present:

- open-core boundary in README and product brief;
- generic credential-provider, capability-grant, Warden, and Armor contracts;
- public-safe ecosystem fixtures;
- repository split and public-doc verification.

Next controls:

- keep neighboring systems behind public contract examples;
- reject private/commercial assumptions in open-core docs and tests;
- review public repo content before visibility changes.

Stop condition: open-core code or docs require a private/commercial product for
baseline verifier value.

## Review Cadence

Review this register:

- before Gate 2 or Gate 3 promotion;
- before public repository visibility or package release;
- after any security incident, wrong-destination delivery, private-data
  leakage, or live-adapter rollback;
- after every significant Warden/Armor contract change.
