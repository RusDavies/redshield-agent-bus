from __future__ import annotations

from pathlib import Path

from agent_bus.capability_grant import verify_capability_grant_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "capability_grants"


def test_capability_grant_fixture_suite() -> None:
    result = verify_capability_grant_path(FIXTURES)

    assert result.ok is True
    assert len(result.cases) == 3


def test_valid_capability_grant_maps_to_agent_bus_authorization() -> None:
    result = verify_capability_grant_path(FIXTURES / "valid-redshieldworks-core-grant.json")

    assert result.ok is True
    assert result.cases[0].valid is True


def test_expired_capability_grant_fails_closed() -> None:
    result = verify_capability_grant_path(FIXTURES / "invalid-expired-grant.json")

    assert result.ok is True
    assert result.cases[0].valid is False
    assert "capability_grant_expired" in result.cases[0].errors


def test_capability_grant_mapping_cannot_widen_actions() -> None:
    result = verify_capability_grant_path(FIXTURES / "invalid-action-mapping.json")

    assert result.ok is True
    assert result.cases[0].valid is False
    assert "grant_action_mapping_mismatch" in result.cases[0].errors
