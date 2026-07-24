# Release Admin Gate Candidate Provenance

No public release is approved.

This record captures release-administration evidence gathered on 2026-07-23
for the private `RusDavies/redshield-agent-bus` repository. It does not approve
public repository visibility, a release tag, package publication, live adapter
behavior, production use, or customer-facing security claims.

## Candidate Scope

- Candidate kind: release-admin-gate evidence.
- Repository: `RusDavies/redshield-agent-bus`.
- Repository visibility at inspection: private.
- Default branch: `main`.
- Source commit inspected: `1c7491b2c644ca109b61a7ae0c2fb9b9adf7d57a`.
- Version declared by package metadata: `0.1.0`.
- Package index: not selected.
- Release tag: not selected.
- Release owner: not selected.
- Approver: not approved.

## GitHub Controls

- CI workflow present: `.github/workflows/ci.yml`.
- CI workflow permission posture: `contents: read`.
- CI workflow status: latest `Verify open core` run for commit
  `1c7491b2c644ca109b61a7ae0c2fb9b9adf7d57a` succeeded.
- Branch protection check: GitHub API returned `403` for
  `GET /repos/RusDavies/redshield-agent-bus/branches/main/protection`.
- Branch protection blocker: GitHub reported that branch protection for this
  private repository requires GitHub Pro or making the repository public.
- Action taken: no repository visibility change was made.

Default-branch protection therefore remains a release blocker. Before a public
release, an administrator must either enable the required protection after the
plan/visibility blocker is resolved or approve and document an equivalent
control path.

## Publishing Choice

Preferred package publication path:

- PyPI trusted publishing through GitHub Actions OpenID Connect.
- A protected release environment for publishing jobs.
- No long-lived package index token committed to the repository or stored in
  ordinary CI variables.

No package publishing workflow or publishing credential was configured during
this gate.

## Local Build Evidence

Build command:

```sh
rm -rf dist build *.egg-info
.venv/bin/python -m build
```

Build environment:

- Python: `Python 3.14.5`.
- Build backend: setuptools through `pyproject.toml`.
- Editable package source before build:
  `redshield-agent-bus @ file:///home/skippy/.openclaw/workspace/projects/redshield-agent-bus`.

Build and test dependencies observed in the verification environment:

- `build==1.5.0`
- `iniconfig==2.3.0`
- `packaging==26.2`
- `pluggy==1.6.0`
- `Pygments==2.20.0`
- `pyproject_hooks==1.2.0`
- `pytest==9.1.1`

Distribution artifacts were built locally and not committed.

Artifact hashes:

```text
cf8adfd0d6afe2601c1abacd9f966f713da67a311dedfbf94e3909fb13807e0b  dist/redshield_agent_bus-0.1.0-py3-none-any.whl
f1f286ce8a4ef3f224900f1cbf00e6745650b4601d2aef20ddcf6c149c2f6a12  dist/redshield_agent_bus-0.1.0.tar.gz
```

Build warnings:

- Setuptools reported deprecation warnings for `project.license` as a TOML
  table and license classifiers. Package metadata should move to modern SPDX
  license expressions before the first public package release.
- Pip emitted cache deserialization warnings. These did not affect package
  contents but should not be treated as release provenance by themselves.

Superseding note:

- The package metadata warning was addressed after this candidate snapshot by
  moving `pyproject.toml` to PEP 639 license metadata:
  `License-Expression: Apache-2.0` and `License-File: LICENSE`. Regenerate
  candidate artifacts before any real public release.

## SBOM

- SBOM format selected for this candidate: SPDX 2.3 JSON.
- SBOM file: `sbom.spdx.json`.
- Runtime dependencies: none declared.
- Build/test dependencies: listed in this evidence record and in the SBOM.
- SBOM generation method: manual candidate inventory from package metadata,
  local build environment output, and artifact hashes.

## Rollback Evidence

- Source rollback: revert the release commit or forward-fix from a reviewed
  branch after branch protection or an equivalent source control is active.
- Workflow rollback: disable or revert the release workflow before publication
  support is added.
- Package rollback: not applicable until a package index is selected; once a
  package is published, record the index-specific yank, supersede, and advisory
  path in the release evidence.
- Credential rollback: not applicable until publishing credentials exist; if
  trusted publishing is used, rotate or remove the PyPI trusted publisher binding
  and disable the protected release environment.
- Repository visibility rollback: no visibility change was made in this gate.

## Blocking Conditions

- No public release approval exists.
- Default-branch protection could not be enabled or verified while the repo is
  private on the current GitHub plan.
- No release tag is selected.
- No package index is selected.
- No package publishing workflow exists.
- No protected release environment exists.
- This historical candidate's artifacts predate the PEP 639 license metadata
  cleanup; regenerate candidate artifacts before any real public release.
