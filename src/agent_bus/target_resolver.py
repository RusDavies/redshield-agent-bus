"""Deterministic target resolution for local adapter dry-runs."""

from __future__ import annotations

from typing import Any

from .verifier import _canonical_hash


RESOLVER_ID = "local_deterministic_resolver_v1"


def build_route_resolution(
    envelope: dict[str, Any],
    adapter_capability: dict[str, Any],
) -> dict[str, Any]:
    """Build a local-only route resolution record for a bus envelope."""
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}
    source = envelope.get("source") if isinstance(envelope.get("source"), dict) else {}
    authz = envelope.get("authorization_context") if isinstance(envelope.get("authorization_context"), dict) else {}
    scope = authz.get("scope") if isinstance(authz.get("scope"), dict) else {}
    delivery = envelope.get("delivery_expectation") if isinstance(envelope.get("delivery_expectation"), dict) else {}

    reason_codes = _reason_codes(target, scope, delivery, adapter_capability)
    decision = "rejected" if any(code.endswith("_missing") or code.endswith("_ambiguous") or code.endswith("_mismatch") for code in reason_codes) else "resolved"

    selected_target = {
        "target_agent_id": target.get("target_agent_id"),
        "target_role": target.get("target_role"),
        "workspace_id": source.get("workspace_id") or scope.get("workspace_id"),
        "project_slug": source.get("project_slug") or scope.get("project_slug"),
        "allowed_runtime_ids": list(target.get("allowed_runtime_ids") or []),
    }
    route_preview = {
        "surface": delivery.get("target_surface"),
        "conversation_id": delivery.get("source_conversation_id"),
        "thread_id": delivery.get("thread_id"),
        "adapter_id": adapter_capability.get("adapter_id"),
        "adapter_type": adapter_capability.get("adapter_type"),
        "delivery_expectation_type": delivery.get("type"),
    }
    content_hash = _canonical_hash(
        {
            "message_id": envelope.get("message_id"),
            "correlation_id": envelope.get("correlation_id"),
            "selected_target": selected_target,
            "route_preview": route_preview,
            "decision": decision,
            "reason_codes": reason_codes,
        }
    )

    return {
        "schema_version": "targetresolution.v1",
        "resolver_id": RESOLVER_ID,
        "resolution_id": f"resolution_{envelope.get('message_id')}",
        "message_id": envelope.get("message_id"),
        "correlation_id": envelope.get("correlation_id"),
        "decision": decision,
        "reason_codes": reason_codes,
        "selected_target": selected_target,
        "route_preview": route_preview,
        "audit_ref": {
            "content_hash": content_hash,
            "privacy_classification": "internal",
        },
    }


def _reason_codes(
    target: dict[str, Any],
    scope: dict[str, Any],
    delivery: dict[str, Any],
    adapter_capability: dict[str, Any],
) -> list[str]:
    reason_codes: list[str] = []
    target_agent_id = target.get("target_agent_id")
    target_role = target.get("target_role")
    if target_agent_id and target_role:
        reason_codes.append("target_selector_ambiguous")
    elif target_agent_id:
        reason_codes.append("target_agent_id_exact")
    elif target_role:
        reason_codes.append("target_role_exact")
    else:
        reason_codes.append("target_selector_missing")

    allowed_agents = set(scope.get("target_agent_ids") or [])
    allowed_roles = set(scope.get("target_roles") or [])
    if target_agent_id and allowed_agents and target_agent_id not in allowed_agents:
        reason_codes.append("target_scope_mismatch")
    if target_role and allowed_roles and target_role not in allowed_roles:
        reason_codes.append("target_scope_mismatch")

    if not delivery.get("target_surface") or not delivery.get("source_conversation_id"):
        reason_codes.append("delivery_destination_missing")
    elif adapter_capability.get("surface") != delivery.get("target_surface"):
        reason_codes.append("adapter_surface_mismatch")
    else:
        reason_codes.append("delivery_destination_bound")

    return reason_codes
