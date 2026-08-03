# Local Verifier Runbook

## Scope

The current core runtime is local verification only.

It reads static fixtures, validates bus-message envelopes and state
transitions, and prints deterministic results. It must not perform live
delivery, external actions, runtime calls, agent spawning, queue publishing, or
tool dispatch.

## Verify Fixtures

Run:

```sh
python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 21
}
```

If verification fails:

- read the failing `case_id`;
- inspect `errors`;
- compare `expected_errors` against the fixture;
- fix either the fixture expectation or verifier behavior;
- rerun the command.

## Fixture Rules

Fixtures must use fake stable ids such as:

- `agent_source_test`;
- `agent_target_test`;
- `runtime_local_test`;
- `workspace_redshield_test`;
- `project_agent_bus_test`;
- `channel_test_source`;
- `credential_local_test`;
- `requester_test_user`.

Fixtures must not include:

- secrets or tokens;
- private messages;
- copied private memory;
- real credential ids;
- production runtime ids;
- live channel ids;
- customer data.

## Credential Provider Contract

Run:

```sh
python3 -m pytest tests/test_credential_provider_contract.py
```

The credential-provider contract accepts the local runtime-token fixture and a
Keyper-style SSH certificate evidence fixture through the same generic provider
response shape. It rejects unavailable, expired, revoked, mismatched,
missing-proof, and missing-evidence provider responses.

The Keyper spike fixture references public Keyper issuer evidence concepts. It
does not import Keyper code, call Keyper, manage SSH keys, or require Keyper as
a dependency.

## Dry-Run Adapters

Dry-run adapters may model delivery previews and receipts as data.

Run:

```sh
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 6
}
```

They must not:

- post messages;
- call live APIs;
- enqueue work;
- spawn agents;
- mutate external systems;
- claim production delivery occurred.

Promotion beyond local verification is controlled by
[`PROMOTION_GATE.md`](../operations/PROMOTION_GATE.md).
Agent action classes and live-use boundaries are defined in
[`AGENT_OPERATION_BOUNDARIES.md`](../operations/AGENT_OPERATION_BOUNDARIES.md).

## Warden Policy Contract

Run:

```sh
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 6
}
```

The Warden contract validates baseline `allow`, `deny`, and
`require_review` policy results. It checks that a policy result binds to the
original request, carries reason/evidence references, requires approvers for
review decisions, and does not embed private evidence.

## Armor Enforcement Contract

Run:

```sh
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 7
}
```

The Armor contract validates baseline `allow`, `block`, `sanitize`,
and `require_review` enforcement results. It checks that an enforcement result
binds to the original request, names finding/evidence references, requires
sanitized field references for sanitize decisions, and does not embed private
evidence.

## Capability Grant Proof Adapter Contract

Run:

```sh
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 3
}
```

The capability-grant proof adapter contract validates the public
RedshieldWorks Core `agent-capability-grant` shape and its mapping into Agent
Bus `authorization_context`. It fails closed for expired grants and for
authorization contexts that widen grant actions.

## Ecosystem Contract Examples

Run:

```sh
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
```

Expected result:

```json
{
  "ok": true,
  "case_count": 4
}
```

The ecosystem contract verifier checks the S5 public example fixtures for
RSK AI Auth-style capability grants, Keyper-style credential evidence, Warden
policy results, and Armor enforcement results. It keeps those as local schema
contracts only; it does not call or require the neighboring systems.
