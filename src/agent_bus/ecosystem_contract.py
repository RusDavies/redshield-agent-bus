"""Open-core ecosystem contract example validators."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .credential_provider import _validate_provider_fixture
from .verifier import _stable_errors


ECOSYSTEM_SCHEMA_VERSION = "agent_bus.ecosystem_fixture.v1"
ALLOWED_FIXTURE_KINDS = {
    "armor_enforcement_result",
    "keyper_credential_evidence",
    "rsk_ai_auth_capability_grant",
    "warden_policy_result",
}
EXPECTED_FIXTURE_NAMES = {
    "armor-enforcement-result.json",
    "keyper-credential-evidence.json",
    "rsk-ai-auth-capability-grant.json",
    "warden-policy-result.json",
}
ALLOWED_WARDEN_DECISIONS = {"allow", "deny", "require_review"}
ALLOWED_ARMOR_DECISIONS = {"allow", "block", "sanitize", "require_review"}
ALLOWED_RISK_CLASSES = {"low", "medium", "high", "critical"}
ALLOWED_ARMOR_TARGETS = {
    "adapter_delivery_preview",
    "context_package",
    "delivery_payload",
    "tool_dispatch",
}
REJECTED_PRIVATE_KEYS = {
    "credential_material",
    "customer_data",
    "full_chat_transcript",
    "host_private_material",
    "issuer_secret",
    "private_memory_dump",
    "raw_certificate_body",
    "raw_content",
    "secret_value",
    "ssh_private_key",
}


@dataclass
class EcosystemContractCaseResult:
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
class EcosystemContractVerificationResult:
    path: str
    cases: list[EcosystemContractCaseResult]

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


def verify_ecosystem_contract_path(path: Path) -> EcosystemContractVerificationResult:
    root = path.resolve()
    cases = [_verify_ecosystem_fixture(fixture) for fixture in _fixture_files(root)]
    if root.is_dir():
        found = {fixture.name for fixture in _fixture_files(root)}
        missing = sorted(EXPECTED_FIXTURE_NAMES - found)
        unexpected = sorted(found - EXPECTED_FIXTURE_NAMES)
        if missing or unexpected:
            errors = [f"ecosystem_fixture_missing:{name}" for name in missing]
            errors.extend(f"ecosystem_fixture_unexpected:{name}" for name in unexpected)
            cases.append(
                _case_result(
                    case_id="ecosystem-fixture-set",
                    path=root,
                    errors=errors,
                    expect={"valid": False, "errors": errors},
                )
            )
    return EcosystemContractVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.glob("*.json"))


def _verify_ecosystem_fixture(path: Path) -> EcosystemContractCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _case_result(path.stem, path, ["fixture_json_invalid"], {})

    errors = _validate_ecosystem_fixture(fixture)
    return _case_result(
        case_id=str(fixture.get("case_id") or path.stem),
        path=path,
        errors=errors,
        expect=fixture.get("expect", {}),
    )


def _validate_ecosystem_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if fixture.get("schema_version") != ECOSYSTEM_SCHEMA_VERSION:
        errors.append("ecosystem_schema_unsupported")
    if fixture.get("fixture_kind") not in ALLOWED_FIXTURE_KINDS:
        errors.append("ecosystem_fixture_kind_unsupported")
    if not fixture.get("case_id"):
        errors.append("ecosystem_case_id_missing")
    _validate_no_private_material(fixture, errors)

    kind = fixture.get("fixture_kind")
    if kind == "rsk_ai_auth_capability_grant":
        _validate_rsk_ai_auth_fixture(fixture, errors)
    elif kind == "keyper_credential_evidence":
        _validate_keyper_fixture(fixture, errors)
    elif kind == "warden_policy_result":
        _validate_warden_fixture(fixture, errors)
    elif kind == "armor_enforcement_result":
        _validate_armor_fixture(fixture, errors)

    return _stable_errors(errors)


def _validate_rsk_ai_auth_fixture(
    fixture: dict[str, Any],
    errors: list[str],
) -> None:
    grant = fixture.get("capability_grant")
    authz = fixture.get("agent_bus_authorization_context")
    if not isinstance(grant, dict):
        errors.append("rsk_ai_auth_grant_missing")
        grant = {}
    if not isinstance(authz, dict):
        errors.append("agent_bus_authorization_context_missing")
        authz = {}

    if grant.get("schema_version") != "rsk_ai_auth.capability_grant.v1":
        errors.append("rsk_ai_auth_grant_schema_unsupported")
    if authz.get("schema_version") != "authzctx.v1":
        errors.append("authorization_context_schema_unsupported")
    if authz.get("authorization_id") != grant.get("grant_id"):
        errors.append("grant_authorization_id_mismatch")
    if authz.get("source_event_ids") != (grant.get("delegated_by") or {}).get(
        "source_event_ids"
    ):
        errors.append("grant_source_events_mismatch")
    if authz.get("allowed_interaction_types") != grant.get("allowed_interaction_types"):
        errors.append("grant_interaction_types_mismatch")
    if authz.get("allowed_action_classes") != grant.get("allowed_action_classes"):
        errors.append("grant_action_classes_mismatch")
    if authz.get("expires_at") != grant.get("expires_at"):
        errors.append("grant_expiry_mismatch")
    if (authz.get("basis") or {}).get("summary_is_authorization") is not False:
        errors.append("summary_authorization_rejected")
    if grant.get("revoked_at") is not None:
        errors.append("grant_revoked")


def _validate_keyper_fixture(fixture: dict[str, Any], errors: list[str]) -> None:
    if fixture.get("credential_provider") != "keyper":
        errors.append("keyper_provider_missing")
    request = fixture.get("provider_request")
    provider_response = fixture.get("provider_response")
    provider_errors = _validate_provider_fixture(
        {
            "request": request,
            "provider_response": provider_response,
            "trusted_time": fixture.get("trusted_time"),
        }
    )
    errors.extend(f"keyper_provider_contract:{error}" for error in provider_errors)

    consumed = fixture.get("agent_bus_consumes")
    if not isinstance(consumed, list) or not consumed:
        errors.append("agent_bus_consumes_missing")
        consumed = []
    if not isinstance(provider_response, dict):
        provider_response = {}
    for field_name in consumed:
        if field_name not in provider_response:
            errors.append(f"agent_bus_consumed_field_missing:{field_name}")

    forbidden = set(fixture.get("agent_bus_does_not_consume") or [])
    if not forbidden:
        errors.append("keyper_private_material_boundary_missing")
    if set(consumed) & REJECTED_PRIVATE_KEYS:
        errors.append("keyper_private_material_consumed")


def _validate_warden_fixture(fixture: dict[str, Any], errors: list[str]) -> None:
    results = fixture.get("policy_results")
    if not isinstance(results, list) or not results:
        errors.append("warden_policy_results_missing")
        return
    decisions: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            errors.append("warden_policy_result_invalid")
            continue
        if result.get("schema_version") != "redshield_warden.policy_result.v1":
            errors.append("warden_policy_result_schema_unsupported")
        decision = result.get("decision")
        if decision not in ALLOWED_WARDEN_DECISIONS:
            errors.append("warden_policy_decision_unsupported")
        else:
            decisions.add(decision)
        if result.get("risk_class") not in ALLOWED_RISK_CLASSES:
            errors.append("warden_policy_risk_class_unsupported")
        if not result.get("decision_id"):
            errors.append("warden_policy_decision_id_missing")
        if not result.get("reason_codes"):
            errors.append("warden_policy_reason_missing")
        if not result.get("policy_refs"):
            errors.append("warden_policy_ref_missing")
        if not result.get("evidence_refs"):
            errors.append("warden_policy_evidence_missing")
        if decision == "require_review" and not result.get("required_approver_roles"):
            errors.append("warden_policy_review_requires_approver")
        if decision == "allow" and result.get("required_approver_roles"):
            errors.append("warden_policy_allow_must_not_require_approver")
    if decisions != ALLOWED_WARDEN_DECISIONS:
        errors.append("warden_policy_decision_coverage_incomplete")


def _validate_armor_fixture(fixture: dict[str, Any], errors: list[str]) -> None:
    results = fixture.get("enforcement_results")
    if not isinstance(results, list) or not results:
        errors.append("armor_enforcement_results_missing")
        return
    decisions: set[str] = set()
    for result in results:
        if not isinstance(result, dict):
            errors.append("armor_enforcement_result_invalid")
            continue
        if result.get("schema_version") != "redshield_armor.enforcement_result.v1":
            errors.append("armor_enforcement_result_schema_unsupported")
        decision = result.get("decision")
        if decision not in ALLOWED_ARMOR_DECISIONS:
            errors.append("armor_enforcement_decision_unsupported")
        else:
            decisions.add(decision)
        if result.get("enforcement_target") not in ALLOWED_ARMOR_TARGETS:
            errors.append("armor_enforcement_target_unsupported")
        if not result.get("enforcement_id"):
            errors.append("armor_enforcement_id_missing")
        if not result.get("finding_codes"):
            errors.append("armor_enforcement_finding_missing")
        if not result.get("evidence_refs"):
            errors.append("armor_enforcement_evidence_missing")
        if decision == "sanitize" and not result.get("sanitized_field_refs"):
            errors.append("armor_enforcement_sanitize_requires_field_refs")
        if decision == "allow" and result.get("sanitized_field_refs"):
            errors.append("armor_enforcement_allow_must_not_sanitize")
        if decision == "require_review" and not result.get("receipt_requirements"):
            errors.append("armor_enforcement_review_requires_receipt_requirement")
        if decision == "block" and result.get("receipt_requirements"):
            errors.append("armor_enforcement_block_must_not_require_receipt")
    if decisions != ALLOWED_ARMOR_DECISIONS:
        errors.append("armor_enforcement_decision_coverage_incomplete")


def _validate_no_private_material(value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REJECTED_PRIVATE_KEYS:
                errors.append("ecosystem_private_material_rejected")
            if key == "privacy_classification" and child in {"private", "secret"}:
                errors.append("ecosystem_private_material_rejected")
            _validate_no_private_material(child, errors)
    elif isinstance(value, list):
        for child in value:
            _validate_no_private_material(child, errors)


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> EcosystemContractCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )

    return EcosystemContractCaseResult(
        case_id=case_id,
        path=str(path),
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
    )
