# Initial Control Register

## Purpose

This register tracks controls for Redshield Agent Bus. It maps the
initial risk register, threat model, release gates, and Class 4 production gates
to concrete control expectations.

Companion evidence expectations are tracked in
`docs/risk/INITIAL_EVIDENCE_REGISTER.md`.

This is a planning and readiness artifact. It does not approve public release,
package publication, live adapter promotion, shared infrastructure use,
production use, or enterprise security claims.

Control status values:

- Defined: documented and ready for local review.
- Started: partly implemented or evidenced by current verifier/docs.
- Planned: required before a later gate, but not implemented yet.
- Blocked: cannot proceed until a named dependency is resolved.
- Retired: superseded by another control.

## Control Summary

| ID | Control | Status | Primary Risks | Primary Threats | Gate |
| --- | --- | --- | --- | --- | --- |
| CTL-001 | Concrete source authorization binding | Started | RSK-001, RSK-005 | TH-3, TH-9 | Gate 0 / Gate 1 |
| CTL-002 | Authenticated actor and runtime identity | Started | RSK-001, RSK-009, RSK-011 | TH-1, TH-12 | Gate 0 / Gate 1 |
| CTL-003 | Authorization-context scope enforcement | Started | RSK-001, RSK-005, RSK-009 | TH-3, TH-9 | Gate 0 / Gate 1 |
| CTL-004 | Context redaction and allowlist enforcement | Started | RSK-003, RSK-011 | TH-6, TH-10 | Gate 0 / Gate 1 |
| CTL-005 | Delivery expectation and receipt binding | Started | RSK-002, RSK-004 | TH-2, TH-7, TH-12 | Gate 0 / Gate 1 |
| CTL-006 | Dry-run/live side-effect separation | Defined | RSK-005, RSK-006 | TH-4, TH-9, TH-12 | Gate 0 / Gate 1 |
| CTL-007 | Promotion gates and explicit approval | Defined | RSK-005, RSK-006, RSK-008 | TH-9, TH-13, TH-14 | Gate 0+ |
| CTL-008 | Agent operation class boundaries | Defined | RSK-001, RSK-004, RSK-005, RSK-006 | TH-3, TH-7, TH-8, TH-9 | Gate 0+ |
| CTL-009 | Class 4 production-readiness gates | Defined | RSK-006, RSK-008, RSK-010, RSK-011 | TH-10, TH-11, TH-14 | Gate 3 |
| CTL-010 | Release security and vulnerability intake | Defined | RSK-007, RSK-008 | TH-13, TH-14 | Public release |
| CTL-011 | Package provenance controls | Defined | RSK-007 | TH-13 | Package release |
| CTL-012 | Warden policy-result contract | Started | RSK-005, RSK-008, RSK-009 | TH-9, TH-15 | Gate 0 / Gate 2 |
| CTL-013 | Armor enforcement-result contract | Started | RSK-003, RSK-005, RSK-009 | TH-6, TH-9, TH-16 | Gate 0 / Gate 2 |
| CTL-014 | Credential-provider evidence contract | Started | RSK-001, RSK-009, RSK-011 | TH-1, TH-12 | Gate 0 / Gate 1 |
| CTL-015 | Capability-grant proof adapter contract | Started | RSK-001, RSK-005, RSK-009 | TH-1, TH-9 | Gate 0 / Gate 1 |
| CTL-016 | Core boundary and coupling control | Defined | RSK-007, RSK-012 | TH-13, TH-14 | Public release |
| CTL-017 | Risk register review | Defined | RSK-001 through RSK-012 | TH-1 through TH-16 | Class 4E planning |
| CTL-018 | Audit minimization and retention | Planned | RSK-003, RSK-011 | TH-6, TH-10, TH-12 | Gate 2 / Gate 3 |
| CTL-019 | Runtime-event boundary | Started | RSK-001, RSK-005 | TH-3, TH-8, TH-9 | Gate 0 / Gate 1 |
| CTL-020 | Queue, rate, quota, and claim controls | Started | RSK-002, RSK-010 | TH-2, TH-11, TH-12 | Gate 2 / Gate 3 |

