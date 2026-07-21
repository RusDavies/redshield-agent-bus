"""Open-core Armor enforcement-result contract checks."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .verifier import _stable_errors


ALLOWED_DECISIONS = {"allow", "block", "sanitize", "require_review"}
ALLOWED_TARGETS = {
    "adapter_delivery_preview",
    "context_package",
    "delivery_payload",
    "tool_dispatch",
}
REQUIRED_REQUEST_FIELDS = {
    "schema_version",
    "request_id",
    "message_id",
    "correlation_id",
    "enforcement_target",
    "action_class",
    "payload_ref",
    "adapter_capability_ref",
    "safety_flags",
}
REQUIRED_RESULT_FIELDS = {
    "schema_version",
    "enforcement_id",
    "decision",
    "enforcement_target",
    "finding_codes",
    "adapter_capability_refs",
    "sanitized_field_refs",
    "receipt_requirements",
    "evidence_refs",
    "applies_to",
    "evaluated_at",
}
REJECTED_EVIDENCE_KEYS = {
    "raw_content",
    "full_chat_transcript",
    "private_memory_dump",
    "secret_value",
    "credential_material",
    "customer_data",
}


@dataclass
class ArmorEnforcementCaseResult:
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
class ArmorEnforcementVerificationResult:
    path: str
    cases: list[ArmorEnforcementCaseResult]

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


def verify_armor_enforcement_path(path: Path) -> ArmorEnforcementVerificationResult:
    root = path.resolve()
    cases = [_verify_enforcement_fixture(fixture) for fixture in _fixture_files(root)]
    return ArmorEnforcementVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_enforcement_fixture(path: Path) -> ArmorEnforcementCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _case_result(path.stem, path, ["fixture_json_invalid"], {})

    errors = _validate_fixture(fixture)
    return _case_result(
        str(fixture.get("case_id") or path.stem),
        path,
        errors,
        fixture.get("expect", {}),
    )


def _validate_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    request = fixture.get("enforcement_check_request")
    result = fixture.get("enforcement_result")
    if not isinstance(request, dict):
        errors.append("armor_request_missing")
        request = {}
    if not isinstance(result, dict):
        errors.append("armor_result_missing")
        return _stable_errors(errors)

    _require_fields(request, REQUIRED_REQUEST_FIELDS, errors, "armor_request_field_missing")
    _require_fields(result, REQUIRED_RESULT_FIELDS, errors, "armor_result_field_missing")
    if request.get("schema_version") != "redshield_armor.enforcement_check_request.v1":
        errors.append("armor_request_schema_unsupported")
    if result.get("schema_version") != "redshield_armor.enforcement_result.v1":
        errors.append("armor_result_schema_unsupported")

    decision = result.get("decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append("armor_decision_unsupported")
    if request.get("enforcement_target") not in ALLOWED_TARGETS:
        errors.append("armor_target_unsupported")
    if result.get("enforcement_target") not in ALLOWED_TARGETS:
        errors.append("armor_target_unsupported")
    if not result.get("finding_codes"):
        errors.append("armor_finding_missing")
    if not result.get("evidence_refs"):
        errors.append("armor_evidence_missing")
    if decision == "sanitize" and not result.get("sanitized_field_refs"):
        errors.append("armor_sanitize_requires_field_refs")
    if decision == "allow" and result.get("sanitized_field_refs"):
        errors.append("armor_allow_must_not_sanitize")
    if decision == "require_review" and not result.get("receipt_requirements"):
        errors.append("armor_review_requires_receipt_requirement")
    if decision == "block" and result.get("receipt_requirements"):
        errors.append("armor_block_must_not_require_receipt")

    _validate_binding(request, result, errors)
    _validate_no_private_evidence(result, errors)
    return _stable_errors(errors)


def _validate_binding(
    request: dict[str, Any],
    result: dict[str, Any],
    errors: list[str],
) -> None:
    applies_to = result.get("applies_to")
    if not isinstance(applies_to, dict):
        errors.append("armor_binding_missing")
        return
    for field_name in (
        "request_id",
        "message_id",
        "correlation_id",
        "enforcement_target",
        "action_class",
        "payload_ref",
    ):
        if applies_to.get(field_name) != request.get(field_name):
            errors.append("armor_binding_failed")
    if applies_to.get("adapter_capability_ref") != request.get("adapter_capability_ref"):
        errors.append("armor_binding_failed")
    if result.get("enforcement_target") != request.get("enforcement_target"):
        errors.append("armor_binding_failed")


def _validate_no_private_evidence(
    result: dict[str, Any],
    errors: list[str],
) -> None:
    evidence = result.get("evidence")
    if not isinstance(evidence, dict):
        return
    if any(key in evidence for key in REJECTED_EVIDENCE_KEYS):
        errors.append("armor_private_evidence_rejected")
    if evidence.get("privacy_classification") in {"private", "secret"}:
        errors.append("armor_private_evidence_rejected")


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> ArmorEnforcementCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )

    return ArmorEnforcementCaseResult(
        case_id=case_id,
        path=str(path),
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
    )


def _require_fields(
    data: dict[str, Any],
    fields: set[str],
    errors: list[str],
    reason: str,
) -> None:
    for field_name in sorted(fields):
        if field_name not in data or data.get(field_name) in (None, ""):
            errors.append(f"{reason}:{field_name}")
