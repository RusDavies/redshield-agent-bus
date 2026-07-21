from __future__ import annotations

import json
from pathlib import Path

from agent_bus.cli import main


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "agent_bus"
DRY_RUN_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "adapter_dry_runs"
ARMOR_ENFORCEMENT_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "armor_enforcement"
WARDEN_POLICY_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "warden_policy"


def test_cli_verifies_fixture_directory(capsys) -> None:
    exit_code = main(["verify", str(FIXTURES), "--pretty"])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["ok"] is True
    assert result["case_count"] == 16


def test_cli_returns_nonzero_when_expectations_fail(tmp_path, capsys) -> None:
    broken_fixture = tmp_path / "broken.json"
    broken_fixture.write_text("{", encoding="utf-8")

    exit_code = main(["verify", str(broken_fixture)])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 1
    assert result["ok"] is False
    assert result["cases"][0]["errors"] == ["fixture_json_invalid"]


def test_cli_verifies_dry_run_fixture_directory(capsys) -> None:
    exit_code = main(["dry-run", str(DRY_RUN_FIXTURES), "--pretty"])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["ok"] is True
    assert result["case_count"] == 6


def test_cli_verifies_warden_policy_fixture_directory(capsys) -> None:
    exit_code = main(["warden-policy", str(WARDEN_POLICY_FIXTURES), "--pretty"])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["ok"] is True
    assert result["case_count"] == 6


def test_cli_verifies_armor_enforcement_fixture_directory(capsys) -> None:
    exit_code = main(["armor-enforcement", str(ARMOR_ENFORCEMENT_FIXTURES), "--pretty"])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["ok"] is True
    assert result["case_count"] == 7