## Control Details

### CTL-001: Concrete Source Authorization Binding

Objective: every risky action must bind to a concrete source request or
approval event, not a summary, continuation note, inferred plan, or stale
handoff.

Evidence:

- `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`
- `tests/fixtures/agent_bus/envelopes/invalid/summarized-context-approval.json`
- `docs/operations/AGENT_OPERATION_BOUNDARIES.md`

Minimum gate expectation: Gate 0 local fixtures reject authorization
laundering patterns. Gate 1 and later live trials must bind approval to the
surface, actor, scope, duration, and action class that caused the live action.

### CTL-002: Authenticated Actor And Runtime Identity

Objective: message creation, claim, transition, completion, and receipt actors
must carry authenticated identity evidence instead of display-name-only claims.

Evidence:

- `docs/security/AGENT_IDENTITY_AUTHENTICATION.md`
- `docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md`
- `docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md`
- `tests/fixtures/agent_bus/envelopes/invalid/display-name-only-identity.json`
- `tests/fixtures/agent_bus/credential_providers/`

Minimum gate expectation: local verification rejects missing, unknown, expired,
revoked, mismatched, or proofless credential evidence. Live gates require
runtime-backed validation, not only fixture shape checks.

### CTL-003: Authorization-Context Scope Enforcement

Objective: requested work must remain inside declared scope, safety
authorization, expiry, action class, and output limits.

Evidence:

- `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`
- `src/agent_bus/verifier.py`
- `tests/test_verifier.py`
- `tests/fixtures/agent_bus/envelopes/`

Minimum gate expectation: local verification rejects unsafe external actions,
expired authorization, mismatched approval, and missing scope. Live gates require
per-action enforcement before side effects.

### CTL-004: Context Redaction And Allowlist Enforcement

Objective: context packages must pass only allowed references or redacted
content and must not copy private memory, secrets, unrelated project data, or
customer data across boundaries.

Evidence:

- `docs/security/CONTEXT_PACKAGE_RULES.md`
- `docs/architecture/FIXTURE_AUDIT_STORAGE.md`
- `tests/fixtures/agent_bus/envelopes/invalid/private-data-leakage.json`

Minimum gate expectation: local fixtures reject obvious private-data leakage.
Live and release gates require scanning, review, and retention rules suitable to
the surface being promoted.

### CTL-005: Delivery Expectation And Receipt Binding

Objective: requested work must declare where results belong, and completion
must bind to a matching visible or auditable receipt.

Evidence:

- `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md`
- `docs/architecture/TRUSTED_LIVE_ADAPTER_RECEIPT_MODEL.md`
- `docs/architecture/TARGET_RESOLVER_CONTRACT.md`
- `docs/operations/AGENT_OPERATION_BOUNDARIES.md`
- `src/agent_bus/target_resolver.py`
- `tests/test_target_resolver.py`
- `tests/test_dry_run.py`
- `tests/test_live_receipt.py`
- `tests/fixtures/adapter_dry_runs/`
- `tests/fixtures/live_receipts/`
- `tests/fixtures/agent_bus/envelopes/invalid/wrong-destination-delivery.json`

Minimum gate expectation: local dry-runs expose route preview and receipt shape.
Live gates require trusted adapter receipts and fail-closed behavior for missing
or mismatched receipts.

### CTL-006: Dry-Run/Live Side-Effect Separation

Objective: local verification and dry-run adapters must never post, publish,
spawn, delete, call side-effecting APIs, or affect customers.

Evidence:

- `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md`
- `docs/operations/PROMOTION_GATE.md`
- `docs/operations/AGENT_OPERATION_BOUNDARIES.md`

