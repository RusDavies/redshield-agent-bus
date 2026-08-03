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

## Core Value

The core gives adopters a local verifier and contract set that can answer:

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
team validation before live deployment.

## Scope Boundaries

The project defines protocol semantics, verifier behavior, fixture contracts,
and release gates. It does not include a production broker, live adapter service,
hosted operations console, organization policy engine, or deployment platform.

Future live use needs explicit promotion evidence, rollback paths, and human
approval for the specific runtime and surface involved.
