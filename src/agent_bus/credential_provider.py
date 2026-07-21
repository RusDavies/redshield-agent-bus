"""Fixture checks for credential capability provider responses."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ACTIVE_STATUS = "active"
TERMINAL_REJECT_STATUSES = {"disabled", "revoked", "rotated", "expired", "unknown"}
REQUIRED_RESPONSE_FIELDS = {
    "credential_id",
    "actor_id",
    "actor_type",
    "runtime_id",
    "status",
    "expires_at",
    "trust_level",
    "evidence_ref",
}


@dataclass
class CredentialProviderCaseResult:
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
class CredentialProviderVerificationResult:
    path: str
    cases: list[CredentialProviderCaseResult]

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


def verify_provider_contract_path(path: Path) -> CredentialProviderVerificationResult:
    root = path.resolve()
    cases = [_verify_provider_fixture(fixture) for fixture in _fixture_files(root)]
    return CredentialProviderVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_provider_fixture(path: Path) -> CredentialProviderCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _case_result(
            case_id=path.stem,
            path=path,
            errors=["fixture_json_invalid"],
            expect={},
        )

    errors = _validate_provider_fixture(fixture)
    return _case_result(
        case_id=str(fixture.get("case_id") or path.stem),
        path=path,
        errors=errors,
        expect=fixture.get("expect", {}),
    )


def _validate_provider_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    request = fixture.get("request")
    response = fixture.get("provider_response")

    if not isinstance(request, dict):
        return ["provider_request_missing"]
    if request.get("proof_present") is not True:
        errors.append("credential_proof_missing")

    if not isinstance(response, dict):
        errors.append(str(fixture.get("provider_error") or "provider_response_missing"))
        return _stable_errors(errors)

    _require_fields(response, REQUIRED_RESPONSE_FIELDS, errors, "provider_response_field_missing")
    _validate_provider_status(response, errors)
    _validate_bindings(request, response, errors)
    _validate_scope(request, response, errors)
    _validate_expiry(response, fixture.get("trusted_time"), errors)

    return _stable_errors(errors)


def _validate_provider_status(response: dict[str, Any], errors: list[str]) -> None:
    status = response.get("status")
    if status == ACTIVE_STATUS:
        return
    if status in TERMINAL_REJECT_STATUSES:
        errors.append(f"credential_{status}")
    else:
        errors.append("credential_status_unsupported")


def _validate_bindings(
    request: dict[str, Any],
    response: dict[str, Any],
    errors: list[str],
) -> None:
    if response.get("credential_id") != request.get("credential_id"):
        errors.append("credential_id_mismatch")
    if response.get("actor_id") != request.get("actor_id"):
        errors.append("actor_id_mismatch")
    if response.get("actor_type") != request.get("actor_type"):
        errors.append("actor_type_mismatch")
    if response.get("runtime_id") != request.get("runtime_id"):
        errors.append("runtime_id_mismatch")


def _validate_scope(
    request: dict[str, Any],
    response: dict[str, Any],
    errors: list[str],
) -> None:
    scopes = response.get("scope_bindings")
    if not isinstance(scopes, dict):
        errors.append("scope_bindings_missing")
        return

    workspace_ids = set(scopes.get("workspace_ids") or [])
    project_slugs = set(scopes.get("project_slugs") or [])

    if request.get("workspace_id") not in workspace_ids:
        errors.append("workspace_scope_mismatch")
    if request.get("project_slug") not in project_slugs:
        errors.append("project_scope_mismatch")


def _validate_expiry(
    response: dict[str, Any],
    trusted_time: str | None,
    errors: list[str],
) -> None:
    expires_at = response.get("expires_at")
    if not expires_at:
        return
    if not trusted_time:
        return
    try:
        expires = _parse_time(str(expires_at))
        now = _parse_time(trusted_time)
    except ValueError:
        errors.append("credential_expiry_invalid")
        return
    if expires <= now:
        errors.append("credential_expired")


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> CredentialProviderCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))

    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )

    return CredentialProviderCaseResult(
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


def _parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _stable_errors(errors: list[str]) -> list[str]:
    return sorted(set(errors))
