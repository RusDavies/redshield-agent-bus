# Agent Identity And Authentication Model

## Purpose

Redshield Agent Bus needs authenticated agent identity before it can safely route, claim, or complete work. This model defines the principals, identity fields, credential expectations, trust rules, and first-slice checks required to close the initial threat-model gap for agent identity and authentication.

This is a design artifact, not production approval. It defines the minimum model that future schema, verifier, and runtime work must implement.

## Security Goals

- Bind each bus-message creation, claim, state transition, and completion to an authenticated actor.
- Distinguish human requesters, source agents, target agents, runtimes, workspaces, projects, and delivery adapters.
- Prevent summarized context, forwarded messages, or runtime continuation text from becoming authenticated human approval.
- Make replay, impersonation, wrong-runtime execution, and forged completion detectable.
- Keep credentials and secrets out of message envelopes and audit records.

## Principals

| Principal | Description | Authentication Need |
| --- | --- | --- |
| Human requester | Person who initiated or approved work. | Source-surface assertion plus captured message provenance; explicit approvals must reference the concrete source event. |
| Source agent | Agent that constructs the bus message. | Runtime-issued agent identity and workspace/project binding. |
| Target agent | Agent or role that claims and executes work. | Runtime-issued agent identity, role binding, and capability/route authorization. |
| Runtime | OpenClaw, ACP, Codex, or other execution environment hosting an agent. | Runtime identity and trusted-origin channel to the bus. |
| Workspace/project | Scope whose private context, files, or git repo may be referenced. | Resolved scope id with verified mapping before project operations. |
| Delivery adapter | Surface adapter that posts or records results. | Adapter identity plus receipt binding for visible/external delivery. |
| Operator | Human or privileged automation diagnosing routing and incidents. | Operator identity with auditable administrative action reason. |

## Stable Identifiers

Agent Bus should treat display names as labels only. Authorization decisions must use stable identifiers:

- `agent_id`: stable unique id for a configured agent identity.
- `agent_role`: optional role such as `source`, `target`, `reviewer`, `operator`, `warden`, or `delivery_adapter`.
- `runtime_id`: stable id for the runtime instance hosting the agent.
- `workspace_id`: stable id for the workspace that owns context and configuration.
- `project_slug`: normalized project scope, when a message is project-bound.
- `source_surface`: surface such as `discord`, `tui`, `whatsapp`, `openclaw`, or `acp`.
- `source_conversation_id`: stable source conversation/channel/thread/session id.
- `source_event_id`: source message/event id for the originating request or approval.
- `requester_id`: stable human or system requester id, when known.
- `credential_id`: opaque id for the credential used to authenticate the actor. The secret itself must never appear in the envelope.

## Credential Model

For the first slice, the bus should support a trusted local/runtime credential model before introducing distributed signing:

1. Runtimes authenticate to the bus over a trusted local channel, service account, or configured runtime token.
2. Agents authenticate through the runtime, which asserts `agent_id`, `runtime_id`, allowed roles, and scope bindings.
3. Delivery adapters authenticate as adapter principals rather than as ordinary agents.
4. Each accepted envelope records `credential_id`, `authenticated_at`, and `auth_method`, but not credential material.
5. Credential rotation invalidates future use of the old credential without rewriting historical audit records.

Future distributed or multi-host operation should add signed envelopes or mutually authenticated transport. That later design must preserve the same actor-bound audit semantics.

The first local runtime credential format is selected in `docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md`: `local_runtime_token`, backed by a local credential registry with opaque credential ids, actor/runtime/scope bindings, status, expiry metadata, and secret hashes kept outside envelopes, fixtures, audit records, and receipts.

Future provider swappability is discussed in `docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md`. Agent Bus should depend on a narrow credential capability contract rather than on Keyper, Smallstep, OpenBao, SPIFFE/SPIRE, OIDC, mTLS, or any other provider directly.

## Required Envelope Fields

The message envelope must include the following authenticated identity fields:

