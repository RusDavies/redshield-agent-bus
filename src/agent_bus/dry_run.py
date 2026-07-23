"""Local-only live-adapter dry-run preview and receipt validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .verifier import (
    _canonical_hash,
    _deep_merge,
    _resolve_extends,
    _stable_errors,
)
from .target_resolver import build_route_resolution


REQUIRED_CAPABILITY_FIELDS = {
    "schema_version",
    "adapter_id",
    "adapter_type",
    "surface",
    "mode",
    "supports_delivery_expectations",
    "supports_interaction_types",
    "forbidden_capabilities",
    "receipt_schema_version",
}
REQUIRED_PREVIEW_FIELDS = {
    "schema_version",
    "preview_id",
    "message_id",
    "correlation_id",
    "idempotency_key",
    "adapter_id",
    "adapter_type",
    "surface",
    "mode",
    "source",
    "destination",
    "delivery_expectation",
    "route_resolution",
    "payload_preview",
    "safety",
}
REQUIRED_RECEIPT_FIELDS = {
    "schema_version",
    "receipt_id",
    "preview_id",
    "message_id",
    "correlation_id",
    "adapter_id",
    "adapter_type",
    "surface",
    "mode",
    "result",
    "reason",
    "destination",
    "delivery_expectation",
    "side_effect_performed",
    "payload_hash",
    "created_at",
}
REQUIRED_FORBIDDEN_CAPABILITIES = {
    "live_send",
    "session_spawn",
    "gateway_call",
    "queue_publish",
}
SUPPORTED_RECEIPT_RESULTS = {"accepted", "rejected"}


@dataclass
class DryRunCaseResult:
    case_id: str
    path: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    expected_valid: bool | None = None
    expected_errors: list[str] = field(default_factory=list)
    expectation_met: bool = True
    preview_request: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None
    audit_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "path": self.path,
            "valid": self.valid,
            "errors": self.errors,
            "expected_valid": self.expected_valid,
            "expected_errors": self.expected_errors,
            "expectation_met": self.expectation_met,
            "preview_request": self.preview_request,
            "receipt": self.receipt,
            "audit_events": self.audit_events,
        }


@dataclass
class DryRunVerificationResult:
    path: str
    cases: list[DryRunCaseResult]

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


def verify_dry_run_path(path: Path) -> DryRunVerificationResult:
    root = path.resolve()
    cases = [_verify_dry_run_fixture(fixture) for fixture in _fixture_files(root)]
    return DryRunVerificationResult(path=str(root), cases=cases)


def build_preview_request(
    envelope: dict[str, Any],
    adapter_capability: dict[str, Any],
) -> dict[str, Any]:
    delivery = envelope.get("delivery_expectation") if isinstance(envelope.get("delivery_expectation"), dict) else {}
    source = envelope.get("source") if isinstance(envelope.get("source"), dict) else {}
    requested_output = envelope.get("requested_output") if isinstance(envelope.get("requested_output"), dict) else {}
    context_package = envelope.get("context_package") if isinstance(envelope.get("context_package"), dict) else {}
    content_hash = _canonical_hash(
        {
            "message_id": envelope.get("message_id"),
            "requested_output": requested_output,
            "context_package_id": context_package.get("package_id"),
        }
    )
    route_resolution = build_route_resolution(envelope, adapter_capability)

    return {
        "schema_version": "adapterpreview.v1",
        "preview_id": f"preview_{envelope.get('message_id')}",
        "message_id": envelope.get("message_id"),
        "correlation_id": envelope.get("correlation_id"),
        "idempotency_key": envelope.get("idempotency_key"),
        "adapter_id": adapter_capability.get("adapter_id"),
        "adapter_type": adapter_capability.get("adapter_type"),
        "surface": adapter_capability.get("surface"),
        "mode": "dry_run",
        "source": {
            "surface": source.get("source_surface"),
            "conversation_id": source.get("source_conversation_id"),
            "event_id": source.get("source_event_id"),
        },
        "destination": {
            "surface": delivery.get("target_surface"),
            "conversation_id": delivery.get("source_conversation_id"),
            "thread_id": delivery.get("thread_id"),
        },
        "delivery_expectation": {
            "type": delivery.get("type"),
        },
        "route_resolution": route_resolution,
        "payload_preview": {
            "content_hash": content_hash,
            "redacted_summary": f"Would deliver {requested_output.get('shape', 'result')}.",
        },
        "safety": {
            "live_side_effect_allowed": False,
            "external_action_allowed": False,
            "private_data_included": _contains_private_data(envelope),
        },
    }


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_dry_run_fixture(path: Path) -> DryRunCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture = _resolve_extends(fixture, path)
        if "envelope_fixture" in fixture:
            fixture = _merge_envelope_fixture(fixture, path)
    except (OSError, json.JSONDecodeError):
        return _case_result(path.stem, path, ["fixture_json_invalid"], {}, None, None, [])

    envelope = fixture.get("envelope")
    capability = fixture.get("adapter_capability")
    if not isinstance(envelope, dict):
        return _case_result(
            str(fixture.get("case_id") or path.stem),
            path,
            ["envelope_missing"],
            fixture.get("expect", {}),
            None,
            None,
            [],
        )
    if not isinstance(capability, dict):
        return _case_result(
            str(fixture.get("case_id") or path.stem),
            path,
            ["adapter_capability_missing"],
            fixture.get("expect", {}),
            None,
            None,
            [],
        )

    preview = fixture.get("adapter_preview_request")
    if not isinstance(preview, dict):
        preview = build_preview_request(envelope, capability)
    receipt = fixture.get("dry_run_delivery_receipt")

    errors: list[str] = []
    _validate_capability(envelope, capability, errors)
    _validate_preview(envelope, capability, preview, errors)
    _validate_receipt(preview, receipt, bool((fixture.get("expect") or {}).get("receipt_required")), errors)

    audit_events = [
        _audit(
            fixture,
            preview,
            receipt if isinstance(receipt, dict) else None,
            "accepted" if not errors else "rejected",
            "would_deliver" if not errors else errors[0],
        )
    ]
    return _case_result(
        str(fixture.get("case_id") or path.stem),
        path,
        _stable_errors(errors),
        fixture.get("expect", {}),
        preview,
        receipt if isinstance(receipt, dict) else None,
        audit_events,
    )


def _merge_envelope_fixture(fixture: dict[str, Any], path: Path) -> dict[str, Any]:
    envelope_path = (path.parent / str(fixture["envelope_fixture"])).resolve()
    envelope_fixture = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope_fixture = _resolve_extends(envelope_fixture, envelope_path)
    merged = _deep_merge({"envelope": envelope_fixture.get("envelope")}, fixture)
    merged.pop("envelope_fixture", None)
    return merged


def _validate_capability(
    envelope: dict[str, Any],
    capability: dict[str, Any],
    errors: list[str],
) -> None:
    _require_fields(capability, REQUIRED_CAPABILITY_FIELDS, errors, "adapter_capability_field_missing")
    if capability.get("schema_version") != "adaptercap.v1":
        errors.append("adapter_capability_schema_unsupported")
    if capability.get("mode") != "dry_run":
        errors.append("adapter_mode_not_dry_run")
    if capability.get("adapter_display_name") and not capability.get("adapter_id"):
        errors.append("adapter_identity_missing")
    if not capability.get("adapter_id"):
        errors.append("adapter_identity_missing")

    forbidden = set(capability.get("forbidden_capabilities") or [])
    if not REQUIRED_FORBIDDEN_CAPABILITIES.issubset(forbidden):
        errors.append("adapter_forbidden_capabilities_incomplete")

    if envelope.get("interaction_type") not in set(capability.get("supports_interaction_types") or []):
        errors.append("interaction_type_unsupported")

    delivery = envelope.get("delivery_expectation") if isinstance(envelope.get("delivery_expectation"), dict) else {}
    if delivery.get("type") not in set(capability.get("supports_delivery_expectations") or []):
        errors.append("delivery_expectation_unsupported")


def _validate_preview(
    envelope: dict[str, Any],
    capability: dict[str, Any],
    preview: dict[str, Any],
    errors: list[str],
) -> None:
    _require_fields(preview, REQUIRED_PREVIEW_FIELDS, errors, "preview_field_missing")
    if preview.get("schema_version") != "adapterpreview.v1":
        errors.append("preview_schema_unsupported")
    if preview.get("mode") != "dry_run":
        errors.append("adapter_mode_not_dry_run")
    for field_name in ("message_id", "correlation_id", "idempotency_key"):
        if preview.get(field_name) != envelope.get(field_name):
            errors.append("preview_binding_failed")
    for field_name in ("adapter_id", "adapter_type", "surface"):
        if preview.get(field_name) != capability.get(field_name):
            errors.append("preview_adapter_binding_failed")

    if preview.get("source") != _expected_source(envelope):
        errors.append("source_mismatch")
    if preview.get("destination") != _expected_destination(envelope):
        errors.append("destination_mismatch")
    route_resolution = preview.get("route_resolution")
    if route_resolution != build_route_resolution(envelope, capability):
        errors.append("route_resolution_mismatch")
    elif isinstance(route_resolution, dict) and route_resolution.get("decision") != "resolved":
        errors.append("route_resolution_rejected")

    delivery = envelope.get("delivery_expectation") if isinstance(envelope.get("delivery_expectation"), dict) else {}
    if (preview.get("delivery_expectation") or {}).get("type") != delivery.get("type"):
        errors.append("delivery_expectation_unsupported")

    safety = preview.get("safety")
    if not isinstance(safety, dict):
        errors.append("preview_safety_missing")
        return
    if safety.get("live_side_effect_allowed") is not False or safety.get("external_action_allowed") is not False:
        errors.append("live_side_effect_requested")
    if safety.get("private_data_included") is True:
        errors.append("payload_contains_private_data")

    payload = preview.get("payload_preview")
    if not isinstance(payload, dict):
        errors.append("payload_preview_missing")
        return
    if _raw_private_payload_present(payload):
        errors.append("payload_contains_private_data")


def _validate_receipt(
    preview: dict[str, Any],
    receipt: Any,
    receipt_required: bool,
    errors: list[str],
) -> None:
    if not isinstance(receipt, dict):
        if receipt_required:
            errors.append("receipt_missing")
        return

    _require_fields(receipt, REQUIRED_RECEIPT_FIELDS, errors, "receipt_field_missing")
    if receipt.get("schema_version") != "dryreceipt.v1":
        errors.append("receipt_schema_unsupported")
    if receipt.get("mode") != "dry_run":
        errors.append("adapter_mode_not_dry_run")
    if receipt.get("result") not in SUPPORTED_RECEIPT_RESULTS:
        errors.append("receipt_result_unsupported")
    if receipt.get("side_effect_performed") is not False:
        errors.append("receipt_claims_side_effect")

    bound_fields = {
        "preview_id",
        "message_id",
        "correlation_id",
        "adapter_id",
        "adapter_type",
        "surface",
    }
    for field_name in bound_fields:
        if receipt.get(field_name) != preview.get(field_name):
            errors.append("receipt_binding_failed")
    if receipt.get("destination") != preview.get("destination"):
        errors.append("receipt_binding_failed")
    if receipt.get("delivery_expectation") != preview.get("delivery_expectation"):
        errors.append("receipt_binding_failed")
    if receipt.get("payload_hash") != (preview.get("payload_preview") or {}).get("content_hash"):
        errors.append("receipt_binding_failed")


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
    preview: dict[str, Any] | None,
    receipt: dict[str, Any] | None,
    audit_events: list[dict[str, Any]],
) -> DryRunCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )

    return DryRunCaseResult(
        case_id=case_id,
        path=str(path),
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
        preview_request=preview,
        receipt=receipt,
        audit_events=audit_events,
    )


def _expected_source(envelope: dict[str, Any]) -> dict[str, Any]:
    source = envelope.get("source") if isinstance(envelope.get("source"), dict) else {}
    return {
        "surface": source.get("source_surface"),
        "conversation_id": source.get("source_conversation_id"),
        "event_id": source.get("source_event_id"),
    }


def _expected_destination(envelope: dict[str, Any]) -> dict[str, Any]:
    delivery = envelope.get("delivery_expectation") if isinstance(envelope.get("delivery_expectation"), dict) else {}
    return {
        "surface": delivery.get("target_surface"),
        "conversation_id": delivery.get("source_conversation_id"),
        "thread_id": delivery.get("thread_id"),
    }


def _contains_private_data(envelope: dict[str, Any]) -> bool:
    if envelope.get("privacy_classification") == "private":
        return True
    package = envelope.get("context_package")
    if not isinstance(package, dict):
        return False
    if package.get("privacy_classification") == "private":
        return True
    return any(
        isinstance(reference, dict) and reference.get("privacy_classification") == "private"
        for reference in package.get("references") or []
    )


def _raw_private_payload_present(payload: dict[str, Any]) -> bool:
    blocked_keys = {
        "raw_content",
        "full_chat_transcript",
        "private_memory_dump",
        "secret_value",
        "credential_material",
    }
    return any(key in payload for key in blocked_keys)


def _require_fields(
    data: dict[str, Any],
    fields: set[str],
    errors: list[str],
    reason: str,
) -> None:
    for field_name in sorted(fields):
        if field_name not in data or data.get(field_name) in (None, ""):
            errors.append(f"{reason}:{field_name}")


def _audit(
    fixture: dict[str, Any],
    preview: dict[str, Any],
    receipt: dict[str, Any] | None,
    result: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "case_id": fixture.get("case_id"),
        "event_type": "adapter_dry_run",
        "preview_id": preview.get("preview_id"),
        "receipt_id": receipt.get("receipt_id") if receipt else None,
        "adapter_id": preview.get("adapter_id"),
        "adapter_type": preview.get("adapter_type"),
        "surface": preview.get("surface"),
        "message_id": preview.get("message_id"),
        "correlation_id": preview.get("correlation_id"),
        "delivery_expectation": preview.get("delivery_expectation"),
        "destination": preview.get("destination"),
        "route_resolution": preview.get("route_resolution"),
        "result": result,
        "reason": reason,
        "side_effect_performed": receipt.get("side_effect_performed") if receipt else False,
        "redaction": "payload_hash_only",
    }
