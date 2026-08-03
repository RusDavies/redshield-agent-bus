# Release Security Gate

No public release is approved yet.

This gate must pass before changing repository visibility, publishing a package,
tagging a public release, or making customer-facing security claims about
Redshield Agent Bus.

## Required Evidence

- `LICENSE` is present and selected deliberately.
- `CONTRIBUTING.md` is present and keeps fixtures, tests, and docs public-safe.
- `SECURITY.md` is present and defines a private vulnerability intake path that
  does not publish personal email addresses.
- `docs/release/CORE_RELEASE_CHECKLIST.md` is current.
- `docs/release/PACKAGE_PROVENANCE_CONTROLS.md` is current.
- `docs/release/PUBLIC_RELEASE_INFRASTRUCTURE_CONTROLS.md` is current.
- `.github/workflows/ci.yml` exists and passes for the release candidate.
- A release-specific evidence file has been copied from
  `docs/release/RELEASE_EVIDENCE_TEMPLATE.md` and completed.
- `README.md` and public docs describe stand-alone verifier value without
  customer-specific, deployment-specific, or launch-plan assumptions.
- Package metadata identifies the selected license and supported Python version.
- Local verifier commands pass against public fixtures.
- Python tests pass in a documented environment.
- `python3 scripts/verify_repo.py core` passes.
- CI status checks for the release candidate pass.
- Public fixtures contain only fake identities, references, channels, runtime
  ids, tokens, and customer data.
- Keyper-style, Warden-style, Armor-style, and capability-grant examples remain
  public contract examples, not hard dependencies on private products.
- Release notes or a changelog identify user-visible changes, security-relevant
  changes, and known limitations.

## Supply-Chain Checks

- Dependencies are reviewed before release; the current package has no runtime
  dependencies.
- Test dependencies are pinned by acceptable lower bounds and installed in an
  isolated environment for release verification.
- Build artifacts are generated from a clean repository state.
- The release commit, tag, package artifact, and verification commands are
  recorded in release evidence.
- Any future CI release workflow must use protected branches, minimal tokens,
  pinned third-party actions, and a documented rollback path.
- The default branch must use branch protection or an equivalent ruleset before
  release.
- Package provenance controls must define protected source, CI/runner controls,
  artifact provenance, SBOM expectations, and rollback/recovery expectations.

## Blocking Conditions

Stop the release when any of these are true:

- a critical or high-severity vulnerability affecting the verifier, fixture set,
  release workflow, or package integrity is unresolved;
- fixtures include real secrets, private messages, customer data, production
  runtime ids, live channel ids, or personal contact data;
- live adapter behavior, production use, public/external actions, or customer
  security claims are implied by the release without explicit approval;
- provenance for the release commit, package artifact, or verification result is
  missing;
- the core repository contains customer-specific, deployment-specific, or
  launch-plan material.

## Approval Record

A release approval record must name:

- release commit;
- version and tag;
- verifier and test commands with results;
- package artifact and checksum if packaging occurs;
- open risks and accepted-risk owner;
- approval date and approver.
