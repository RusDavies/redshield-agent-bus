# Threat Model

## Scope

This initial threat model covers the first Redshield Agent Bus messaging slice:

- one source agent creates one typed bus message;
- the bus validates the message envelope;
- one target agent or agent role can claim and act on the message;
- the target records completion, failure, rejection, or required input;
- the bus records delivery expectations, state transitions, and audit evidence.

This model also covers the Class 4E product direction: production infrastructure use, open-source publication of the core bus, and paid enterprise RedshieldWarden/RedshieldArmor integrations.

Out of scope for this initial model:

- multi-target broadcast fan-out;
- long-running subscriptions;
- full RedshieldWarden policy engine integration;
- full RedshieldArmor runtime enforcement integration;
- production queue/database selection;
- public package release workflow details;
- enterprise compliance evidence beyond identifying required controls and gaps.

## Security Objectives

- Preserve trustworthy provenance for every bus message.
- Prevent unauthorized work, tool use, external action, or public/customer-impacting action.
- Prevent private memory, secrets, or unrelated project context from crossing boundaries.
- Ensure chat-visible work requested through a chat surface is delivered or visibly failed in the correct source surface.
- Make retries, duplicates, failures, and state transitions idempotent and auditable.
- Prevent summarized context, runtime continuation text, or forwarded briefs from becoming fresh human authorization.
- Provide enough audit evidence for production and enterprise review without storing unnecessary private content.

## Assets

| Asset | Sensitivity | Owner |
| --- | --- | --- |
| Bus-message envelope | Internal / sensitive metadata | Product owner / operator |
| Authorization context | Sensitive | Product owner / operator |
| Source and target provenance | Sensitive metadata | Product owner / operator |
| Context package | Variable; can include private or confidential references | Source workspace/project owner |
| Private memory and project context | Private / sensitive | Relevant workspace/project owner |
| Agent credentials and runtime tokens | Secret | Operator |
| Tool capabilities and permissions | Sensitive / privileged | Operator |
| State transition log | Internal / audit-sensitive | Operator |
| Delivery receipt | Internal / audit-sensitive | Operator |
| Rejection/failure reason | Internal; may reveal policy details | Operator |
| RedshieldWarden policy decisions | Sensitive / governance evidence | Operator / enterprise customer |
| RedshieldArmor enforcement decisions | Sensitive / security evidence | Operator / enterprise customer |
| Open-source release artifacts | Public / supply-chain sensitive | Maintainer |
| Enterprise evidence artifacts | Confidential / customer-facing | Operator / enterprise customer |

## Actors

- Product owner: sets product direction, accepts risk, approves external/public actions, and approves releases.
- Agent participant: creates, claims, acts on, or completes bus messages.
- Operator: diagnoses routing, delivery, policy, and incident failures.
- Conversation participant: receives visible status in the surface where work was requested.
- Maintainer: reviews code, releases, vulnerabilities, and open-source governance.
- Enterprise reviewer: evaluates controls, evidence, posture, and integration risk.
- External attacker: attempts spoofing, replay, injection, denial of service, or data theft.
- Malicious or compromised agent: abuses legitimate permissions or attempts to route unsafe work.
- Malicious insider: abuses operator or maintainer access.
- Abusive user: sends prompt-injection-like or policy-bypassing requests through a supported chat surface.

## Trust Boundaries

- Source chat/workspace surface to Agent Bus.
- Source agent/runtime to Agent Bus.
- Agent Bus to target agent/runtime.
- Agent Bus to project repositories and local files.
- Agent Bus to external tools, public services, or side-effecting APIs.
- Agent Bus to future RedshieldWarden policy service.
- Agent Bus to future RedshieldArmor enforcement layer.
- Private memory stores to context packages.
- Internal audit evidence to customer-facing security posture material.
- Open-source public repository boundary.
- Enterprise integration boundary.

## Data Flows

Diagrams:

- `docs/architecture/diagrams/agent-bus-data-flow.html`
- `docs/architecture/diagrams/agent-bus-trust-boundaries.html`

Identity and authentication model:

- `docs/security/AGENT_IDENTITY_AUTHENTICATION.md`
- `docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md`

