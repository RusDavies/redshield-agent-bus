"""Trusted live-adapter receipt verifier for later promotion gates."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .verifier import _resolve_extends, _stable_errors


REQUIRED_FIELDS = {
    "schema_version",
    "receipt_id",
    "preview_id",
    "message_id",
    "correlation_id",
    "adapter_id",
    "adapter_type",
    "surface",
    "mode",
    "gate",
    "approval_event_id",
    "route_resolution",
    "destination",
    "delivery_expectation",
    "result",
    "reason",
    "side_effect_performed",
    "adapter_actor",
    "evidence_refs",
    "created_at",
}
ALLOWED_GATES = {"gate_2_owner_only_live_trial", "gate_3_shared_or_production"}
ALLOWED_RESULTS = {"delivered", "rejected", "failed"}
BLOCKED_RAW_FIELDS = {
    "raw_platform_response",
    "raw_message_body",
    "private_memory_dump",
    "secret_value",
    "credential_material",
}


@dataclass
class LiveReceiptCaseResult:
    case_id: str
    path: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    expected_valid: bool | None = None
    expected_errors: list[str] = field(default_factory=list)
    expectation_met: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "path": self.path,
            "valid": self.valid,
            "errors": self.errors,
            "expected_valid": self.expected_valid,
            "expected_errors": self.expected_errors,
            "expectation_met": self.expectation_met,
        }


@dataclass
class LiveReceiptVerificationResult:
    path: str
    cases: list[LiveReceiptCaseResult]

    @property
    def ok(self) -> bool:
        return all(case.expectation_met for case in self.cases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "ok": self.ok,
            "case_count": len(self.cases),
            "cases": [case.to_dict() for case in self.cases],
        }


def verify_live_receipt_path(path: Path) -> LiveReceiptVerificationResult:
    root = path.resolve()
    cases = [_verify_fixture(fixture) for fixture in _fixture_files(root)]
    return LiveReceiptVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_fixture(path: Path) -> LiveReceiptCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture = _resolve_extends(fixture, path)
    except (OSError, json.JSONDecodeError):
        return _case_result(path.stem, path, ["fixture_json_invalid"], {})

    receipt = fixture.get("live_adapter_receipt")
    if not isinstance(receipt, dict):
        return _case_result(str(fixture.get("case_id") or path.stem), path, ["live_receipt_missing"], fixture.get("expect", {}))

    errors: list[str] = []
    _validate_receipt(receipt, errors)
    return _case_result(str(fixture.get("case_id") or path.stem), path, _stable_errors(errors), fixture.get("expect", {}))


def _validate_receipt(receipt: dict[str, Any], errors: list[str]) -> None:
    for field_name in sorted(REQUIRED_FIELDS):
        if field_name not in receipt or receipt.get(field_name) in (None, "", []):
            errors.append(f"live_receipt_field_missing:{field_name}")

    if receipt.get("schema_version") != "liveadapterreceipt.v1":
        errors.append("live_receipt_schema_unsupported")
    if receipt.get("mode") != "live":
        errors.append("live_receipt_mode_invalid")
    if receipt.get("gate") not in ALLOWED_GATES:
        errors.append("live_receipt_gate_unsupported")
    if receipt.get("result") not in ALLOWED_RESULTS:
        errors.append("live_receipt_result_unsupported")
    if not receipt.get("approval_event_id"):
        errors.append("approval_event_missing")

    route_resolution = receipt.get("route_resolution")
    if not isinstance(route_resolution, dict):
        errors.append("route_resolution_missing")
    else:
        if route_resolution.get("schema_version") != "targetresolution.v1":
            errors.append("route_resolution_schema_unsupported")
        if route_resolution.get("decision") != "resolved":
            errors.append("route_resolution_not_resolved")
        if route_resolution.get("message_id") != receipt.get("message_id"):
            errors.append("live_receipt_route_binding_failed")
        if route_resolution.get("correlation_id") != receipt.get("correlation_id"):
            errors.append("live_receipt_route_binding_failed")
        if receipt.get("destination") != _expected_destination(route_resolution):
            errors.append("live_receipt_destination_mismatch")

    actor = receipt.get("adapter_actor")
    if not isinstance(actor, dict):
        errors.append("adapter_actor_missing")
    else:
        for field_name in ("actor_id", "runtime_id", "credential_id", "authenticated_at"):
            if not actor.get(field_name):
                errors.append(f"adapter_actor_field_missing:{field_name}")

    if receipt.get("result") == "delivered":
        if receipt.get("side_effect_performed") is not True:
            errors.append("delivered_receipt_missing_side_effect")
        if not receipt.get("platform_delivery_ref"):
            errors.append("platform_delivery_ref_missing")
    elif receipt.get("side_effect_performed") is not False:
        errors.append("rejected_receipt_claims_side_effect")

    if receipt.get("gate") == "gate_2_owner_only_live_trial" and receipt.get("owner_only_access_verified") is not True:
        errors.append("owner_only_access_not_verified")

    if not all(isinstance(ref, str) and ref.startswith("evidence:") for ref in receipt.get("evidence_refs") or []):
        errors.append("live_receipt_evidence_ref_invalid")

    if any(field in receipt for field in BLOCKED_RAW_FIELDS):
        errors.append("live_receipt_contains_raw_private_or_platform_data")


def _expected_destination(route_resolution: dict[str, Any]) -> dict[str, Any]:
    route_preview = route_resolution.get("route_preview") if isinstance(route_resolution.get("route_preview"), dict) else {}
    return {
        "surface": route_preview.get("surface"),
        "conversation_id": route_preview.get("conversation_id"),
        "thread_id": route_preview.get("thread_id"),
    }


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> LiveReceiptCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )
    return LiveReceiptCaseResult(
        case_id=case_id,
        path=str(path),
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
    )
