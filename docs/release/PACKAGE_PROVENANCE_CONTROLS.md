# Package Provenance Controls

No public package release is approved yet.

These controls define the minimum release-integrity posture for a future
Redshield Agent Bus public package. They apply before publishing to PyPI or any
other package index, creating a public release tag, or changing the repository
visibility for release purposes.

## Protected Source

- Release commits must come from the protected default branch.
- Direct pushes to the protected branch must be disabled for normal
  maintainers.
- Required status checks must include the local verifier profile and Python
  test suite.
- A maintainer review is required for release, security, fixture, and workflow
  changes.
- Repository administrators must review branch-protection settings before the
  first public release and after any release-workflow change.

## CI And Runner Controls

Use GitHub Actions only after the workflow is explicitly reviewed for release
use. If a different runner is selected, record equivalent controls in the
release evidence.

Minimum GitHub Actions controls:

- workflows run with least-privilege `permissions`;
- package publishing uses a protected environment or trusted publishing;
- third-party actions are pinned to immutable commit SHAs;
- first-party GitHub actions are pinned to reviewed major versions or immutable
  SHAs, with the choice recorded in release evidence;
- release workflows do not run on untrusted pull-request code with package
  publishing credentials available;
- generated artifacts are uploaded from the same checked-out commit recorded in
  the release evidence;
- secrets are not printed, copied into fixtures, or stored in build artifacts.

## Build Artifact Provenance

Every release must record:

- source repository and release commit SHA;
- tag and version;
- Python version and build backend;
- exact build command;
- generated distribution filenames;
- SHA-256 digest for each distribution artifact;
- test and verifier commands with results;
- release approver and approval date.

The build must start from a clean working tree. If generated artifacts differ
between local and CI builds, stop the release until the difference is explained
and recorded.

## SBOM Expectation

Before the first public package release, choose and document an SBOM format,
normally SPDX or CycloneDX.

The SBOM must cover:

- the package source version;
- runtime dependencies, even when the list is empty;
- build and test dependencies used to produce release evidence;
- license metadata for direct dependencies;
- the tool and version used to generate the SBOM.

If the package still has no runtime dependencies, record that explicitly rather
than omitting SBOM evidence. Boring is fine. Ambiguous is not.

## Rollback And Recovery

Before release, document the rollback path for:

- reverting the release commit or follow-up regression fix;
- yanking or superseding a broken package version;
- removing or replacing a compromised release artifact where the package index
  permits it;
- revoking or rotating release credentials;
- disabling the release workflow;
- publishing a security advisory or post-release correction.

Rollback evidence must name the owner, commands or administrative path, expected
blast radius, and any action that requires human approval.

## Release Evidence File

Use `docs/release/RELEASE_EVIDENCE_TEMPLATE.md` as the minimum release approval
record. A real release evidence file should be copied from the template and
filled in for the specific version under review.

