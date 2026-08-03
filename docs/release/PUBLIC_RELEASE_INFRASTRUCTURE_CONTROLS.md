# Public Release Infrastructure Controls

## Purpose

These controls define the concrete repository-side infrastructure expected
before Redshield Agent Bus can become public, publish a package, tag a release,
or make customer-facing security claims.

This document does not approve public release. It records the controls that
must be present and verified before a separate release approval can be valid.

## Implemented Repository Controls

- GitHub Actions CI workflow: `.github/workflows/ci.yml`.
- Least-privilege workflow permissions: `contents: read`.
- CI verifies the core repository profile.
- CI runs all local fixture verifier commands.
- CI runs the Python test suite.
- Release evidence template requires source protection, verification, build
  provenance, SBOM, vulnerability/risk review, rollback, and final approvals.
- Package provenance controls define protected-source, runner, artifact, SBOM,
  and rollback expectations.

## Branch Protection Requirements

Before changing visibility, tagging a public release, or publishing a package,
repository administrators must enable branch protection or an equivalent ruleset
for the default branch.

Minimum settings:

- require pull request review before merging release, security, fixture, and
  workflow changes;
- require the `Verify core` CI job before merge;
- block force pushes;
- block branch deletion;
- require conversations to be resolved before merge;
- restrict bypass to named administrators;
- review the ruleset after every release-workflow change.

If GitHub branch protection is unavailable, record the equivalent control and
approval path in the candidate release evidence.

Current status: branch protection for the private `RusDavies/redshield-agent-bus`
repository could not be enabled or verified during the 2026-07-23
release-admin gate because GitHub returned a plan/visibility `403`. A follow-up
A1 reattempt on 2026-08-02 still returned the same `403` for both classic branch
protection and repository rulesets while the repository remained private. The
2026-08-02 project decision is to defer GitHub default-branch protection until
the repository is made public under separate explicit public-release approval.
The public release remains blocked until that public-visibility step is approved
and default-branch protection is enabled and verified.

## Publishing Controls

Package publication must use one of:

- PyPI trusted publishing with a protected release environment; or
- an explicitly approved protected token flow with documented rotation and
  revocation path.

Publishing credentials must never be available to untrusted pull-request code.
The current CI workflow does not publish packages.

Current selected direction: PyPI trusted publishing through GitHub Actions
OpenID Connect and a protected release environment. The workflow and PyPI
publisher binding are not configured yet.

## Candidate SBOM And Provenance

Each candidate release must record:

- release commit SHA;
- tag and version;
- Python version and build backend;
- clean tree confirmation;
- exact verifier and test commands with results;
- distribution artifact filenames and SHA-256 digests;
- SBOM format and generator;
- runtime dependencies, even when empty;
- build/test dependencies;
- rollback and credential-rotation path.

Current candidate evidence:
`docs/release/candidates/2026-07-23-release-admin-gate/PROVENANCE.md`.

## Verification

Run local release-control verification:

```sh
python3 scripts/verify_repo.py core
```

Run the same commands the CI workflow runs:

```sh
python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
python3 scripts/agent_bus_verify.py shared-use tests/fixtures/shared_use --pretty
python3 scripts/agent_bus_verify.py live-receipt tests/fixtures/live_receipts --pretty
python3 -m pytest
```

## Still Blocked

These actions remain blocked until a specific release approval exists:

- changing repository visibility;
- tagging a public release;
- publishing to a package index;
- making customer-facing security claims;
- enabling live adapter behavior;
- using the bus in production or shared infrastructure.
