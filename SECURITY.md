# Security Policy

Redshield Agent Bus is pre-release and has not been approved for public
visibility, package release, production deployment, live adapter use, or
customer-facing security claims.

## Supported Versions

No stable public version is supported yet. Security fixes should target the
current main branch until a release support policy exists.

## Reporting A Vulnerability

Use GitHub private vulnerability reporting or a private security advisory for
this repository. Do not file public issues for vulnerabilities that expose
private data, bypass authorization, enable live side effects, weaken verifier
fail-closed behavior, or affect release integrity.

If private vulnerability reporting is unavailable, request a private advisory
channel through the repository owner on GitHub. Do not publish personal email
addresses in this repository or in public issue text.

## Scope

Please report suspected vulnerabilities involving:

- spoofed or unauthenticated agent identity;
- authorization-context bypass;
- context-package private data leakage;
- replay, duplicate, or stale-message handling;
- wrong-destination delivery;
- summarized context being treated as fresh approval;
- runtime-event boundary confusion;
- forged completion or delivery receipts;
- Warden policy-result or Armor enforcement-result bypass;
- credential-provider evidence validation failures;
- fixture, release, or package supply-chain integrity.

## Response Expectations

The project should acknowledge private reports, triage the affected verifier or
governance boundary, and link fixes to tests, fixtures, or release-gate evidence
before publishing details. A public release must not proceed while a critical or
high-severity unresolved vulnerability affects the local verifier, release
workflow, or public fixture set.

