# QA Plan

## Initial Verification

- Run `python3 scripts/verify_repo.py`.
- Run `python3 scripts/agent_bus_verify.py verify tests/fixtures/agent_bus --pretty`.
- Run `python3 scripts/agent_bus_verify.py dry-run tests/fixtures/adapter_dry_runs --pretty`.
- Run `python3 scripts/agent_bus_verify.py warden-policy tests/fixtures/warden_policy --pretty`.
- Run `python3 -m pytest`.
- Validate required package, fixture, test, and public documentation paths
  exist.
- Validate fixture data uses fake ids and contains no secrets, live provider
  ids, private messages, or production runtime ids.

## Future Test Areas

- Bus-message envelope schema validation.
- Wrong-destination rejection.
- Duplicate/replay handling.
- Missing approval rejection for external actions.
- Private-data exclusion.
- Runtime-event boundary handling.
- Adapter capability variants for each supported delivery expectation.
- Armor baseline contract validation in the integrated verifier.