- `auth.actor_id`: authenticated agent, adapter, runtime, or operator id creating the envelope or transition.
- `auth.actor_type`: `agent`, `runtime`, `adapter`, `operator`, or `system`.
- `auth.runtime_id`: runtime asserting the actor identity, when applicable.
- `auth.credential_id`: opaque credential reference used for authentication.
- `auth.auth_method`: method such as `local_runtime_token`, `service_account`, `mTLS`, or `signed_envelope`.
- `auth.authenticated_at`: trusted timestamp assigned by the bus or trusted runtime.
- `source.source_agent_id`: source agent constructing the request.
- `source.runtime_id`: source runtime.
- `source.workspace_id`: source workspace.
- `source.source_event_id`: concrete event that caused the message, when available.
- `requester.requester_id`: requester id, when known.
- `requester.approval_event_ids`: explicit source events that grant approval, when required.
- `target.target_agent_id` or `target.target_role`: specific destination identity or resolvable role.
- `target.allowed_runtime_ids`: optional allowlist for runtimes that may claim the message.

The bus, not the source agent, should assign trusted `created_at`, validation result, and state-transition timestamps.

## Authentication Rules

- Reject any message that lacks an authenticated source actor.
- Reject any message whose `source_agent_id` is not bound to the authenticated actor or runtime.
- Reject any target claim where the claiming actor does not match the resolved `target_agent_id`, `target_role`, workspace, project, or allowed runtime.
- Reject state transitions without an authenticated transition actor.
- Reject completion or delivery receipts from actors that are neither the claimant nor an authorized delivery adapter.
- Reject messages whose explicit approvals reference no concrete source event.
- Reject messages that cite summarized context, continuation notes, compacted summaries, or inferred intent as approval.
- Reject expired, revoked, disabled, or unknown credentials.
- Reject ambiguous display-name-only identities.

## Authorization Handoff

Authentication proves who the actor is; it does not prove the actor may perform the requested action. After authentication, the bus must pass the authenticated identity and scoped request into the authorization-context checks.

The current first-slice authorization-context schema is defined in `docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md`.

The authorization layer must receive:

- authenticated actor id and role;
- source surface and event provenance;
- requester id and approval event ids;
- target identity and runtime;
- workspace/project scope;
- requested interaction type and safety flags;
- delivery expectation;
- credential trust level.

This keeps identity and authorization separate. Boring, yes. Also how we avoid building a permission soup with a logo.

## Audit Evidence

Audit records must store:

- actor id, actor type, runtime id, and credential id;
- authentication result and failure reason;
- transition actor for every state change;
- envelope hash and auth-relevant field hashes;
- approval event references, not copied private message bodies;
- delivery adapter identity and delivery receipt id;
- credential revocation status at validation time, when known.

Audit records must not store credential secrets, raw tokens, private memory, unnecessary chat content, or unrelated project context.

## Failure Handling

Authentication failures are terminal validation failures for the affected message or transition:

- message creation failure records `rejected` with `auth_failed`;
- claim failure leaves the message claimable by other authorized targets until expiry;
- transition failure records an audit event without changing message state;
- forged completion or receipt is recorded as `rejected_transition` and should create a security-review follow-up item.

Repeated authentication failures from the same actor, runtime, credential, or source should be rate-limited and surfaced to operations.

## First-Slice Acceptance Criteria

- Sample envelopes include authenticated source, target claim, transition, and delivery actors.
- The verifier rejects missing actor identity, unknown credential id, display-name-only identity, target-claim mismatch, actorless transitions, and summarized-context approvals.
- Threat-model checks for spoofed source agents, forged completion, target ambiguity, and authorization laundering reference this model.
- No sample, audit fixture, or documentation example includes credential secrets.

## Open Questions

- Should project/workspace scope binding live in static config, a local registry, or the future Agent Hub?
- What minimum credential rotation and revocation evidence is needed before production use?
- Which fields become public open-source defaults, and which remain operator-local configuration?
