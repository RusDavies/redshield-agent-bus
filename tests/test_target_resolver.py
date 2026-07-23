from __future__ import annotations

import copy
import json
from pathlib import Path

from agent_bus.target_resolver import build_route_resolution


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "adapter_dry_runs"


def test_resolver_records_exact_target_and_route_preview() -> None:
    envelope, capability = _load_valid_envelope_and_capability()

    resolution = build_route_resolution(envelope, capability)

    assert resolution["decision"] == "resolved"
    assert resolution["reason_codes"] == [
        "target_agent_id_exact",
        "delivery_destination_bound",
    ]
    assert resolution["selected_target"]["target_agent_id"] == "agent_target_test"
    assert resolution["route_preview"]["conversation_id"] == "channel_test_source"
    assert resolution["audit_ref"]["content_hash"].startswith("sha256:")


def test_resolver_rejects_ambiguous_agent_and_role_selector() -> None:
    envelope, capability = _load_valid_envelope_and_capability()
    envelope = copy.deepcopy(envelope)
    envelope["target"]["target_role"] = "reviewer"

    resolution = build_route_resolution(envelope, capability)

    assert resolution["decision"] == "rejected"
    assert "target_selector_ambiguous" in resolution["reason_codes"]


def test_resolver_rejects_adapter_surface_mismatch() -> None:
    envelope, capability = _load_valid_envelope_and_capability()
    capability = copy.deepcopy(capability)
    capability["surface"] = "slack"

    resolution = build_route_resolution(envelope, capability)

    assert resolution["decision"] == "rejected"
    assert "adapter_surface_mismatch" in resolution["reason_codes"]


def _load_valid_envelope_and_capability() -> tuple[dict, dict]:
    fixture_path = FIXTURES / "valid-visible-preview.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    envelope_fixture = json.loads(
        (fixture_path.parent / fixture["envelope_fixture"]).resolve().read_text(encoding="utf-8")
    )
    return envelope_fixture["envelope"], fixture["adapter_capability"]
