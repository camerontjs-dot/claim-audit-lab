# Contract C Unresolved-Evidence Information Sufficiency — Handoff

## Classification

Planning handoff only. No Contract C amendment, producer change, Decision Engine change, Contract E work, merge, release, tag, or promotion.

## Current supported state

Draft PR #98 established a bounded event-order path through common evidence-world binding, unchanged Contract C 1.0, and the maintained Decision Engine.

The remaining observed compression boundary is narrower:

- CAL can derive a warranted `UNRESOLVED` or `IRRELEVANT` temporal relation tied to an exact admitted passage;
- Contract C 1.0 contribution channels are only `support` and `counterevidence`;
- the bound projector therefore refuses to misclassify unresolved/irrelevant evidence and instead carries the terminal not-checkable state through a `state:` basis while recording omitted relation IDs only in the research projection receipt.

## Next question

Given only:

1. canonical released Contract C 1.0 bytes; and
2. the exact Contract B artifact/index to which those bytes are bound,

can an independent consumer reconstruct **which exact evidence reference caused a not-checkable unresolved/irrelevant result**, without producer-private state, CAL code, research sidecars, or knowledge of the opaque `state:` ID construction?

## Discriminator

Construct at least two exact upstream evidence worlds that:

- bind the same proposition semantics and same terminal reason category;
- each contain multiple admitted passages;
- differ only in which admitted passage produces the warranted unresolved/irrelevant relation;
- produce independently valid Contract C 1.0 objects using the frozen bound projector.

The independent consumer receives only Contract C + exact Contract B index/artifact.

The information-sufficiency hypothesis is weakened if the consumer can uniquely recover the causal evidence reference using only released contract semantics.

The gap hypothesis is strengthened if multiple Contract-B evidence references remain equally compatible with the Contract C terminal state and the causal passage can be recovered only from producer-private/research sidecar data.

## Important controls

- Do not let proposition text differ between worlds.
- Do not let the terminal branch/reported verdict differ between worlds.
- Keep Contract C producer policy fixed.
- Include at least one irrelevant/noncausal admitted passage in each world.
- Require exact released Contract C validation before consumer analysis.
- Consumer must not import CAL or the temporal projector.
- Consumer must treat opaque `state:` identifiers as opaque contract identifiers, not reverse-engineer producer-private hashing conventions.
- Preserve Contract B whole-world differences as immutable identity differences; the question is not whether the worlds are byte-identical, but whether Contract C tells the consumer which evidence inside its bound world caused the terminal state.

## Falsifier

If released Contract C semantics plus the bound Contract B are sufficient for an independent consumer to identify the exact unresolved/irrelevant causal passage without non-contract knowledge, no Contract C information-sufficiency gap is established by this case.

## Success interpretation

A failure to recover the exact causal passage establishes only a bounded information-sufficiency gap for unresolved/irrelevant evidence provenance. It does not itself select a schema fix. A later design comparison would still need to test alternatives such as a neutral contribution channel, a separate non-deciding evidence-role field, or another compact attribution representation.
