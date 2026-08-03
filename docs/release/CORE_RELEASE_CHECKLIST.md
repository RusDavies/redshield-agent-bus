# Core Release Checklist

No public release is approved yet.

Before a public core release:

- [ ] License is selected and present.
- [ ] Contribution policy is present.
- [ ] Security policy and vulnerability intake path are present.
- [ ] Release security gate is present and satisfied.
- [ ] Public README explains stand-alone verifier value.
- [ ] Public product overview is current.
- [ ] Local verifier passes against public fixtures.
- [ ] Capability-grant proof adapter contract passes against public fixtures.
- [ ] Python tests pass in a documented environment.
- [ ] Release notes or changelog are present.
- [ ] Package metadata is accurate.
- [ ] Package provenance controls are present.
- [ ] Public release infrastructure controls are present.
- [ ] CI workflow passes for the release candidate.
- [ ] Release evidence record is complete for the candidate release.
- [ ] Public fixtures contain only fake ids and no private data.
- [ ] Keyper-style provider fixture stays behind the generic credential-provider
      contract and does not introduce a hard dependency.
- [ ] Core Warden and Armor baseline contract examples are present.
- [ ] Ecosystem contract examples pass the local schema verifier.
- [ ] Repo verification profile for core passes.
- [ ] Supply-chain and provenance expectations are documented.
- [ ] SBOM expectation and rollback path are documented.
- [ ] Branch protection or equivalent default-branch ruleset is verified.
- [ ] No customer-specific, deployment-specific, or launch-plan material is
      included in the public repo.

Production, hosted, managed, enterprise, or customer-facing deployment requires
separate gates and evidence. A public package release is not a production
authorization.