Minimum gate expectation: Gate 0 allows only local verification and dry-run
modeling. Any live action requires an explicit higher gate, named adapter,
scope, rollback path, and approval evidence.

### CTL-007: Promotion Gates And Explicit Approval

Objective: public release, package publication, live adapter use, production
use, and customer-facing security claims must be gated by explicit review and
approval evidence.

Evidence:

- `docs/operations/PROMOTION_GATE.md`
- `docs/release/CORE_RELEASE_CHECKLIST.md`
- `docs/release/RELEASE_SECURITY_GATE.md`
- `docs/release/RELEASE_EVIDENCE_TEMPLATE.md`

Minimum gate expectation: the gate records must show what is being approved,
what is excluded, who approved it, and which rollback or stop condition applies.

### CTL-008: Agent Operation Class Boundaries

Objective: agent work must stay inside the operation class authorized for the
current surface and must fail closed when approval, context, or delivery
evidence is ambiguous.

Evidence:

- `docs/operations/AGENT_OPERATION_BOUNDARIES.md`
- `docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md`

Minimum gate expectation: Class 0 through Class 4E boundaries are documented.
Live classes require explicit approval, visible receipts, runtime-event
separation, and audit evidence.

### CTL-009: Class 4 Production-Readiness Gates

Objective: shared or production infrastructure use must not start until
operations, monitoring, incident, rollback, backup/restore, security, privacy,
release, and review gates are satisfied.

Evidence:

- `docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md`
- `docs/risk/INITIAL_EVIDENCE_REGISTER.md`

Minimum gate expectation: no Class 4 approval exists until all gates have named
evidence, owners, status, and a production decision record.

### CTL-010: Release Security And Vulnerability Intake

Objective: public repository and package releases must have governance,
vulnerability intake, private-data review, release evidence, and rollback
expectations before release.

