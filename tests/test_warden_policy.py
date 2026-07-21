from __future__ import annotations

from pathlib import Path

from agent_bus.warden_policy import verify_warden_policy_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "warden_policy"


def test_warden_policy_fixture_suite_matches_expectations() -> None:
    result = verify_warden_policy_path(FIXTURES)
    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert "valid-allow" in case_ids
    assert "valid-deny" in case_ids
    assert "valid-require-review" in case_ids
    assert "invalid-binding-mismatch" in case_ids


def test_valid_warden_policy_decisions_cover_baseline_contract() -> None:
    result = verify_warden_policy_path(FIXTURES)
    valid_cases = {
        case.case_id
        for case in result.cases
        if case.expected_valid is True
    }

    assert valid_cases == {
        "valid-allow",
        "valid-deny",
        "valid-require-review",
    }


def test_invalid_warden_policy_cases_fail_closed() -> None:
    result = verify_warden_policy_path(FIXTURES)
    invalid = {
        case.case_id: case.errors
        for case in result.cases
        if case.expected_valid is False
    }

    assert invalid["invalid-binding-mismatch"] == ["policy_binding_failed"]
    assert invalid["invalid-review-missing-approver"] == ["policy_review_requires_approver"]
    assert invalid["invalid-private-evidence"] == ["policy_private_evidence_rejected"]
