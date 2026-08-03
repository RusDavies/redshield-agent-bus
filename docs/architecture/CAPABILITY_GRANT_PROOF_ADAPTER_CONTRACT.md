# Capability Grant Proof Adapter Contract

This contract lets Agent Bus consume a public core capability-grant shape
without depending on a live issuer, private `rsk-ai-auth` history, or a hosted
RedshieldWorks service.

The current source schema is:

- `redshieldworks-core`:
  `schemas/core/agent-capability-grant.schema.json`
- schema version: `0.1.0`
- grant profile: `redshieldworks-agent-capability-grant.v0`

The older `rsk-ai-auth` name is provenance for the capability-grant idea. The
adapter contract is implemented against the public RedshieldWorks Core schema.

## Required Grant Properties

The local verifier expects a grant to carry:

- stable grant id, schema version, and grant profile;
- issuer, issue time, optional not-before time, and expiry;
- workload identity;
- delegation source and purpose;
- project scope;
- allowed secure-intake actions;
- source-class, sensitivity, content-access, and AI-processing limits;
- sender constraint;
- revocation status reference;
- audit correlation.

The verifier fails closed when the grant is expired, revoked, unsupported,
missing required binding fields, or attempts to authorize private/public,
external, or destructive behavior outside the explicit grant limits.

## Agent Bus Mapping

The adapter maps the grant into `authorization_context`:

- `authorization_id` comes from `grant_id`;
- `requester_id` comes from the authorizing actor, authorizing workflow, or
  delegation id;
- `basis.kind` is `capability_grant`;
- `basis.proof_issuer` comes from `issuer`;
- `basis.proof_ref` comes from the sender constraint id;
- `scope.project_slug` comes from the grant project id;
- secure-intake grant actions become Agent Bus action classes with the same
  names;
- `private_data` authorization is derived from the maximum sensitivity.

The proof adapter is a local schema contract only. It does not validate a
signature, call an issuer, query revocation infrastructure, or approve live
adapter behavior.

## Local Verification

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
