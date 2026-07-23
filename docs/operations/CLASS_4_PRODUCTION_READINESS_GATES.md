# Class 4 Production Readiness Gates

## Purpose

These gates define the minimum production-readiness evidence required before
Redshield Agent Bus can be used for shared or production infrastructure work.

They do not approve production use, public release, live adapters, enterprise
claims, or customer-facing security posture. They define the checks that must
pass before those decisions can be considered.

## Gate Summary

A Gate 3 shared or production promotion must pass all Class 4 gates:

- G1: production scope and ownership;
- G2: operational runbook;
- G3: monitoring and stuck-work detection;
- G4: incident intake and escalation;
- G5: rollback and disable path;
- G6: backup, restore, and audit retention;
- G7: security and privacy controls;
- G8: release approval and change control;
- G9: post-promotion review.

Any failed gate blocks promotion unless an accepted-risk record names the owner,
expiry, compensating controls, and rollback path.

## G1: Production Scope And Ownership

Required evidence:

- named production or shared-use scope;
- source and destination surfaces;
- allowed interaction types and action classes;
- owner and backup owner;
- operator coverage expectation;
- out-of-scope surfaces, adapters, tools, and action classes;
- customer-impacting and enterprise-impacting boundaries.

Blocking conditions:

- scope is described only by a broad label such as "production";
- owner or backup owner is missing;
- shared-channel, customer, public, destructive, or external behavior is
  implied but not explicitly approved.

## G2: Operational Runbook

Required evidence:

- start, stop, disable, and health-check procedures;
- configuration locations and change process;
- log locations and retention expectations;
- delivery receipt inspection path;
- stuck-work inspection path;
- operator commands or administrative paths;
- escalation contacts or channels;
- known failure modes and first response.

Blocking conditions:

- an operator cannot identify whether the bus is enabled;
- disable steps are missing or untested;
- receipt or stuck-work inspection requires private tribal knowledge. Yes, the
  sacred oral tradition of "ask whoever touched it last" remains banned.

## G3: Monitoring And Stuck-Work Detection

Required evidence:

- health signal for the bus component or adapter;
- queue or pending-work age signal where queues exist;
- delivery receipt success/failure metrics;
- wrong-destination and private-only completion detection;
- policy/enforcement denial and block counts;
- alert thresholds and destination;
- expected manual review cadence.

Blocking conditions:

- failures are visible only after a user complains;
- no alert exists for missing receipts or stale in-flight work;
- monitoring emits private message bodies, secrets, or customer data.

## G4: Incident Intake And Escalation

Required evidence:

- incident intake path;
- severity categories;
- escalation route for wrong-destination delivery, private data leakage,
  unauthorized action, stuck work, and runtime-event boundary confusion;
- containment steps;
- communication expectations for source channels and operators;
- post-incident evidence requirements.

Blocking conditions:

- runtime-event continuation text can enter ordinary project flow;
- incident response has no owner;
- private data leakage lacks an immediate containment and notification path.

## G5: Rollback And Disable Path

Required evidence:

- feature flag, config switch, or equivalent hard disable;
- per-adapter disable path;
- rollback command or administrative procedure;
- rollback test result;
- expected user-visible behavior while disabled;
- conditions that automatically stop promotion or revert to the previous gate.

Blocking conditions:

- live behavior cannot be disabled without code changes;
- rollback requires unreviewed destructive action;
- disabling the bus silently drops work instead of failing visibly.

## G6: Backup, Restore, And Audit Retention

Required evidence:

- state that must be backed up;
- state that must not be backed up because it is secret or private;
- restore procedure and test result where durable state exists;
- audit retention duration;
- redaction and minimization rules;
- evidence export owner and approval path.

Blocking conditions:

- restore has never been tested for durable routing or audit state;
- audit records contain raw secrets, private messages, or unnecessary customer
  content;
- retention is undefined for production or customer-impacting evidence.

## G7: Security And Privacy Controls

Required evidence:

- authenticated actor and runtime identity checks;
- authorization-context checks for allowed action classes;
- Warden policy result requirement for risky live actions;
- Armor enforcement result requirement for private/sensitive payloads;
- private-data redaction and allowlist rules;
- idempotency, expiry, and replay controls;
- rate limit, quota, or claim-authorization control for shared use;
- current control-register review with mapped risks, threats, gate
  expectations, and control status;
- vulnerability intake path and open-finding review.

Blocking conditions:

- risky action classes can run on summarized, stale, or inferred approval;
- Warden/Armor evidence is bypassable for actions that require it;
- rate limiting or claim authorization is absent for shared-use queues.

## G8: Release Approval And Change Control

Required evidence:

- release candidate commit;
- verifier and test command results;
- operational gate evidence;
- open risks and accepted-risk owner;
- current risk-register review;
- current control-register review;
- rollback plan;
- approval event naming scope, duration, and allowed behavior;
- public-release evidence when repository visibility or package publishing is
  involved.

Blocking conditions:

- approval is broad, stale, or copied from a summary;
- release evidence does not bind to a commit;
- public release or customer-facing claims are bundled into a production
  approval without their own gates.

## G9: Post-Promotion Review

Required evidence:

- review date and owner;
- observed incidents, failed deliveries, stuck work, denials, and rollbacks;
- user-visible failure reports;
- false positives and false negatives for Warden/Armor decisions;
- action items and gate changes.

Blocking conditions:

- no review date is scheduled;
- incidents or missing receipts are not reviewed;
- continued production use relies on expired accepted risk.

## Promotion Decision Record

Every Class 4 promotion decision must record:

- target gate;
- production/shared-use scope;
- evidence files;
- verification commands and results;
- unresolved blockers;
- accepted risks with owner and expiry;
- rollback or disable result;
- approval event;
- next review date.
