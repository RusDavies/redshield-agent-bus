"""Open-core Warden policy-result contract checks."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .verifier import _stable_errors


ALLOWED_DECISIONS = {"allow", "deny", "require_review"}
ALLOWED_RISK_CLASSES = {"low", "medium", "high", "critical"}
REQUIRED_REQUEST_FIELDS = {
    "schema_version",
    "request_id",
    "message_id",
    "correlation_id",
    "action_class",
    "actor_id",
    "target",
    "delivery_expectation",
    "safety_flags",
}
REQUIRED_RESULT_FIELDS = {
    "schema_version",
    "decision_id",
    "decision",
    "reason_codes",
    "risk_class",
    "policy_refs",
    "required_approver_roles",
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
class WardenPolicyCaseResult:
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
class WardenPolicyVerificationResult:
    path: str
    cases: list[WardenPolicyCaseResult]

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


def verify_warden_policy_path(path: Path) -> WardenPolicyVerificationResult:
    root = path.resolve()
    cases = [_verify_policy_fixture(fixture) for fixture in _fixture_files(root)]
    return WardenPolicyVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_policy_fixture(path: Path) -> WardenPolicyCaseResult:
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
    request = fixture.get("policy_check_request")
    result = fixture.get("policy_result")
    if not isinstance(request, dict):
        errors.append("policy_request_missing")
        request = {}
    if not isinstance(result, dict):
        errors.append("policy_result_missing")
        return _stable_errors(errors)

    _require_fields(request, REQUIRED_REQUEST_FIELDS, errors, "policy_request_field_missing")
    _require_fields(result, REQUIRED_RESULT_FIELDS, errors, "policy_result_field_missing")
    if request.get("schema_version") != "redshield_warden.policy_check_request.v1":
        errors.append("policy_request_schema_unsupported")
    if result.get("schema_version") != "redshield_warden.policy_result.v1":
        errors.append("policy_result_schema_unsupported")

    decision = result.get("decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append("policy_decision_unsupported")
    if result.get("risk_class") not in ALLOWED_RISK_CLASSES:
        errors.append("policy_risk_class_unsupported")
    if not result.get("reason_codes"):
        errors.append("policy_reason_missing")
    if not result.get("policy_refs"):
        errors.append("policy_ref_missing")
    if not result.get("evidence_refs"):
        errors.append("policy_evidence_missing")
    if decision == "require_review" and not result.get("required_approver_roles"):
        errors.append("policy_review_requires_approver")
    if decision == "allow" and result.get("required_approver_roles"):
        errors.append("policy_allow_must_not_require_approver")

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
        errors.append("policy_binding_missing")
        return
    for field_name in ("request_id", "message_id", "correlation_id", "action_class"):
        if applies_to.get(field_name) != request.get(field_name):
            errors.append("policy_binding_failed")
    if applies_to.get("actor_id") != request.get("actor_id"):
        errors.append("policy_binding_failed")
    if applies_to.get("target") != request.get("target"):
        errors.append("policy_binding_failed")
    if applies_to.get("delivery_expectation") != request.get("delivery_expectation"):
        errors.append("policy_binding_failed")


def _validate_no_private_evidence(
    result: dict[str, Any],
    errors: list[str],
) -> None:
    evidence = result.get("evidence")
    if not isinstance(evidence, dict):
        return
    if any(key in evidence for key in REJECTED_EVIDENCE_KEYS):
        errors.append("policy_private_evidence_rejected")
    if evidence.get("privacy_classification") in {"private", "secret"}:
        errors.append("policy_private_evidence_rejected")


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> WardenPolicyCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )

    return WardenPolicyCaseResult(
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
