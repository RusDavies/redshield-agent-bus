"""Command line interface for the local verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .armor_enforcement import verify_armor_enforcement_path
from .dry_run import verify_dry_run_path
from .ecosystem_contract import verify_ecosystem_contract_path
from .verifier import verify_path
from .warden_policy import verify_warden_policy_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-bus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="verify a fixture file or directory")
    verify.add_argument("path", type=Path, help="fixture file or directory")
    verify.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    dry_run = subparsers.add_parser(
        "dry-run",
        help="verify local-only adapter dry-run preview and receipt fixtures",
    )
    dry_run.add_argument("path", type=Path, help="dry-run fixture file or directory")
    dry_run.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    warden_policy = subparsers.add_parser(
        "warden-policy",
        help="verify open-core Warden policy-result contract fixtures",
    )
    warden_policy.add_argument("path", type=Path, help="Warden policy fixture file or directory")
    warden_policy.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    armor_enforcement = subparsers.add_parser(
        "armor-enforcement",
        help="verify open-core Armor enforcement-result contract fixtures",
    )
    armor_enforcement.add_argument("path", type=Path, help="Armor enforcement fixture file or directory")
    armor_enforcement.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    ecosystem_contract = subparsers.add_parser(
        "ecosystem-contract",
        help="verify open-core ecosystem contract example fixtures",
    )
    ecosystem_contract.add_argument(
        "path",
        type=Path,
        help="ecosystem contract fixture file or directory",
    )
    ecosystem_contract.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "verify":
        result = verify_path(args.path)
        json.dump(
            result.to_dict(),
            sys.stdout,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if result.ok else 1

    if args.command == "dry-run":
        result = verify_dry_run_path(args.path)
        json.dump(
            result.to_dict(),
            sys.stdout,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if result.ok else 1

    if args.command == "warden-policy":
        result = verify_warden_policy_path(args.path)
        json.dump(
            result.to_dict(),
            sys.stdout,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if result.ok else 1

    if args.command == "armor-enforcement":
        result = verify_armor_enforcement_path(args.path)
        json.dump(
            result.to_dict(),
            sys.stdout,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if result.ok else 1

    if args.command == "ecosystem-contract":
        result = verify_ecosystem_contract_path(args.path)
        json.dump(
            result.to_dict(),
            sys.stdout,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if result.ok else 1

    parser.error(f"unknown command: {args.command}")
    return 2
