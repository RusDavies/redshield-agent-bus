"""Capability-grant proof adapter contract checks."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .verifier import _stable_errors


GRANT_SCHEMA_VERSION = "0.1.0"
GRANT_PROFILE = "redshieldworks-agent-capability-grant.v0"
AUTHZ_SCHEMA_VERSION = "authzctx.v1"
ALLOWED_SOURCE_CLASSES = {
    "accounting_export",
    "banking_export",
    "cloud_drive_file",
    "discord_export",
    "document_record",
    "email_item",
    "local_file",
    "manual_upload",
    "other",
    "payroll_export",
}
ALLOWED_SENSITIVITY = {"public", "internal", "confidential", "restricted", "secret"}
ALLOWED_CONTENT_ACCESS = {"metadata_only", "redacted_content", "raw_content_reference"}
ALLOWED_AI_PROCESSING = {
    "not_allowed",
    "requires_manifest_approval",
    "may_start_after_policy_allow",
}
ALLOWED_GRANT_ACTIONS = {
    "create_secure_intake",
    "finalize_agent_populated_intake",
    "register_intake_source",
    "upload_intake_material",
}
GRANT_ACTION_TO_BUS_ACTION_CLASS = {
    "create_secure_intake": "create_secure_intake",
    "finalize_agent_populated_intake": "finalize_agent_populated_intake",
    "register_intake_source": "register_intake_source",
    "upload_intake_material": "upload_intake_material",
}
REJECTED_PRIVATE_KEYS = {
    "credential_material",
    "full_chat_transcript",
    "private_memory_dump",
    "raw_content",
    "secret_value",
}


@dataclass
class CapabilityGrantCaseResult:
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
class CapabilityGrantVerificationResult:
    path: str
    cases: list[CapabilityGrantCaseResult]

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


def verify_capability_grant_path(path: Path) -> CapabilityGrantVerificationResult:
    root = path.resolve()
    cases = [_verify_capability_fixture(fixture) for fixture in _fixture_files(root)]
    return CapabilityGrantVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_capability_fixture(path: Path) -> CapabilityGrantCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _case_result(path.stem, path, ["fixture_json_invalid"], {})

    errors = _validate_fixture(fixture)
    return _case_result(
        case_id=str(fixture.get("case_id") or path.stem),
        path=path,
        errors=errors,
        expect=fixture.get("expect", {}),
    )


def _validate_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    grant = fixture.get("capability_grant")
    authz = fixture.get("agent_bus_authorization_context")
    if not isinstance(grant, dict):
        errors.append("capability_grant_missing")
        grant = {}
    if not isinstance(authz, dict):
        errors.append("agent_bus_authorization_context_missing")
        authz = {}

    _validate_grant(grant, fixture.get("trusted_time"), errors)
    _validate_authorization_context(grant, authz, errors)
    _validate_no_private_payloads(fixture, errors)
    return _stable_errors(errors)


def _validate_grant(
    grant: dict[str, Any],
    trusted_time: str | None,
    errors: list[str],
) -> None:
    required = {
        "schema_version",
        "grant_id",
        "grant_profile",
        "issuer",
        "issued_at",
        "expires_at",
        "audience",
        "workload",
        "delegation",
        "scope",
        "allowed_actions",
        "limits",
        "sender_constraint",
        "revocation_status_ref",
        "audit_correlation",
    }
    _require_fields(grant, required, errors, "capability_grant_field_missing")
    if grant.get("schema_version") != GRANT_SCHEMA_VERSION:
        errors.append("capability_grant_schema_unsupported")
    if grant.get("grant_profile") != GRANT_PROFILE:
        errors.append("capability_grant_profile_unsupported")
    if grant.get("revoked_at") is not None:
        errors.append("capability_grant_revoked")

    workload = grant.get("workload")
    delegation = grant.get("delegation")
    scope = grant.get("scope")
    limits = grant.get("limits")
    sender_constraint = grant.get("sender_constraint")
    audit_correlation = grant.get("audit_correlation")
    if not isinstance(workload, dict):
        errors.append("capability_grant_workload_missing")
        workload = {}
    if not isinstance(delegation, dict):
        errors.append("capability_grant_delegation_missing")
        delegation = {}
    if not isinstance(scope, dict):
        errors.append("capability_grant_scope_missing")
        scope = {}
    if not isinstance(limits, dict):
        errors.append("capability_grant_limits_missing")
        limits = {}
    if not isinstance(sender_constraint, dict):
        errors.append("capability_grant_sender_constraint_missing")
        sender_constraint = {}
    if not isinstance(audit_correlation, dict):
        errors.append("capability_grant_audit_correlation_missing")
        audit_correlation = {}

    _require_fields(workload, {"workload_id", "workload_issuer"}, errors, "workload_field_missing")
    _require_fields(delegation, {"delegation_id", "source_type", "purpose"}, errors, "delegation_field_missing")
    _require_fields(scope, {"project_id"}, errors, "scope_field_missing")
    _require_fields(
        limits,
        {"source_classes", "max_sensitivity", "content_access", "ai_processing"},
        errors,
        "limits_field_missing",
    )
    _require_fields(
        sender_constraint,
        {"sender_constraint_id", "method"},
        errors,
        "sender_constraint_field_missing",
    )
    _require_fields(audit_correlation, {"correlation_id"}, errors, "audit_field_missing")

    allowed_actions = grant.get("allowed_actions")
    if not isinstance(allowed_actions, list) or not allowed_actions:
        errors.append("capability_grant_actions_missing")
    elif any(action not in ALLOWED_GRANT_ACTIONS for action in allowed_actions):
        errors.append("capability_grant_action_unsupported")

    source_classes = limits.get("source_classes")
    if not isinstance(source_classes, list) or not source_classes:
        errors.append("source_classes_missing")
    elif any(source_class not in ALLOWED_SOURCE_CLASSES for source_class in source_classes):
        errors.append("source_class_unsupported")
    if limits.get("max_sensitivity") not in ALLOWED_SENSITIVITY:
        errors.append("sensitivity_unsupported")
    if limits.get("content_access") not in ALLOWED_CONTENT_ACCESS:
        errors.append("content_access_unsupported")
    if limits.get("ai_processing") not in ALLOWED_AI_PROCESSING:
        errors.append("ai_processing_unsupported")

    _validate_expiry(grant, trusted_time, errors)


def _validate_authorization_context(
    grant: dict[str, Any],
    authz: dict[str, Any],
    errors: list[str],
) -> None:
    required = {
        "schema_version",
        "authorization_id",
        "requester_id",
        "source_event_ids",
        "basis",
        "scope",
        "allowed_interaction_types",
        "allowed_action_classes",
        "safety_authorizations",
        "constraints",
        "expires_at",
        "evidence_refs",
    }
    _require_fields(authz, required, errors, "authorization_context_field_missing")
    if authz.get("schema_version") != AUTHZ_SCHEMA_VERSION:
        errors.append("authorization_context_schema_unsupported")
    if authz.get("authorization_id") != grant.get("grant_id"):
        errors.append("grant_authorization_id_mismatch")
    if authz.get("requester_id") != _requester_id(grant):
        errors.append("grant_requester_mismatch")
    if authz.get("expires_at") != grant.get("expires_at"):
        errors.append("grant_expiry_mismatch")

    basis = authz.get("basis")
    scope = authz.get("scope")
    constraints = authz.get("constraints")
    safety_authorizations = authz.get("safety_authorizations")
    if not isinstance(basis, dict):
        errors.append("authorization_basis_missing")
        basis = {}
    if not isinstance(scope, dict):
        errors.append("authorization_scope_missing")
        scope = {}
    if not isinstance(constraints, dict):
        errors.append("authorization_constraints_missing")
        constraints = {}
    if not isinstance(safety_authorizations, dict):
        errors.append("authorization_safety_missing")
        safety_authorizations = {}

    if basis.get("kind") != "capability_grant":
        errors.append("grant_basis_kind_mismatch")
    if basis.get("summary_is_authorization") is not False:
        errors.append("summary_authorization_rejected")
    if basis.get("proof_issuer") != grant.get("issuer"):
        errors.append("grant_issuer_mismatch")
    sender_constraint = grant.get("sender_constraint") or {}
    if basis.get("proof_ref") != sender_constraint.get("sender_constraint_id"):
        errors.append("grant_sender_constraint_mismatch")

    grant_scope = grant.get("scope") or {}
    if scope.get("project_slug") != grant_scope.get("project_id"):
        errors.append("grant_project_scope_mismatch")
    if grant_scope.get("channel_id") and scope.get("source_conversation_id") != grant_scope.get("channel_id"):
        errors.append("grant_channel_scope_mismatch")

    expected_action_classes = sorted(
        GRANT_ACTION_TO_BUS_ACTION_CLASS[action]
        for action in grant.get("allowed_actions", [])
        if action in GRANT_ACTION_TO_BUS_ACTION_CLASS
    )
    if sorted(authz.get("allowed_action_classes") or []) != expected_action_classes:
        errors.append("grant_action_mapping_mismatch")
    if authz.get("allowed_interaction_types") != ["instruct"]:
        errors.append("grant_interaction_mapping_mismatch")

    limits = grant.get("limits") or {}
    if constraints.get("max_sensitivity") != limits.get("max_sensitivity"):
        errors.append("grant_sensitivity_mismatch")
    if constraints.get("content_access") != limits.get("content_access"):
        errors.append("grant_content_access_mismatch")
    if constraints.get("source_classes") != limits.get("source_classes"):
        errors.append("grant_source_class_mismatch")
    if safety_authorizations.get("private_data") != (
        limits.get("max_sensitivity") in {"confidential", "restricted", "secret"}
    ):
        errors.append("grant_private_data_authorization_mismatch")
    if safety_authorizations.get("external_action") is not False:
        errors.append("grant_external_action_rejected")
    if safety_authorizations.get("public_action") is not False:
        errors.append("grant_public_action_rejected")
    if safety_authorizations.get("destructive_action") is not False:
        errors.append("grant_destructive_action_rejected")


def _requester_id(grant: dict[str, Any]) -> str | None:
    delegation = grant.get("delegation") or {}
    return (
        delegation.get("authorizing_actor_id")
        or delegation.get("authorizing_workflow_id")
        or delegation.get("delegation_id")
    )


def _validate_expiry(
    grant: dict[str, Any],
    trusted_time: str | None,
    errors: list[str],
) -> None:
    try:
        issued_at = _parse_time(str(grant.get("issued_at")))
        expires_at = _parse_time(str(grant.get("expires_at")))
    except ValueError:
        errors.append("capability_grant_time_invalid")
        return
    if expires_at <= issued_at:
        errors.append("capability_grant_expiry_invalid")
    if not_before := grant.get("not_before"):
        try:
            if _parse_time(str(not_before)) > expires_at:
                errors.append("capability_grant_not_before_invalid")
        except ValueError:
            errors.append("capability_grant_time_invalid")
    if trusted_time:
        try:
            now = _parse_time(trusted_time)
        except ValueError:
            errors.append("trusted_time_invalid")
            return
        if expires_at <= now:
            errors.append("capability_grant_expired")
        if not_before and _parse_time(str(not_before)) > now:
            errors.append("capability_grant_not_yet_valid")


def _validate_no_private_payloads(value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REJECTED_PRIVATE_KEYS:
                errors.append("capability_grant_private_payload_rejected")
            _validate_no_private_payloads(child, errors)
    elif isinstance(value, list):
        for child in value:
            _validate_no_private_payloads(child, errors)


def _require_fields(
    data: dict[str, Any],
    fields: set[str],
    errors: list[str],
    reason: str,
) -> None:
    for field_name in sorted(fields):
        if field_name not in data or data.get(field_name) in (None, ""):
            errors.append(f"{reason}:{field_name}")


def _parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> CapabilityGrantCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )
    return CapabilityGrantCaseResult(
        case_id=case_id,
        path=str(path),
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
    )
