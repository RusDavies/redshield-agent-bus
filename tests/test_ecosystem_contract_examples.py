"""Shape checks for public-safe ecosystem contract examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_bus" / "ecosystem"
EXPECTED_FIXTURES = {
    "rsk-ai-auth-capability-grant.json",
    "keyper-credential-evidence.json",
    "warden-policy-result.json",
    "armor-enforcement-result.json",
}


def test_ecosystem_fixture_set_is_present() -> None:
    assert {path.name for path in FIXTURE_DIR.glob("*.json")} == EXPECTED_FIXTURES


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
