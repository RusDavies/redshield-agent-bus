# Architecture Overview

## Current State

No runtime architecture has been selected. This repository starts with process, requirements, and safety scaffolding.

The current alternatives review in `docs/architecture/ALTERNATIVES_REVIEW.md` selects a repository-local verifier and envelope/state model as the first build-vs-use decision. Existing agent sessions, chat surfaces, local project files, runtime/gateway tools, MCP, and later queues should be treated as adapters around validated bus semantics, not as substitutes for the bus contract.

The first buildable architecture path is selected in `docs/architecture/FIRST_BUILDABLE_PATH.md`: a repository-local verifier driven by static fixtures. Direct message-tool handoff, durable queues, gateway-mediated routing, session-spawn delegation, and project-local inbox files are deferred as integration options until the verifier contract exists.

The local fixture and audit-record storage shape is selected in `docs/architecture/FIXTURE_AUDIT_STORAGE.md`: strict JSON fixtures under `tests/fixtures/agent_bus/`, deterministic JSONL expected audit events, and ignored scratch output under `tmp/agent-bus/`.

The first prototype scope is selected in `docs/requirements/FIRST_PROTOTYPE_SCOPE.md`: local-only fixture verification. Live chat posting, runtime/session integration, gateway routing, MCP exposure, queues, `broadcast`, and `subscribe` are deferred.

The Gate 1 dry-run adapter and receipt boundary is defined in `docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md`. Dry-run adapters model previews and receipts only; they must not post, spawn, send, enqueue, publish, mutate, or call external/runtime services.

Credential provider swappability is recorded in `docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md`. Keyper is a future provider candidate, not a hard dependency; Agent Bus should consume a narrow credential capability contract that can also be backed by local runtime tokens, Smallstep, OpenBao/Vault, SPIFFE/SPIRE, mTLS, OIDC/JWT, static bootstrap tokens, or hardware-backed keys where appropriate.

## Naming Decision

- Redshield Agent Bus is the product/system name.
- `agent-bus` is the implementation/service name.
- Gateway, Hub, Warden, and Armor are component or role names inside the architecture.

## Design Questions

- What is the minimal envelope needed for provenance, authorization, and delivery guarantees?
- Which state belongs in runtime adapters, which belongs in project repos, and
  which belongs in audit or incident records?
- How should receiving agents verify source, target, and project scope before
  acting?
- What later promotion gate allows the local verifier to become a live adapter-backed bus component?
- What credential capability contract is sufficient to compare Keyper and non-Keyper identity providers without hiding security-relevant differences?

## Initial Components To Consider

- Bus-message envelope schema.
- Router or dispatcher.
- Delivery adapter for chat-visible replies.
- Project/context resolver.
- Audit log or evidence register.
- Recovery scanner for stale or privately answered work.
- Agent Gateway for controlled ingress/egress and protocol translation.
- Agent Hub for later human/admin inspection.
- RedshieldWarden policy hooks for authorization and governance.
- RedshieldArmor enforcement hooks for payload and runtime controls.

## Early Constraints

- Requests with visible-delivery obligations must produce auditable delivery
  evidence using the appropriate surface adapter.
- Project-file operations must resolve and verify the intended project scope
  first.
- External/public actions require explicit human approval.
- Runtime-event continuation diagnostics belong in operational context, not
  ordinary project work.
