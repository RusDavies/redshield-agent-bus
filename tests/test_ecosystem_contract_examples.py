"""Shape checks for public-safe ecosystem contract examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_bus.ecosystem_contract import verify_ecosystem_contract_path


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_bus" / "ecosystem"
EXPECTED_FIXTURES = {
    "rsk-ai-auth-capability-grant.json",
    "keyper-credential-evidence.json",
    "warden-policy-result.json",
    "armor-enforcement-result.json",
}


def test_ecosystem_fixture_set_is_present() -> None:
    assert {path.name for path in FIXTURE_DIR.glob("*.json")} == EXPECTED_FIXTURES


def test_ecosystem_contract_fixture_suite() -> None:
    result = verify_ecosystem_contract_path(FIXTURE_DIR)

    assert result.ok is True
    assert len(result.cases) == 4


def test_ecosystem_contract_rejects_private_material(tmp_path: Path) -> None:
    fixture = _load("keyper-credential-evidence.json")
    fixture["provider_response"]["ssh_private_key"] = "redacted-test-private-key"
    fixture["expect"] = {
        "valid": False,
        "errors": ["ecosystem_private_material_rejected"],
    }
    path = tmp_path / "keyper-private-material.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    result = verify_ecosystem_contract_path(path)

    assert result.ok is True
    assert result.cases[0].valid is False
    assert "ecosystem_private_material_rejected" in result.cases[0].errors


def test_ecosystem_contract_rejects_bad_rsk_mapping(tmp_path: Path) -> None:
    fixture = _load("rsk-ai-auth-capability-grant.json")
    fixture["agent_bus_authorization_context"]["authorization_id"] = "grant_forged"
    fixture["expect"] = {
        "valid": False,
        "errors": ["grant_authorization_id_mismatch"],
    }
    path = tmp_path / "rsk-bad-mapping.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    result = verify_ecosystem_contract_path(path)

    assert result.ok is True
    assert result.cases[0].valid is False
    assert "grant_authorization_id_mismatch" in result.cases[0].errors


def test_ecosystem_contract_rejects_incomplete_warden_coverage(tmp_path: Path) -> None:
    fixture = _load("warden-policy-result.json")
    fixture["policy_results"] = [
        result for result in fixture["policy_results"] if result["decision"] != "deny"
    ]
    fixture["expect"] = {
        "valid": False,
        "errors": ["warden_policy_decision_coverage_incomplete"],
    }
    path = tmp_path / "warden-incomplete.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    result = verify_ecosystem_contract_path(path)

    assert result.ok is True
    assert result.cases[0].valid is False
    assert "warden_policy_decision_coverage_incomplete" in result.cases[0].errors


def test_ecosystem_contract_rejects_incomplete_armor_coverage(tmp_path: Path) -> None:
    fixture = _load("armor-enforcement-result.json")
    fixture["enforcement_results"] = [
        result for result in fixture["enforcement_results"] if result["decision"] != "block"
    ]
    fixture["expect"] = {
        "valid": False,
        "errors": ["armor_enforcement_decision_coverage_incomplete"],
    }
    path = tmp_path / "armor-incomplete.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    result = verify_ecosystem_contract_path(path)

    assert result.ok is True
    assert result.cases[0].valid is False
    assert "armor_enforcement_decision_coverage_incomplete" in result.cases[0].errors


def test_rsk_ai_auth_grant_maps_to_authorization_context() -> None:
    fixture = _load("rsk-ai-auth-capability-grant.json")
    grant = fixture["capability_grant"]
    authz = fixture["agent_bus_authorization_context"]

    assert authz["authorization_id"] == grant["grant_id"]
    assert authz["source_event_ids"] == grant["delegated_by"]["source_event_ids"]
    assert authz["allowed_interaction_types"] == grant["allowed_interaction_types"]
    assert authz["allowed_action_classes"] == grant["allowed_action_classes"]
    assert authz["expires_at"] == grant["expires_at"]
    assert authz["basis"]["summary_is_authorization"] is False


def test_keyper_example_stays_behind_provider_contract() -> None:
    fixture = _load("keyper-credential-evidence.json")
    response = fixture["provider_response"]

    assert fixture["credential_provider"] == "keyper"
    assert response["status"] == "active"
    assert "ssh_private_key" in fixture["agent_bus_does_not_consume"]
    assert set(fixture["agent_bus_consumes"]).issubset(response.keys())


def test_warden_policy_result_decisions_are_explicit() -> None:
    fixture = _load("warden-policy-result.json")
    decisions = {result["decision"] for result in fixture["policy_results"]}

    assert decisions == {"allow", "deny", "require_review"}
    for result in fixture["policy_results"]:
        assert result["reason_codes"]
        assert result["evidence_refs"]


def test_armor_enforcement_result_decisions_are_explicit() -> None:
    fixture = _load("armor-enforcement-result.json")
    decisions = {result["decision"] for result in fixture["enforcement_results"]}

    assert decisions == {"allow", "block", "sanitize", "require_review"}
    for result in fixture["enforcement_results"]:
        assert result["enforcement_target"]
        assert result["finding_codes"]
        assert result["evidence_refs"]


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
