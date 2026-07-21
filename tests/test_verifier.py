from __future__ import annotations

from pathlib import Path

from agent_bus.verifier import verify_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "agent_bus"


def test_verifier_accepts_expected_fixture_suite() -> None:
    result = verify_path(FIXTURES)

    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert len(result.cases) == 16
    assert "valid-notify-minimal" in case_ids
    assert "wrong-destination-delivery" in case_ids
    assert "valid-basic-flow" in case_ids


def test_expected_invalid_cases_still_meet_expectations() -> None:
    result = verify_path(FIXTURES)

    expected_invalid = {
        case.case_id: case
        for case in result.cases
        if case.expected_valid is False
    }

    assert "private-data-leakage" in expected_invalid
    assert "context_private_data_not_authorized" in expected_invalid["private-data-leakage"].errors
    assert expected_invalid["wrong-destination-delivery"].errors == ["wrong_destination_delivery"]
    assert expected_invalid["deferred-broadcast"].errors == ["interaction_type_deferred"]
