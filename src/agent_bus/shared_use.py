"""Shared-use limits, quotas, claim authorization, and monitoring verifier."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .verifier import _resolve_extends, _stable_errors


REQUIRED_FIELDS = {
    "schema_version",
    "profile_id",
    "scope",
    "rate_limits",
    "quota_limits",
    "claim_authorization",
    "stale_work_monitoring",
    "evidence_refs",
}
ALLOWED_RATE_SCOPES = {"actor", "runtime", "workspace", "project", "target", "source_surface"}
ALLOWED_CLAIM_MODES = {"exact_agent", "role_with_runtime_allowlist"}


@dataclass
class SharedUseCaseResult:
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
class SharedUseVerificationResult:
    path: str
    cases: list[SharedUseCaseResult]

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


def verify_shared_use_path(path: Path) -> SharedUseVerificationResult:
    root = path.resolve()
    cases = [_verify_fixture(fixture) for fixture in _fixture_files(root)]
    return SharedUseVerificationResult(path=str(root), cases=cases)


def _fixture_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.rglob("*.json"))


def _verify_fixture(path: Path) -> SharedUseCaseResult:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture = _resolve_extends(fixture, path)
    except (OSError, json.JSONDecodeError):
        return _case_result(path.stem, path, ["fixture_json_invalid"], {})

    profile = fixture.get("shared_use_profile")
    if not isinstance(profile, dict):
        return _case_result(str(fixture.get("case_id") or path.stem), path, ["shared_use_profile_missing"], fixture.get("expect", {}))

    errors: list[str] = []
    _validate_profile(profile, errors)
    return _case_result(str(fixture.get("case_id") or path.stem), path, _stable_errors(errors), fixture.get("expect", {}))


def _validate_profile(profile: dict[str, Any], errors: list[str]) -> None:
    for field_name in sorted(REQUIRED_FIELDS):
        if field_name not in profile or profile.get(field_name) in (None, "", []):
            errors.append(f"shared_use_field_missing:{field_name}")

    if profile.get("schema_version") != "shareduse.v1":
        errors.append("shared_use_schema_unsupported")

    scope = profile.get("scope") if isinstance(profile.get("scope"), dict) else {}
    if scope.get("mode") not in {"owner_only_trial", "shared", "production"}:
        errors.append("shared_use_scope_mode_unsupported")
    if not scope.get("workspace_id") or not scope.get("project_slug"):
        errors.append("shared_use_scope_missing")

    _validate_rate_limits(profile.get("rate_limits"), errors)
    _validate_quotas(profile.get("quota_limits"), errors)
    _validate_claim_authorization(profile.get("claim_authorization"), errors)
    _validate_monitoring(profile.get("stale_work_monitoring"), errors)

    if not all(isinstance(ref, str) and ref.startswith("evidence:") for ref in profile.get("evidence_refs") or []):
        errors.append("shared_use_evidence_ref_invalid")


def _validate_rate_limits(rate_limits: Any, errors: list[str]) -> None:
    if not isinstance(rate_limits, list) or not rate_limits:
        errors.append("rate_limits_missing")
        return
    seen_names: set[str] = set()
    for limit in rate_limits:
        if not isinstance(limit, dict):
            errors.append("rate_limit_invalid")
            continue
        name = limit.get("name")
        if not name or name in seen_names:
            errors.append("rate_limit_name_invalid")
        seen_names.add(str(name))
        if limit.get("scope") not in ALLOWED_RATE_SCOPES:
            errors.append("rate_limit_scope_unsupported")
        if not _positive_int(limit.get("window_seconds")) or not _positive_int(limit.get("max_messages")):
            errors.append("rate_limit_value_invalid")


def _validate_quotas(quotas: Any, errors: list[str]) -> None:
    if not isinstance(quotas, dict):
        errors.append("quota_limits_missing")
        return
    for field_name in ("daily_message_limit", "daily_claim_limit", "max_inflight_claims"):
        if not _positive_int(quotas.get(field_name)):
            errors.append(f"quota_limit_invalid:{field_name}")


def _validate_claim_authorization(claim: Any, errors: list[str]) -> None:
    if not isinstance(claim, dict):
        errors.append("claim_authorization_missing")
        return
    if claim.get("require_actor_binding") is not True:
        errors.append("claim_actor_binding_required")
    modes = claim.get("allowed_claim_modes")
    if not isinstance(modes, list) or not modes:
        errors.append("claim_modes_missing")
    elif any(mode not in ALLOWED_CLAIM_MODES for mode in modes):
        errors.append("claim_mode_unsupported")
    if claim.get("allow_display_name_claims") is not False:
        errors.append("display_name_claims_forbidden")
    if claim.get("allow_actorless_transitions") is not False:
        errors.append("actorless_transitions_forbidden")


def _validate_monitoring(monitoring: Any, errors: list[str]) -> None:
    if not isinstance(monitoring, dict):
        errors.append("stale_work_monitoring_missing")
        return
    for field_name in ("pending_age_threshold_seconds", "claimed_age_threshold_seconds"):
        if not _positive_int(monitoring.get(field_name)):
            errors.append(f"stale_work_threshold_invalid:{field_name}")
    if not monitoring.get("alert_destination_ref"):
        errors.append("stale_work_alert_destination_missing")
    if monitoring.get("missing_receipt_detection") is not True:
        errors.append("missing_receipt_detection_required")
    if monitoring.get("wrong_destination_detection") is not True:
        errors.append("wrong_destination_detection_required")


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and value > 0


def _case_result(
    case_id: str,
    path: Path,
    errors: list[str],
    expect: dict[str, Any],
) -> SharedUseCaseResult:
    valid = not errors
    expected_valid = expect.get("valid")
    expected_errors = list(expect.get("errors", []))
    if expected_valid is None:
        expectation_met = valid
    else:
        expectation_met = valid is bool(expected_valid) and all(
            error in errors for error in expected_errors
        )
    return SharedUseCaseResult(
        case_id=case_id,
        path=str(path),
        valid=valid,
        errors=errors,
        expected_valid=expected_valid,
        expected_errors=expected_errors,
        expectation_met=expectation_met,
    )