1. Source request arrives in a chat/workspace/runtime surface.
2. Source agent builds a scoped bus-message envelope.
3. Agent Bus assigns trusted timestamps and validates required envelope fields.
4. Agent Bus rejects, queues, or routes the message.
5. Target agent/runtime claims the message.
6. Target agent acts within the authorization context and context package.
7. Target records state transitions and result.
8. Agent Bus records completion/failure and delivery receipt or delivery failure.
9. Source surface, operator surface, project file, or follow-up bus message receives the declared result path.

## Threats And Abuse Cases

| ID | Threat / Abuse Case | Impact | Existing Control | Needed Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| TH-1 | Spoofed source agent creates a message that appears authorized. | Unauthorized work, data access, or tool use. | Envelope requires source and requester fields. Agent identity/authentication model defines required actor binding; first local credential format is selected. | Implement verifier/runtime checks for authenticated actor identity, credential status, and source binding. | Started |
| TH-2 | Target ambiguity routes work to the wrong agent, workspace, or project. | Private-data exposure, wrong action, lost accountability. | Target field required. | Deterministic resolver, ambiguity rejection, route preview/audit record. | Open |
| TH-3 | Summarized context is treated as fresh human command authorization. | Authorization laundering and unsafe action. | Validation rule rejects this pattern. Authorization-context schema now requires concrete source/approval events and rejects summaries as authority. | Implement verifier tests for summarized-context authorization laundering. | Started |
| TH-4 | Replay or duplicate message causes repeated external or destructive action. | Duplicate side effects, data damage, customer impact. | `idempotency_key` required. | Idempotency conflict checks and side-effect guards. | Open |
| TH-5 | Expired message is claimed or executed after context changed. | Stale authorization or wrong result. | `expires_at` required. | Expiry enforcement and renewal flow. | Open |
| TH-6 | Private memory or unrelated project context is included in the context package. | Confidentiality breach. | Privacy classification and safety flags required. Context-package redaction and allowlist rules now define reference types, copy modes, privacy classifications, redaction categories, and rejection codes. | Implement verifier checks and later private-data/content scanning. | Started |
| TH-7 | Chat-visible answer is completed privately only. | User-visible failure, audit gap, operational confusion. | Delivery expectation required. | Delivery receipt enforcement and stuck/private-only recovery scanner. | Open |
| TH-8 | Runtime-event continuation text is treated as ordinary project work. | Cross-surface side effects, incident confusion. | Validation rule rejects runtime-event boundary misuse. | Runtime-event classifier and ops-only continuation path. | Open |
| TH-9 | Target agent exceeds delegated authority. | Unauthorized tool use, data access, or public/external action. | Authorization context required. Authorization-context schema defines action classes, safety authorizations, scope, expiry, and rejection codes. | Implement per-action verifier checks, then later RedshieldWarden policy and RedshieldArmor enforcement hooks. | Started |
| TH-10 | Bus audit logs store secrets or unnecessary private content. | Secondary data breach through evidence stores. | Audit record must avoid secrets. | Audit schema with hashes/references, redaction, retention policy. | Open |
| TH-11 | Attacker floods bus with messages or claims work to starve legitimate tasks. | Denial of service, delayed operations. | None yet. | Rate limits, quotas, claim authorization, queue isolation. | Open |
| TH-12 | Malicious or compromised agent forges completion or delivery receipt. | False status, lost work, hidden failure. | State model requires transitions. Agent identity/authentication model requires authenticated transition and delivery actors. | Implement trusted delivery adapter receipts and actor-bound transition validation. | Started |
| TH-13 | Open-source release workflow is compromised. | Supply-chain compromise. | None yet. | Release security gate, pinned CI actions, protected branches, provenance/SBOM plan. | Open |
| TH-14 | Enterprise integration overclaims security/compliance readiness. | Customer trust, legal, and sales risk. | Non-goal prohibits unsupported claims. | Control/evidence register and approved customer-facing security posture. | Open |
| TH-15 | RedshieldWarden policy decision is bypassed or ignored. | Governance control failure. | Open-core Warden policy-result contract and integrated envelope checks exist for baseline local verification. | Mandatory policy decision point before risky live actions once a live Warden exists. | Started |
| TH-16 | RedshieldArmor enforcement is incomplete or inconsistent across adapters. | Boundary bypass and data leakage. | Open-core Armor enforcement-result contract and integrated envelope checks exist for baseline local verification. | Adapter-specific enforcement tests and fail-closed live defaults before live adapters. | Started |

## Security Requirements

