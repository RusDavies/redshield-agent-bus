from __future__ import annotations

from pathlib import Path

from agent_bus.armor_enforcement import verify_armor_enforcement_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "armor_enforcement"


def test_armor_enforcement_fixture_suite_matches_expectations() -> None:
    result = verify_armor_enforcement_path(FIXTURES)
    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert "valid-allow" in case_ids
    assert "valid-block" in case_ids
    assert "valid-sanitize" in case_ids
    assert "valid-require-review" in case_ids


def test_valid_armor_enforcement_decisions_cover_baseline_contract() -> None:
    result = verify_armor_enforcement_path(FIXTURES)
    valid_cases = {
        case.case_id
        for case in result.cases
        if case.expected_valid is True
    }

    assert valid_cases == {
        "valid-allow",
        "valid-block",
        "valid-sanitize",
        "valid-require-review",
    }


def test_invalid_armor_enforcement_cases_fail_closed() -> None:
    result = verify_armor_enforcement_path(FIXTURES)
    invalid = {
        case.case_id: case.errors
        for case in result.cases
        if case.expected_valid is False
    }

    assert invalid["invalid-binding-mismatch"] == ["armor_binding_failed"]
    assert invalid["invalid-sanitize-missing-fields"] == ["armor_sanitize_requires_field_refs"]
    assert invalid["invalid-private-evidence"] == ["armor_private_evidence_rejected"]
