from __future__ import annotations

import json
from pathlib import Path

from agent_bus.dry_run import build_preview_request, verify_dry_run_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "adapter_dry_runs"


def test_dry_run_fixture_suite_matches_expectations() -> None:
    result = verify_dry_run_path(FIXTURES)
    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert "valid-visible-preview" in case_ids
    assert "wrong-destination-preview" in case_ids
    assert "private-only-completion-missing-receipt" in case_ids


def test_preview_binds_source_destination_and_payload_without_side_effects() -> None:
    fixture = _load_fixture("valid-visible-preview.json")
    preview = build_preview_request(fixture["envelope"], fixture["adapter_capability"])

    assert preview["mode"] == "dry_run"
    assert preview["source"]["conversation_id"] == "channel_test_source"
    assert preview["destination"]["conversation_id"] == "channel_test_source"
    assert preview["safety"]["live_side_effect_allowed"] is False
    assert preview["safety"]["external_action_allowed"] is False
    assert preview["payload_preview"]["content_hash"].startswith("sha256:")
    assert "raw_content" not in preview["payload_preview"]


def test_receipt_validation_accepts_bound_synthetic_receipt(tmp_path: Path) -> None:
    fixture = _load_fixture("valid-visible-preview.json")
    preview = build_preview_request(fixture["envelope"], fixture["adapter_capability"])
    fixture["dry_run_delivery_receipt"] = {
        "schema_version": "dryreceipt.v1",
        "receipt_id": "dryreceipt_test_bound",
        "preview_id": preview["preview_id"],
        "message_id": preview["message_id"],
        "correlation_id": preview["correlation_id"],
        "adapter_id": preview["adapter_id"],
        "adapter_type": preview["adapter_type"],
        "surface": preview["surface"],
        "mode": "dry_run",
        "result": "accepted",
        "reason": "would_deliver",
        "destination": preview["destination"],
        "delivery_expectation": preview["delivery_expectation"],
        "side_effect_performed": False,
        "payload_hash": preview["payload_preview"]["content_hash"],
        "created_at": "2026-07-10T22:00:00Z",
    }
    fixture["expect"] = {"valid": True, "errors": [], "receipt_required": True}
    path = tmp_path / "bound-receipt.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    result = verify_dry_run_path(path)

    assert result.ok is True
    assert result.cases[0].valid is True


def test_receipt_claiming_side_effect_is_rejected(tmp_path: Path) -> None:
    fixture = _load_fixture("valid-visible-preview.json")
    preview = build_preview_request(fixture["envelope"], fixture["adapter_capability"])
    fixture["dry_run_delivery_receipt"] = {
        "schema_version": "dryreceipt.v1",
        "receipt_id": "dryreceipt_test_side_effect",
        "preview_id": preview["preview_id"],
        "message_id": preview["message_id"],
        "correlation_id": preview["correlation_id"],
        "adapter_id": preview["adapter_id"],
        "adapter_type": preview["adapter_type"],
        "surface": preview["surface"],
        "mode": "dry_run",
        "result": "accepted",
        "reason": "would_deliver",
        "destination": preview["destination"],
        "delivery_expectation": preview["delivery_expectation"],
        "side_effect_performed": True,
        "payload_hash": preview["payload_preview"]["content_hash"],
        "created_at": "2026-07-10T22:00:00Z",
    }
    fixture["expect"] = {
        "valid": False,
        "errors": ["receipt_claims_side_effect"],
        "receipt_required": True,
    }
    path = tmp_path / "side-effect-receipt.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    result = verify_dry_run_path(path)

    assert result.ok is True
    assert result.cases[0].errors == ["receipt_claims_side_effect"]


def _load_fixture(name: str) -> dict:
    path = FIXTURES / name
    fixture = json.loads(path.read_text(encoding="utf-8"))
    envelope_ref = fixture.pop("envelope_fixture")
    envelope_fixture = json.loads((path.parent / envelope_ref).resolve().read_text(encoding="utf-8"))
    fixture["envelope"] = envelope_fixture["envelope"]
    return fixture