Evidence:

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/release/RELEASE_SECURITY_GATE.md`
- `docs/release/CORE_RELEASE_CHECKLIST.md`

Minimum gate expectation: release candidates must satisfy the security gate and
record review evidence before public visibility or package publication.

### CTL-011: Package Provenance Controls

Objective: packages must be traceable to protected source, trusted build
workflow, reviewed release candidate, artifact hashes, and rollback evidence.

Evidence:

- `docs/release/PACKAGE_PROVENANCE_CONTROLS.md`
- `docs/release/RELEASE_EVIDENCE_TEMPLATE.md`

Minimum gate expectation: publication remains blocked until concrete CI/release
automation, branch protection, trusted publishing, SBOM, artifact hashes, and
candidate evidence exist.

### CTL-012: Warden Policy-Result Contract

Objective: policy decisions must be explicit, bound to the envelope and action,
and able to allow, deny, or require review before risky work proceeds.

Evidence:

- `docs/architecture/CORE_WARDEN_POLICY_CONTRACT.md`
- `src/agent_bus/warden_policy.py`
- `tests/fixtures/warden_policy/`
- `tests/fixtures/agent_bus/envelopes/valid/valid-notify-with-warden-armor.json`

Minimum gate expectation: local fixtures verify the public contract. Live gates
must define mandatory policy decision points and fail-closed behavior for risky
actions.

### CTL-013: Armor Enforcement-Result Contract

Objective: enforcement decisions must be explicit, bound to the envelope and
action, and able to allow, block, sanitize, or require review before work
crosses sensitive boundaries.

Evidence:

- `docs/architecture/CORE_ARMOR_ENFORCEMENT_CONTRACT.md`
- `src/agent_bus/armor_enforcement.py`
- `tests/fixtures/armor_enforcement/`
- `tests/fixtures/agent_bus/envelopes/valid/valid-notify-with-warden-armor.json`

Minimum gate expectation: local fixtures verify the public contract. Live gates
must define adapter-specific enforcement tests and fail-closed defaults.

### CTL-014: Credential-Provider Evidence Contract

Objective: credential checks must return enough evidence to prove credential
availability, identity binding, expiry, revocation, and scope without exposing
secrets.

Evidence:

- `docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md`
- `src/agent_bus/credential_provider.py`
- `tests/test_credential_provider_contract.py`
- `tests/fixtures/agent_bus/credential_providers/`

Minimum gate expectation: local fixtures verify runtime-token and Keyper-style
SSH certificate evidence shapes. Live gates require actual provider integration
and secret-safe evidence storage.

### CTL-015: Capability-Grant Proof Adapter Contract

Objective: delegated authority must be represented by bounded capability grants
with actor, audience, action, expiry, and proof evidence.

Evidence:

- `src/agent_bus/capability_grant.py`
- `tests/test_capability_grant.py`
- `tests/fixtures/capability_grants/`
- `tests/fixtures/agent_bus/ecosystem/rsk-ai-auth-capability-grant.json`

Minimum gate expectation: local fixtures verify the public grant shape and
reject expired or mismatched grants. Live gates require issuer trust and proof
validation.

### CTL-016: Core Boundary And Coupling Control

Objective: the core must stay downstream-agnostic and avoid depending on
customer-specific data, deployment-specific state, or external products.

Evidence:

- `README.md`
- `docs/release/CORE_RELEASE_CHECKLIST.md`
- `docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md`

Minimum gate expectation: public docs and fixtures describe contracts rather
than private implementations. Release review must check for private data and
downstream coupling.

### CTL-017: Risk Register Review

Objective: risks must stay explicit, owned, reviewed, and linked to controls or
blocking follow-up before promotion.

Evidence:

- `docs/risk/INITIAL_RISK_REGISTER.md`

Minimum gate expectation: risk status, treatment, owner, and stop condition are
reviewed before public release, live trials, production use, or enterprise
claims.

### CTL-018: Audit Minimization And Retention

Objective: audit evidence must preserve provenance, decisions, receipts, and
reviewability without storing secrets or unnecessary private content.

Evidence:

- `docs/architecture/FIXTURE_AUDIT_STORAGE.md`
- `docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md`
- `docs/risk/INITIAL_EVIDENCE_REGISTER.md`

Minimum gate expectation: Gate 2 and Gate 3 require concrete retention,
redaction, evidence-export, and access-review rules before live or shared use.

### CTL-019: Runtime-Event Boundary

Objective: runtime-event continuation text must be treated as an operations
incident or runtime recovery signal, not as ordinary project work or fresh human
authorization.

Evidence:

- `tests/fixtures/agent_bus/envelopes/invalid/runtime-event-misuse.json`
- `docs/operations/AGENT_OPERATION_BOUNDARIES.md`

Minimum gate expectation: local verifier fixtures reject runtime-event misuse.
Live gates require a classifier and ops-only continuation path.

### CTL-020: Queue, Rate, Quota, And Claim Controls

Objective: shared work queues must prevent flooding, starvation, stale claims,
wrong-actor claims, and unbounded retry behavior.

Evidence:

- `docs/operations/CLASS_4_PRODUCTION_READINESS_GATES.md`
- `docs/operations/SHARED_USE_CONTROLS.md`
- `docs/risk/INITIAL_RISK_REGISTER.md`
- `src/agent_bus/shared_use.py`
- `tests/fixtures/shared_use/`
- `tests/test_shared_use.py`

Minimum gate expectation: shared and production gates require rate limits,
quotas, claim authorization, stale-claim monitoring, retry limits, and operator
recovery procedures before shared use.

## Review Rules

- Review this register whenever a new risk is added or a gate changes.
- Every open risk should map to at least one defined, started, or planned
  control.
- Every control should map to current or planned evidence in the evidence
  register.
- Every live, shared, production, package-release, public-release, or
  enterprise-readiness approval must cite the current register revision.
- Controls that remain planned cannot be used as evidence that a later gate is
  satisfied.
