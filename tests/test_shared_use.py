from __future__ import annotations

from pathlib import Path

from agent_bus.shared_use import verify_shared_use_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "shared_use"


def test_shared_use_fixture_suite_matches_expectations() -> None:
    result = verify_shared_use_path(FIXTURES)
    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert case_ids == {
        "invalid-display-name-claims",
        "invalid-monitoring",
        "invalid-rate-limit",
        "valid-shared-profile",
    }


def test_valid_shared_profile_accepts_required_controls() -> None:
    result = verify_shared_use_path(FIXTURES / "valid-shared-profile.json")

    assert result.ok is True
    assert result.cases[0].valid is True


def test_display_name_claims_fail_closed() -> None:
    result = verify_shared_use_path(FIXTURES / "invalid-display-name-claims.json")

    assert result.ok is True
    assert result.cases[0].errors == ["display_name_claims_forbidden"]
