# ADR 0001: Select Bytewax for the Stream Forge topology worker

## Status

Accepted for Week 1 scaffold.

## Context

The R2 role owns the stream topology layer for Stream Forge. The Week 1 decision is whether to use Faust or Bytewax as the Python streaming framework.

## Options considered

### Faust

Pros:

- Familiar Kafka-streams style programming model.
- Good conceptual fit for agent-based stream processing.

Risks:

- More legacy maintenance concerns for a new portfolio project.
- Less attractive for a modern intern-quality engineering submission.

### Bytewax

Pros:

- Modern Python dataflow model.
- Clear fit for pipeline stages like consume, filter, map, window, and stateful recovery.
- Has Kafka connector support, which matches the project stack.
- Easier to explain as a topology graph during review.

Risks:

- Requires discipline around version pinning and connector testing.
- Some Kafka wiring should be smoke-tested with Docker before demo.

## Decision

Use Bytewax as the selected topology framework, while keeping the core business logic framework-independent in `topology.py`.

## Consequences

- Week 1 code is testable without Kafka.
- Week 2 can wire Kafka source and sink into the same processing functions.
- The design is professional because framework-specific code is isolated from validation and transformation logic.
