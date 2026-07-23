from __future__ import annotations

from pathlib import Path

from agent_bus.live_receipt import verify_live_receipt_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "live_receipts"


def test_live_receipt_fixture_suite_matches_expectations() -> None:
    result = verify_live_receipt_path(FIXTURES)
    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert case_ids == {
        "invalid-destination-mismatch",
        "invalid-missing-approval",
        "invalid-raw-platform-response",
        "valid-owner-only-delivered",
    }


def test_valid_owner_only_receipt_is_accepted() -> None:
    result = verify_live_receipt_path(FIXTURES / "valid-owner-only-delivered.json")

    assert result.ok is True
    assert result.cases[0].valid is True


def test_wrong_destination_receipt_fails_closed() -> None:
    result = verify_live_receipt_path(FIXTURES / "invalid-destination-mismatch.json")

    assert result.ok is True
    assert result.cases[0].errors == ["live_receipt_destination_mismatch"]
