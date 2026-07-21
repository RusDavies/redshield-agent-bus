#!/usr/bin/env python3
"""Lightweight public repository scaffold verification."""

from __future__ import annotations

import argparse
from pathlib import Path
from collections.abc import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]

OPEN_CORE_REQUIRED_PATHS = [
    ".gitignore",
    "pyproject.toml",
    "docs/architecture/ALTERNATIVES_REVIEW.md",
    "docs/architecture/ARCHITECTURE_OVERVIEW.md",
    "docs/architecture/CREDENTIAL_CAPABILITY_PROVIDERS.md",
    "docs/architecture/FIRST_BUILDABLE_PATH.md",
    "docs/architecture/FIXTURE_AUDIT_STORAGE.md",
    "docs/architecture/LIVE_ADAPTER_DRY_RUN_CONTRACT.md",
    "docs/architecture/OPEN_CORE_ARMOR_ENFORCEMENT_CONTRACT.md",
    "docs/architecture/OPEN_CORE_WARDEN_POLICY_CONTRACT.md",
    "docs/architecture/diagrams/agent-bus-data-flow.html",
    "docs/architecture/diagrams/agent-bus-trust-boundaries.html",
    "docs/requirements/REQUIREMENTS_SPEC.md",
    "docs/requirements/INITIAL_AGENT_BUS_SLICE.md",
    "docs/requirements/FIRST_PROTOTYPE_SCOPE.md",
    "docs/security/THREAT_MODEL.md",
    "docs/security/AGENT_IDENTITY_AUTHENTICATION.md",
    "docs/security/LOCAL_RUNTIME_CREDENTIAL_FORMAT.md",
    "docs/security/AUTHORIZATION_CONTEXT_SCHEMA.md",
    "docs/security/CONTEXT_PACKAGE_RULES.md",
    "docs/qa/QA_PLAN.md",
    "scripts/agent_bus_verify.py",
    "scripts/verify_repo.py",
    "src/agent_bus/__init__.py",
    "src/agent_bus/__main__.py",
    "src/agent_bus/armor_enforcement.py",
    "src/agent_bus/cli.py",
    "src/agent_bus/credential_provider.py",
    "src/agent_bus/ecosystem_contract.py",
    "src/agent_bus/verifier.py",
    "src/agent_bus/warden_policy.py",
    "tests/fixtures/README.md",
    "tests/test_cli.py",
    "tests/test_armor_enforcement.py",
    "tests/test_credential_provider_contract.py",
    "tests/test_ecosystem_contract_examples.py",
    "tests/test_warden_policy.py",
    "tests/test_verifier.py",
    "tests/fixtures/agent_bus/envelopes/valid/valid-notify-minimal.json",
    "tests/fixtures/agent_bus/envelopes/valid/valid-notify-with-warden-armor.json",
    "tests/fixtures/agent_bus/envelopes/invalid/armor-block-result.json",
    "tests/fixtures/agent_bus/envelopes/invalid/armor-private-evidence.json",
    "tests/fixtures/agent_bus/credential_providers/valid-local-runtime-token.json",
    "tests/fixtures/agent_bus/envelopes/invalid/missing-source.json",
    "tests/fixtures/agent_bus/envelopes/invalid/warden-binding-mismatch.json",
    "tests/fixtures/agent_bus/envelopes/invalid/warden-deny-result.json",
    "tests/fixtures/agent_bus/envelopes/invalid/wrong-destination-delivery.json",
    "tests/fixtures/agent_bus/ecosystem/armor-enforcement-result.json",
    "tests/fixtures/agent_bus/ecosystem/keyper-credential-evidence.json",
    "tests/fixtures/agent_bus/ecosystem/rsk-ai-auth-capability-grant.json",
    "tests/fixtures/agent_bus/ecosystem/warden-policy-result.json",
    "tests/fixtures/armor_enforcement/valid-allow.json",
    "tests/fixtures/armor_enforcement/valid-block.json",
    "tests/fixtures/armor_enforcement/valid-require-review.json",
    "tests/fixtures/armor_enforcement/valid-sanitize.json",
    "tests/fixtures/warden_policy/valid-allow.json",
    "tests/fixtures/warden_policy/valid-deny.json",
    "tests/fixtures/warden_policy/valid-require-review.json",
    "tests/fixtures/agent_bus/transitions/valid/valid-basic-flow.json",
]

OPEN_CORE_ALTERNATIVES = [
    (
        "public README",
        ("README.md", "docs/open-core/README.md"),
    ),
    (
        "public product overview",
        (
            "docs/product/PRODUCT_OVERVIEW.md",
            "docs/open-core/PRODUCT_OVERVIEW.md",
        ),
    ),
    (
        "local verifier runbook",
        (
            "docs/operations/LOCAL_VERIFIER_RUNBOOK.md",
            "docs/open-core/LOCAL_VERIFIER_RUNBOOK.md",
        ),
    ),
    (
        "open-core release checklist",
        (
            "docs/release/OPEN_CORE_RELEASE_CHECKLIST.md",
            "docs/open-core/OPEN_CORE_RELEASE_CHECKLIST.md",
        ),
    ),
]

PROFILES = {
    "open-core": (OPEN_CORE_REQUIRED_PATHS, OPEN_CORE_ALTERNATIVES),
}

try:
    from verify_repo_profiles import EXTRA_PROFILES
except ImportError:
    EXTRA_PROFILES = {}

PROFILES.update(EXTRA_PROFILES)


def _missing_required_paths(root: Path, paths: Iterable[str]) -> list[str]:
    return [path for path in paths if not (root / path).exists()]


def _missing_alternatives(
    root: Path,
    alternatives: Sequence[tuple[str, Sequence[str]]],
) -> list[str]:
    missing: list[str] = []
    for label, paths in alternatives:
        if not any((root / path).exists() for path in paths):
            joined = " or ".join(paths)
            missing.append(f"{label}: {joined}")
    return missing


def verify(profile: str, root: Path) -> int:
    required_paths, alternatives = PROFILES[profile]
    missing = _missing_required_paths(root, required_paths)
    missing.extend(_missing_alternatives(root, alternatives))

    if missing:
        print(f"Missing required paths for {profile} profile:")
        for path in missing:
            print(f"- {path}")
        return 1

    if profile == "commercial" and not required_paths:
        placeholder = root / "COMMERCIAL_PLACEHOLDER.md"
        if placeholder.exists():
            print(
                f"OK: {root.name} commercial profile is placeholder-only "
                f"({placeholder.name})"
            )
        else:
            print(
                f"OK: {root.name} commercial profile has no required paths yet; "
                "commercial implementation is not approved"
            )
        return 0

    total = len(required_paths) + len(alternatives)
    print(f"OK: {root.name} {profile} profile contains {total} required checks")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify required files for source and split target repos."
    )
    default_profile = "source" if "source" in PROFILES else "open-core"
    parser.add_argument(
        "profile",
        nargs="?",
        choices=sorted(PROFILES),
        default=default_profile,
        help=f"Repository profile to verify. Defaults to {default_profile}.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to verify. Defaults to this script's repository.",
    )
    args = parser.parse_args()

    return verify(args.profile, args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