- Authenticate participating agents and runtimes before message creation, claim, transition, or completion, using `docs/security/AGENT_IDENTITY_AUTHENTICATION.md` and `docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md` as the current design sources.
- Authorize each message against source, target, requester, interaction type, safety flags, and requested output.
- Reject ambiguous targets and missing provenance.
- Reject external, public, destructive, sensitive, or customer-impacting actions without explicit matching authorization context.
- Treat context packages as scoped references by default; avoid copying raw private memory.
- Enforce idempotency for retries and side-effecting work.
- Enforce expiry before claim and before execution.
- Keep state transitions append-only and actor-attributed.
- Record delivery receipts for chat-visible or external result paths.
- Log hashes, references, decisions, and receipts without logging secrets or unnecessary private content.
- Keep runtime-event continuation handling separate from ordinary project work.
- Require release security gates before public/open-source release or production deployment.
- Require control/evidence support before enterprise security/compliance posture claims.

## Security Acceptance Criteria

- A verifier rejects bus-message samples with missing provenance, ambiguous target, unsupported interaction type, expired `expires_at`, unsafe external action, incompatible idempotency reuse, private-data leakage, and runtime-event boundary misuse.
- State-transition tests reject invalid transitions and actorless transitions.
- Completion tests require delivery evidence for chat-visible result paths.
- Audit tests confirm sensitive fields are redacted or referenced rather than copied.
- Release-readiness checks block public/open-source release until release-security gate, vulnerability intake, and supply-chain requirements exist.
- Enterprise-readiness checks block Warden/Armor enterprise claims until control/evidence registers and customer-facing security posture are approved.

## Gate 0 Review

Review date: 2026-07-21.

Review scope: local verifier and open-core repository readiness only. This review
does not approve public visibility, a package release, live adapter behavior,
production use, enterprise claims, or customer-facing security posture.

Reviewed evidence:

- `src/agent_bus/verifier.py`
- `src/agent_bus/capability_grant.py`
- `src/agent_bus/credential_provider.py`
- `src/agent_bus/ecosystem_contract.py`
- `tests/test_verifier.py`
- `tests/test_capability_grant.py`
- `tests/test_credential_provider_contract.py`
- `tests/test_ecosystem_contract_examples.py`
- `tests/fixtures/agent_bus/envelopes/`
- `tests/fixtures/agent_bus/transitions/`
- `tests/fixtures/capability_grants/`
- `tests/fixtures/agent_bus/credential_providers/`
- `tests/fixtures/agent_bus/ecosystem/`
- `docs/security/AGENT_IDENTITY_AUTHENTICATION.md`
- `docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md`
- `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`
- `docs/security/CONTEXT_PACKAGE_RULES.md`
- `docs/operations/PROMOTION_GATE.md`

Threat-to-mitigation links:

