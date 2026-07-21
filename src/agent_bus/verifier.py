"""Fixture-driven verifier for the first local-only agent-bus prototype."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUPPORTED_INTERACTIONS = {
    "notify",
    "ask",
    "instruct",
    "delegate",
    "handoff",
    "consult",
    "escalate",
}
DEFERRED_INTERACTIONS = {"broadcast", "subscribe"}

REQUIRED_ENVELOPE_FIELDS = {
    "message_id",
    "correlation_id",
    "idempotency_key",
    "interaction_type",
    "created_at",
    "expires_at",
    "auth",
    "source",
    "target",
    "requester",
    "authorization_context",
    "delivery_expectation",
    "context_package",
    "privacy_classification",
    "safety_flags",
    "requested_output",
}
REQUIRED_AUTH_FIELDS = {
    "actor_id",
    "actor_type",
    "runtime_id",
    "credential_id",
    "auth_method",
    "authenticated_at",
}
REQUIRED_SOURCE_FIELDS = {
    "source_surface",
    "source_conversation_id",
    "source_event_id",
    "source_agent_id",
    "runtime_id",
    "workspace_id",
}
REQUIRED_AUTHZ_FIELDS = {
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
}
RISKY_ACTION_FLAGS = {
    "external_action": "external_action",
    "public_action": "public_action",
    "destructive_action": "destructive_action",
    "sensitive_data_action": "sensitive_data",
    "private_data_action": "private_data",
    "runtime_event_action": "runtime_event",
    "customer_impacting_action": "customer_impacting",
}
SUPPORTED_DELIVERY_EXPECTATIONS = {
    "visible_chat_reply",
    "internal_result",
    "project_file_update",
    "ops_report",
    "followup_bus_message",
}
SUPPORTED_CONTEXT_REFERENCE_TYPES = {
    "source_event",
    "project_file",
    "requirements_doc",
    "security_doc",
    "architecture_doc",
    "fixture",
    "audit_event",
}
REJECTED_CONTEXT_REFERENCE_TYPES = {
    "private_memory",
    "raw_chat_history",
    "credential",
    "secret",
    "external_url",
    "production_runtime_state",
    "unrelated_project_file",
    "customer_data",
    "unknown",
}
ALLOWED_COPY_MODES = {"reference_only", "sanitized_excerpt", "metadata_only"}
REJECTED_COPY_MODES = {
    "raw_content",
    "full_chat_transcript",
    "private_memory_dump",
    "secret_value",
    "credential_material",
}
TERMINAL_STATES = {"completed", "failed", "expired", "cancelled", "rejected"}
STATE_TRANSITIONS = {
    "created": {"queued", "rejected", "expired", "cancelled"},
    "queued": {"claimed", "expired", "cancelled", "rejected"},
    "claimed": {"in_progress", "needs_input", "completed", "failed", "cancelled"},
    "in_progress": {"needs_input", "completed", "failed", "cancelled"},
    "needs_input": {"in_progress", "failed", "cancelled", "expired"},
}


@dataclass
class CaseResult:
    case_id: str
    path: str
    kind: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    expected_valid: bool | None = None
    expected_errors: list[str] = field(default_factory=list)
    expectation_met: bool = True
    audit_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "path": self.path,
            "kind": self.kind,
            "valid": self.valid,
            "errors": self.errors,
            "expected_valid": self.expected_valid,
            "expected_errors": self.expected_errors,
            "expectation_met": self.expectation_met,
            "audit_events": self.audit_events,
        }


@dataclass
class VerificationResult:
    path: str
    cases: list[CaseResult]

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


def verify_path(path: Path) -> VerificationResult:
    root = path.resolve()
    files = _fixture_files(root)
    idempotency_payloads: dict[str, str] = {}
    cases = [
        _verify_fixture_file(fixture, idempotency_payloads)
        for fixture in files
    ]
    return VerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(
        fixture
        for fixture in path.rglob("*.json")
        if "credential_providers" not in fixture.parts
        and "ecosystem" not in fixture.parts
    )


def _verify_fixture_file(
    path: Path,
    idempotency_payloads: dict[str, str],
) -> CaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture = _resolve_extends(fixture, path)
    except (OSError, json.JSONDecodeError):
        return _case_result(
            case_id=path.stem,
            path=path,
            kind="unknown",
            errors=["fixture_json_invalid"],
            expect={},
            audit_events=[],
        )

    kind = _fixture_kind(fixture, path)
    if kind == "transition":
        errors, audit_events = _verify_transition_fixture(fixture, path)
    else:
        errors, audit_events = _verify_envelope_fixture(
            fixture,
            path,
            idempotency_payloads,
        )

    return _case_result(
        case_id=str(fixture.get("case_id") or path.stem),
        path=path,
        kind=kind,
        errors=errors,
        expect=fixture.get("expect", {}),
        audit_events=audit_events,
    )


def _fixture_kind(fixture: dict[str, Any], path: Path) -> str:
    if "events" in fixture or "transitions" in path.parts:
        return "transition"
    return "envelope"


def _case_result(
    case_id: str,
    path: Path,
    kind: str,
    errors: list[str],
    expect: dict[str, Any],
    audit_events: list[dict[str, Any]],
) -> CaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))

    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )

    return CaseResult(
        case_id=case_id,
        path=str(path),
        kind=kind,
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
        audit_events=audit_events,
    )


def _verify_envelope_fixture(
    fixture: dict[str, Any],
    path: Path,
    idempotency_payloads: dict[str, str],
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    envelope = fixture.get("envelope")
    if not isinstance(envelope, dict):
        return ["envelope_missing"], [_audit(fixture, "validation", "rejected", "envelope_missing")]

    _require_fields(envelope, REQUIRED_ENVELOPE_FIELDS, errors, "envelope_field_missing")
    _validate_interaction(envelope, errors)
    _validate_auth(envelope.get("auth"), errors)
    _validate_source(envelope.get("source"), errors)
    _validate_target(envelope.get("target"), errors)
    _validate_expiry(envelope.get("expires_at"), fixture.get("trusted_time"), errors, "message_expired")
    _validate_authorization_context(envelope, fixture.get("trusted_time"), errors)
    _validate_context_package(envelope, errors)
    _validate_delivery_expectation(envelope, errors)
    _validate_idempotency(envelope, idempotency_payloads, errors)

    audit_events = [
        _audit(
            fixture,
            "validation",
            "accepted" if not errors else "rejected",
            "ok" if not errors else errors[0],
            envelope=envelope,
        )
    ]
    return _stable_errors(errors), audit_events


def _validate_interaction(envelope: dict[str, Any], errors: list[str]) -> None:
    interaction = envelope.get("interaction_type")
    if interaction in DEFERRED_INTERACTIONS:
        errors.append("interaction_type_deferred")
    elif interaction not in SUPPORTED_INTERACTIONS:
        errors.append("interaction_type_unsupported")


def _validate_auth(auth: Any, errors: list[str]) -> None:
    if not isinstance(auth, dict):
        errors.append("auth_missing")
        return
    _require_fields(auth, REQUIRED_AUTH_FIELDS, errors, "auth_field_missing")
    if auth.get("actor_display_name") and not auth.get("actor_id"):
        errors.append("display_name_only_identity")
    if auth.get("credential_id") == "credential_unknown":
        errors.append("credential_unknown")


def _validate_source(source: Any, errors: list[str]) -> None:
    if not isinstance(source, dict):
        errors.append("source_missing")
        return
    _require_fields(source, REQUIRED_SOURCE_FIELDS, errors, "source_field_missing")


def _validate_target(target: Any, errors: list[str]) -> None:
    if not isinstance(target, dict):
        errors.append("target_missing")
        return
    if not target.get("target_agent_id") and not target.get("target_role"):
        errors.append("target_ambiguous")


def _validate_authorization_context(
    envelope: dict[str, Any],
    trusted_time: str | None,
    errors: list[str],
) -> None:
    authz = envelope.get("authorization_context")
    if not isinstance(authz, dict):
        errors.append("authorization_context_missing")
        return

    _require_fields(authz, REQUIRED_AUTHZ_FIELDS, errors, "authorization_field_missing")
    if authz.get("schema_version") != "authzctx.v1":
        errors.append("authorization_context_schema_unsupported")
    if not authz.get("authorization_id"):
        errors.append("authorization_id_missing")
    if not authz.get("source_event_ids"):
        errors.append("authorization_source_event_missing")

    basis = authz.get("basis")
    if not isinstance(basis, dict):
        errors.append("authorization_basis_missing")
    else:
        if basis.get("summary_is_authorization") is not False:
            errors.append("summarized_context_not_authorization")
        if basis.get("kind") == "explicit_approval" and not basis.get("approval_event_ids"):
            errors.append("explicit_approval_event_missing")
        if basis.get("kind") in {"standing_policy", "operator_action", "system_rule"}:
            errors.append("authorization_basis_deferred")

    if envelope.get("interaction_type") not in set(authz.get("allowed_interaction_types") or []):
        errors.append("interaction_type_not_authorized")

    safety = authz.get("safety_authorizations")
    allowed_actions = set(authz.get("allowed_action_classes") or [])
    if isinstance(safety, dict):
        for action_class, safety_flag in RISKY_ACTION_FLAGS.items():
            if action_class in allowed_actions and safety.get(safety_flag) is not True:
                errors.append("risky_action_requires_explicit_authorization")
    else:
        errors.append("authorization_safety_missing")

    _validate_scope(envelope, authz, errors)
    _validate_expiry(authz.get("expires_at"), trusted_time, errors, "authorization_expired")

    safety_flags = envelope.get("safety_flags")
    if isinstance(safety_flags, dict) and safety_flags.get("runtime_event_boundary"):
        if "runtime_event_action" not in set(authz.get("allowed_action_classes") or []):
            errors.append("runtime_event_boundary_misuse")


def _validate_scope(envelope: dict[str, Any], authz: dict[str, Any], errors: list[str]) -> None:
    scope = authz.get("scope")
    if not isinstance(scope, dict):
        errors.append("authorization_scope_missing")
        return

    source = envelope.get("source") if isinstance(envelope.get("source"), dict) else {}
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}

    if scope.get("workspace_id") and source.get("workspace_id") != scope.get("workspace_id"):
        errors.append("scope_workspace_mismatch")
    if scope.get("project_slug") and source.get("project_slug") != scope.get("project_slug"):
        errors.append("scope_project_mismatch")

    allowed_agents = set(scope.get("target_agent_ids") or [])
    allowed_roles = set(scope.get("target_roles") or [])
    target_agent = target.get("target_agent_id")
    target_role = target.get("target_role")
    if target_agent and allowed_agents and target_agent not in allowed_agents:
        errors.append("scope_target_mismatch")
    if target_role and allowed_roles and target_role not in allowed_roles:
        errors.append("scope_target_mismatch")


def _validate_context_package(envelope: dict[str, Any], errors: list[str]) -> None:
    package = envelope.get("context_package")
    if not isinstance(package, dict):
        errors.append("context_package_missing")
        return
    if package.get("schema_version") != "ctxpkg.v1":
        errors.append("context_package_schema_unsupported")
    if not package.get("package_id"):
        errors.append("context_package_id_missing")
    if _claims_authorization(package.get("summary")) or _claims_authorization(package.get("notes")):
        errors.append("context_summary_claims_authorization")

    authz = envelope.get("authorization_context") if isinstance(envelope.get("authorization_context"), dict) else {}
    constraints = authz.get("constraints") if isinstance(authz.get("constraints"), dict) else {}
    allowed_ref_types = set(constraints.get("allowed_context_reference_types") or [])
    safety = authz.get("safety_authorizations") if isinstance(authz.get("safety_authorizations"), dict) else {}

    for reference in package.get("references") or []:
        if not isinstance(reference, dict):
            errors.append("context_reference_invalid")
            continue
        ref_type = reference.get("type")
        copy_mode = reference.get("copy_mode")
        privacy = reference.get("privacy_classification")

        if ref_type in REJECTED_CONTEXT_REFERENCE_TYPES or ref_type not in SUPPORTED_CONTEXT_REFERENCE_TYPES:
            errors.append("context_reference_type_not_allowed")
        if allowed_ref_types and ref_type not in allowed_ref_types:
            errors.append("context_reference_type_not_allowed")
        if copy_mode in REJECTED_COPY_MODES or copy_mode not in ALLOWED_COPY_MODES:
            errors.append("context_copy_mode_rejected")
        if privacy == "secret":
            errors.append("context_secret_rejected")
        if privacy == "private" and safety.get("private_data") is not True:
            errors.append("context_private_data_not_authorized")
        if privacy == "sensitive" and safety.get("sensitive_data") is not True:
            errors.append("context_sensitive_data_not_authorized")
        if reference.get("redaction_status") == "rejected":
            errors.append("context_redaction_required")


def _validate_delivery_expectation(envelope: dict[str, Any], errors: list[str]) -> None:
    delivery = envelope.get("delivery_expectation")
    if not isinstance(delivery, dict):
        errors.append("delivery_expectation_missing")
        return
    delivery_type = delivery.get("type")
    if delivery_type not in SUPPORTED_DELIVERY_EXPECTATIONS:
        errors.append("delivery_expectation_unsupported")
    if delivery_type == "visible_chat_reply":
        if not delivery.get("target_surface") or not delivery.get("source_conversation_id"):
            errors.append("delivery_expectation_missing_destination")
        source = envelope.get("source")
        if isinstance(source, dict) and delivery.get("source_conversation_id") != source.get("source_conversation_id"):
            errors.append("wrong_destination_delivery")


def _validate_idempotency(
    envelope: dict[str, Any],
    idempotency_payloads: dict[str, str],
    errors: list[str],
) -> None:
    key = envelope.get("idempotency_key")
    if not key:
        return
    payload_hash = _canonical_hash(envelope)
    previous = idempotency_payloads.setdefault(str(key), payload_hash)
    if previous != payload_hash:
        errors.append("idempotency_conflict")


def _verify_transition_fixture(
    fixture: dict[str, Any],
    path: Path,
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    state = fixture.get("initial_state")
    events = fixture.get("events")
    target_agent_id = fixture.get("target_agent_id")
    audit_events: list[dict[str, Any]] = []

    if not isinstance(state, str):
        errors.append("transition_initial_state_missing")
        state = "created"
    if not isinstance(events, list):
        errors.append("transition_events_missing")
        events = []

    for event in events:
        if not isinstance(event, dict):
            errors.append("transition_event_invalid")
            continue
        target_state = event.get("to")
        actor_id = event.get("actor_id")
        reason = "ok"
        accepted = True

        if not actor_id:
            errors.append("transition_actor_missing")
            reason = "transition_actor_missing"
            accepted = False
        elif state in TERMINAL_STATES:
            errors.append("transition_from_terminal_state")
            reason = "transition_from_terminal_state"
            accepted = False
        elif target_state not in STATE_TRANSITIONS.get(state, set()):
            errors.append("transition_invalid")
            reason = "transition_invalid"
            accepted = False
        elif target_state == "claimed" and target_agent_id and actor_id != target_agent_id:
            errors.append("target_claim_mismatch")
            reason = "target_claim_mismatch"
            accepted = False

        audit_events.append(
            _audit(
                fixture,
                "state_transition",
                "accepted" if accepted else "rejected",
                reason,
                actor_id=actor_id,
                actor_type=event.get("actor_type"),
                state_before=state,
                state_after=target_state if accepted else None,
            )
        )
        if accepted:
            state = target_state

    expected_final = (fixture.get("expect") or {}).get("final_state")
    if expected_final and state != expected_final:
        errors.append("transition_final_state_mismatch")

    return _stable_errors(errors), audit_events


def _require_fields(
    data: dict[str, Any],
    fields: set[str],
    errors: list[str],
    reason: str,
) -> None:
    for field_name in sorted(fields):
        if field_name not in data or data.get(field_name) in (None, ""):
            errors.append(f"{reason}:{field_name}")


def _resolve_extends(fixture: dict[str, Any], path: Path) -> dict[str, Any]:
    parent_ref = fixture.get("extends")
    if not parent_ref:
        return fixture
    parent_path = (path.parent / str(parent_ref)).resolve()
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    parent = _resolve_extends(parent, parent_path)
    merged = _deep_merge(parent, {key: value for key, value in fixture.items() if key != "extends"})
    return merged


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            merged[key] = _deep_merge(merged.get(key), value)
        return merged
    return override


def _validate_expiry(
    value: Any,
    trusted_time: str | None,
    errors: list[str],
    reason: str,
) -> None:
    if not value:
        return
    if not trusted_time:
        return
    try:
        expires_at = _parse_time(str(value))
        now = _parse_time(trusted_time)
    except ValueError:
        errors.append(f"{reason}:invalid_timestamp")
        return
    if expires_at <= now:
        errors.append(reason)


def _parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _claims_authorization(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return "authorized by summary" in lowered or "summary grants" in lowered


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _audit(
    fixture: dict[str, Any],
    event_type: str,
    result: str,
    reason: str,
    envelope: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    envelope = envelope or fixture.get("envelope") or {}
    return {
        "case_id": fixture.get("case_id"),
        "event_type": event_type,
        "message_id": envelope.get("message_id"),
        "correlation_id": envelope.get("correlation_id"),
        "actor_id": (envelope.get("auth") or {}).get("actor_id") if isinstance(envelope.get("auth"), dict) else None,
        "actor_type": (envelope.get("auth") or {}).get("actor_type") if isinstance(envelope.get("auth"), dict) else None,
        "result": result,
        "reason": reason,
        **extra,
    }


def _stable_errors(errors: list[str]) -> list[str]:
    return sorted(set(errors))
