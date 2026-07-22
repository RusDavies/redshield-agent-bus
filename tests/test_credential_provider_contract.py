from __future__ import annotations

import json
from pathlib import Path

from agent_bus.credential_provider import verify_provider_contract_path


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "agent_bus" / "credential_providers"


def test_credential_provider_contract_fixture_suite() -> None:
    result = verify_provider_contract_path(FIXTURES)

    case_ids = {case.case_id for case in result.cases}

    assert result.ok is True
    assert len(result.cases) == 11
    assert "valid-local-runtime-token" in case_ids
    assert "valid-keyper-ssh-certificate-evidence" in case_ids
    assert "revoked-credential" in case_ids
    assert "provider-unavailable" in case_ids


def test_credential_provider_contract_expected_failures() -> None:
    result = verify_provider_contract_path(FIXTURES)

    expected_invalid = {
        case.case_id: case
        for case in result.cases
        if case.expected_valid is False
    }

    assert expected_invalid["unknown-credential"].errors == ["credential_unknown"]
    assert expected_invalid["actor-mismatch"].errors == ["actor_id_mismatch"]
    assert expected_invalid["runtime-mismatch"].errors == ["runtime_id_mismatch"]
    assert expected_invalid["scope-mismatch"].errors == [
        "project_scope_mismatch",
        "workspace_scope_mismatch",
    ]


def test_keyper_spike_fixture_stays_behind_provider_boundary() -> None:
    fixture = json.loads(
        (FIXTURES / "valid-keyper-ssh-certificate-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    response = fixture["provider_response"]
    provider_refs = response["provider_specific_refs"]

    assert response["auth_method"] == "ssh_certificate_evidence"
    assert provider_refs["provider"] == "keyper"
    assert provider_refs["record_kind"] == "SshCertificateIssueEvidence"
    assert provider_refs["decision"]["outcome"] == "issued"
    assert set(fixture["agent_bus_consumes"]).issubset(response.keys())
    assert "ssh_private_key" in fixture["agent_bus_does_not_consume"]