| Threat | Gate 0 review result | Evidence |
| --- | --- | --- |
| TH-1 | Partly mitigated for local fixtures. Runtime credential verification remains future work. | `tests/fixtures/agent_bus/envelopes/invalid/missing-actor-identity.json`, `tests/fixtures/agent_bus/envelopes/invalid/display-name-only-identity.json`, `tests/fixtures/agent_bus/envelopes/invalid/unknown-credential.json`, `tests/fixtures/agent_bus/credential_providers/` |
| TH-2 | Partly mitigated for explicit ambiguous targets and target-claim mismatch. Full resolver design remains open. | `tests/fixtures/agent_bus/envelopes/invalid/wrong-destination-delivery.json`, `tests/fixtures/agent_bus/transitions/invalid/target-claim-mismatch.json` |
| TH-3 | Mitigated for current local verifier fixtures. | `tests/fixtures/agent_bus/envelopes/invalid/summarized-context-approval.json`, `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md` |
| TH-4 | Mitigated for incompatible local fixture reuse. Side-effect guards remain future live-adapter work. | `tests/fixtures/agent_bus/envelopes/invalid/idempotency-conflict-a.json`, `tests/fixtures/agent_bus/envelopes/invalid/idempotency-conflict-b.json` |
| TH-5 | Mitigated for message, authorization, and credential expiry checks in local fixtures. Renewal flow remains open. | `tests/fixtures/agent_bus/envelopes/invalid/expired-message.json`, `tests/fixtures/agent_bus/credential_providers/expired-credential.json` |
| TH-6 | Mitigated for current private-context fixture leakage checks. Content scanning remains future work. | `tests/fixtures/agent_bus/envelopes/invalid/private-data-leakage.json`, `docs/security/CONTEXT_PACKAGE_RULES.md` |
| TH-7 | Partly mitigated by delivery expectation and wrong-destination checks. Live receipt enforcement remains Gate 1/Gate 2 work. | `tests/fixtures/agent_bus/envelopes/valid/valid-notify-minimal.json`, `tests/fixtures/agent_bus/envelopes/invalid/wrong-destination-delivery.json`, `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md` |
| TH-8 | Mitigated for current local verifier fixtures. Ops-only runtime continuation handling remains implementation work. | `tests/fixtures/agent_bus/envelopes/invalid/runtime-event-misuse.json` |
| TH-9 | Partly mitigated for authorization-context fields, risky-action authorization, scope, expiry, capability-grant mapping, and public ecosystem contract examples. Warden/Armor live enforcement remains open. | `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`, `src/agent_bus/capability_grant.py`, `src/agent_bus/ecosystem_contract.py`, `tests/fixtures/capability_grants/`, `tests/fixtures/agent_bus/ecosystem/` |
| TH-10 | Partly mitigated by fixture audit shape and redaction rules. Retention and evidence export policy remain open. | `docs/architecture/FIXTURE_AUDIT_STORAGE.md`, `docs/security/CONTEXT_PACKAGE_RULES.md` |
| TH-11 | Not mitigated in Gate 0. Track rate limits, quotas, claim authorization, and queue isolation before live/shared use. | `docs/operations/PROMOTION_GATE.md` |
| TH-12 | Partly mitigated for actor-bound transitions. Trusted adapter receipts remain Gate 1/Gate 2 work. | `tests/fixtures/agent_bus/transitions/invalid/actorless-transition.json`, `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md` |
| TH-13 | Not mitigated yet. Blocks public visibility and package release until governance and supply-chain release gates are complete. | `docs/release/OPEN_CORE_RELEASE_CHECKLIST.md`, `docs/operations/PROMOTION_GATE.md` |
| TH-14 | Not mitigated yet. Blocks enterprise/customer-facing posture claims. | `docs/operations/PROMOTION_GATE.md` |
| TH-15 | Partly mitigated for local fixtures by Warden result contract checks and envelope binding checks. Live policy hook enforcement remains future work. | `src/agent_bus/warden_policy.py`, `tests/fixtures/warden_policy/`, `tests/fixtures/agent_bus/envelopes/valid/valid-notify-with-warden-armor.json` |
| TH-16 | Partly mitigated for local fixtures by Armor result contract checks and envelope binding checks. Live adapter enforcement remains future work. | `src/agent_bus/armor_enforcement.py`, `tests/fixtures/armor_enforcement/`, `tests/fixtures/agent_bus/envelopes/valid/valid-notify-with-warden-armor.json` |

Gate 0 decision: approved with conditions for continued local-verifier and
open-core preparation work. The current mitigations are sufficient to keep
building the local verifier and public-target repository while the remaining
findings stay explicit backlog. They are not sufficient for public release or
live adapter promotion.

## Open Findings

- OF-1: Agent identity and authentication model is defined in `docs/security/AGENT_IDENTITY_AUTHENTICATION.md`, and the first local credential format is selected in `docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md`; implementation and verifier tests are still required.
- OF-2: Authorization-context schema is defined in `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`; verifier implementation and tests are still required.
- OF-3: Context-package redaction and allowlist rules are defined in `docs/security/CONTEXT_PACKAGE_RULES.md`; verifier implementation and tests are still required.
- OF-4: Idempotency conflict behavior is not specified beyond the requirement.
- OF-5: Audit retention, redaction, and evidence-export policy is not defined.
- OF-6: Delivery adapter receipt model is not defined.
- OF-7: Runtime-event boundary classifier is not designed.
- OF-8: Baseline open-core RedshieldWarden policy-result contract and local envelope binding checks exist; live Warden policy hook enforcement is not implemented.
- OF-9: Baseline open-core RedshieldArmor enforcement-result contract and local envelope binding checks exist; live Armor enforcement is not implemented.
- OF-10: Open-source release security gate is missing.
- OF-11: Enterprise control/evidence registers are missing.

## Approval

- Reviewer: Product owner approval recorded from the Discord project channel.
- Date: 2026-07-21.
- Conditions: Approved only for Gate 0 local-verifier and open-core preparation work. Do not use this as public-release approval, live-adapter approval, production approval, enterprise-readiness approval, or customer-facing security posture.
