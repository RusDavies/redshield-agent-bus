# Local Verifier Runbook

## Scope

The current open-core runtime is local verification only.

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
  "case_count": 16
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

## Dry-Run Adapters

Dry-run adapters may model delivery previews and receipts as data.

They must not:

- post messages;
- call live APIs;
- enqueue work;
- spawn agents;
- mutate external systems;
- claim production delivery occurred.

Promotion beyond local verification is controlled by
[`PROMOTION_GATE.md`](../operations/PROMOTION_GATE.md).
