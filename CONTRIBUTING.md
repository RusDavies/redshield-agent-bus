# Contributing To Redshield Agent Bus

Redshield Agent Bus is currently pre-release. Contributions are welcome once
they preserve the open-core boundary and the local-first safety model.

## Ground Rules

- Keep the open core downstream-agnostic. Do not add product, customer,
  commercial, management, or launch-plan assumptions to this repository.
- Keep verifier behavior deterministic and local. Tests must not require live
  credentials, live chat surfaces, agent runtimes, network services, or
  production infrastructure.
- Use fake fixture data only. Do not commit real secrets, tokens, private
  messages, production runtime ids, customer data, or live channel ids.
- Fail closed for missing identity, authorization, freshness, idempotency,
  delivery, Warden, Armor, or credential-provider evidence.
- Document new protocol behavior before relying on it in fixtures or tests.

## Development

Install test dependencies in an isolated environment, then run:

```sh
python3 -m pip install -e '.[test]'
python3 -m pytest
```

Before opening a change, also run the local verifier checks that apply to the
files you touched. The full open-core verification set is:

```sh
python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty
python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty
python3 scripts/agent_bus_verify.py capability-grant tests/fixtures/capability_grants --pretty
python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty
python3 scripts/agent_bus_verify.py armor-enforcement tests/fixtures/armor_enforcement --pretty
python3 scripts/agent_bus_verify.py ecosystem-contract tests/fixtures/agent_bus/ecosystem --pretty
python3 scripts/verify_repo.py open-core
```

## Change Review Expectations

Protocol, security, release, and fixture changes should explain:

- what new behavior or boundary is being introduced;
- which existing safety control is affected;
- which tests or fixtures prove the behavior;
- what remains out of scope.

Changes that enable live posting, live agent spawning, external actions,
production runtime calls, public package release, or customer-facing security
claims require explicit human approval recorded outside this public-target
repository before implementation.

