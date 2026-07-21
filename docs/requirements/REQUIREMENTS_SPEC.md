# Requirements Spec

## Functional Requirements

- Capture source surface, channel, message id, sender, timestamp, and requested action for each bus message.
- Support initial interaction types: `notify`, `ask`, `instruct`, `delegate`, `handoff`, `consult`, `escalate`, `broadcast`, and `subscribe`.
- Declare the intended response surface: visible chat message, private final, project file, or ops channel.
- Preserve explicit human approvals and distinguish them from inferred context.
- Support bounded delegation with a clear owner, status, and completion/blocker summary.
- Provide a recovery path for stuck, timed-out, privately answered, or misrouted work.

The first buildable requirements slice is defined in `docs/requirements/INITIAL_AGENT_BUS_SLICE.md`. It covers one-source to one-target typed bus messages, the minimum envelope, validation rules, state model, delivery expectations, and prototype acceptance criteria.

## Non-Functional Requirements

- Bus messages must be auditable without exposing secrets or private memory.
- Duplicate delivery must be detectable or harmless.
- Failed delivery must be visible to the appropriate operator or source conversation.
- The system must be testable locally before touching live agent routing.

## Security And Privacy Requirements

- Authenticate message origin before acting on instructions.
- Validate target surface/project mapping before project operations.
- Prevent runtime-event continuation phrases from causing project side effects in shared/project channels.
- Do not route private memory into shared chats unless clearly appropriate and safe.
- Require explicit approval for external/public actions.

## Acceptance Criteria For First Slice

- A documented bus-message envelope exists.
- A prototype or verifier can reject missing provenance, ambiguous target, and unsafe external-action requests.
- Tests cover wrong-destination delivery, replay/duplicate detection, and private-content exclusion.
- The first prototype does not require live chat posting, external network access, or production runtime routing.
