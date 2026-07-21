"""Command line interface for the local verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .verifier import verify_path


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

    parser.error(f"unknown command: {args.command}")
    return 2
