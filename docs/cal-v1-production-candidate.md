# CAL V1 production candidate

This document describes the unreleased 0.6.0 production-intent candidate. It
is a qualification subject, not a release authorization.

## Runtime identity

- Distribution: claim-audit-lab 0.6.0
- Profile: cal-v1-production-v1
- Semantic implementation authority:
  a902621e8baea3063dddd7f92ba975aade305464
- Contract B input authority: exact released 1.2.0
- Result schema: cal-v1-result-v1
- Packet schema: cal-v1-production-packet-v1

The candidate's canonical installed entry point is:

    claim-audit run PACKET.json --out-dir RUN_DIR

It also exposes claim-audit validate PACKET.json for intake-only checks and
claim-audit inspect --json for deterministic runtime identity. The existing
audit, demo, audit-bundle, calibrate, and explain commands remain
compatibility surfaces.

run executes one already typed packet through the qualified CAL semantic
implementation. It does not retrieve evidence, type propositions, invoke the
historical retrieve-to-entail engine, project Contract C, call Decision Engine
or Authorization, or perform an automatic action. A successful run emits a
native CAL result receipt; Contract C remains a separately versioned
Apparatus handoff layer.

## Explicit nonclaims

This candidate does not establish:

- universal semantic-family coverage;
- automatic claim typing;
- retrieval completeness;
- Contract B completeness;
- Contract C 2.0 release readiness;
- Decision Engine correctness;
- Authorization;
- automatic MainFrame mutation.

The frozen semantic envelope supports strict comparison and direct event order.
Other admitted families fail closed as UNSUPPORTED_SEMANTIC_FAMILY with a
terminal CAL result. The existing ten-case prototype smoke evidence remains
visible as a limitation: all ten natural claims were assertion_scope,
not_checkable, and UNSUPPORTED_SEMANTIC_FAMILY. That result is evidence for
the next semantic successor/evaluation programme, not a reason to broaden this
candidate.
