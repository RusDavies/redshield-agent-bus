# Release Candidate Evidence

No public release is approved.

This file records the current release-infrastructure readiness snapshot. It is
not a release approval and must be replaced by a candidate-specific evidence
record before a real public release.

Candidate-specific release-admin evidence now exists at
`docs/release/candidates/2026-07-23-release-admin-gate/PROVENANCE.md`.
That record documents the private-repository branch-protection blocker,
the preferred protected publishing path, locally built artifact hashes, SBOM
location, and rollback evidence. It remains evidence only, not approval.

## Candidate

- Version: not selected
- Tag: not selected
- Release commit: not selected
- Repository: `RusDavies/redshield-agent-bus`
- Package index: not selected
- Release owner: not selected
- Approval date: not approved
- Approver: not approved

## Infrastructure Snapshot

- CI workflow present: `.github/workflows/ci.yml`
- CI permission posture: read-only repository contents
- Public release controls: `docs/release/PUBLIC_RELEASE_INFRASTRUCTURE_CONTROLS.md`
- Release security gate: `docs/release/RELEASE_SECURITY_GATE.md`
- Package provenance controls: `docs/release/PACKAGE_PROVENANCE_CONTROLS.md`
- Release evidence template: `docs/release/RELEASE_EVIDENCE_TEMPLATE.md`
- Current release-admin candidate evidence:
  `docs/release/candidates/2026-07-23-release-admin-gate/PROVENANCE.md`

## Current Local Verification Commands

```sh
python3 scripts/verify_repo.py open-core
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

## SBOM Status

- SBOM format: not selected
- SBOM generator: not selected
- Runtime dependencies: none declared
- Build/test dependencies: see `pyproject.toml`
- Candidate SBOM artifact:
  `docs/release/candidates/2026-07-23-release-admin-gate/sbom.spdx.json`

## Rollback Status

- Commit revert or forward-fix path: use normal git review and protected-branch
  flow once branch protection is enabled.
- Package yank/supersede path: not applicable until a package index is selected.
- Release workflow disable path: disable or revert the release workflow before
  publication support is added.
- Credential rotation path: not applicable until publishing credentials exist.

## Blocking Conditions

- No public release approval exists.
- Default-branch protection is blocked while the repository remains private on
  the current GitHub plan; the GitHub API returned `403` during verification.
- No candidate-specific package artifacts exist.
- No package publishing workflow exists.
- Package license metadata uses deprecated setuptools forms and should be
  modernized before public package publication.
- No customer-facing security claim is approved.
