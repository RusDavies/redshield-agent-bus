# QA Plan

## Initial Verification

- Run `python3 scripts/verify_repo.py`.
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
- Declared delivery expectation and receipt-shape validation.
