# Product Overview

Redshield Agent Bus is a typed coordination layer for agent work.

It is for teams building agents, tools, or workflows that need safer handoffs
than copied chat text, summarized context, or informal session notes can
provide.

## Problem

Agent work often crosses boundaries:

- one agent asks another agent to act;
- one runtime hands work to another runtime;
- a tool call needs explicit authority;
- a result must be visibly delivered somewhere;
- private context must be referenced without being copied;
- retries must not duplicate risky side effects;
- operators need evidence when work stalls, misroutes, or completes privately.

Without a typed bus model, those boundaries become convention and guesswork.

## Open-Core Value

The open core gives adopters a local verifier and contract set that can answer:

- Is this handoff well formed?
- Who is acting?
- What authority is claimed?
- Is the target unambiguous?
- Is the context package scoped and redacted?
- Is the request fresh and non-duplicated?
- Does the delivery expectation make sense?
- Would baseline policy require review?
- Would baseline enforcement block or sanitize unsafe content?

That is useful for local development, CI checks, adapter development, and
small-team validation before any paid service exists.

## Commercial Boundary

Commercial editions should make the open-core safety model easier to operate
across organizations and production systems.

Paid value may include:

- organization policy and approval workflows;
- deployed runtime enforcement;
- admin visibility and Agent Hub workflows;
- connector-specific controls;
- evidence and audit exports;
- managed operations and support.

Paid features should not be required for the basic verifier, protocol semantics,
local safety model, or baseline Warden/Armor result contracts.
