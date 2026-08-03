# Release Evidence Template

Copy this template for each release candidate. Do not treat this template as an
approval record by itself.

## Release Candidate

- Version:
- Tag:
- Release commit:
- Repository:
- Package index:
- Release owner:
- Approval date:
- Approver:

## Scope

- Release type:
- User-visible changes:
- Security-relevant changes:
- Known limitations:
- Explicitly out of scope:

## Source Protection

- Protected branch reviewed:
- Required status checks:
- Reviewers:
- Direct push disabled:
- Release workflow reviewed:
- Notes:

## Verification

Record exact commands and results.
Cross-check required evidence classes against
`docs/risk/INITIAL_EVIDENCE_REGISTER.md`.

```sh
python3 scripts/verify_repo.py core
python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
python3 -m pytest
```

## Build Provenance

- Python version:
- Build backend:
- Build command:
- Clean tree confirmed:
- Distribution artifacts:
- Artifact SHA-256 digests:
- CI run or local build evidence:
- Reproducibility notes:

## SBOM

- SBOM format:
- SBOM tool and version:
- Runtime dependencies:
- Build/test dependencies:
- SBOM artifact:
- Notes:

## Vulnerability And Risk Review

- Private vulnerability reports reviewed:
- Open critical/high findings:
- Accepted risks:
- Accepted-risk owner:
- Advisory required:
- Notes:

## Rollback

- Package yank/supersede path:
- Release workflow disable path:
- Credential rotation path:
- Commit revert or forward-fix path:
- Advisory/correction path:
- Rollback owner:

## Approval

- Approved for public repository visibility:
- Approved for package publication:
- Approved for customer-facing claims:
- Approval event/reference:
- Final decision:
