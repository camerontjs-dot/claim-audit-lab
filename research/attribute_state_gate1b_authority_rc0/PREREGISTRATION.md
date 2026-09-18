# CAL Attribute State Gate-1B Authority RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

Parent: terminal Attribute-State Gate-1A RC1 head `08c198ee009f389b6386383c289494f2a44c2a9a`.
Selected measurement path: `conservative_state_hybrid`.

Question: can authority independently reconstruct the exact declared state atom and refuse any measured atom with altered entity, attribute, domain, value, or functional flag?

The candidate may not call Gate-1A measurement as source authority. It must independently parse the bounded direct and safe-extension surfaces, reconstruct exactly one `StateAtom`, then require exact equality with the measured atom.

Frozen mutation falsifiers cover entity, attribute, domain, value, and functional-state changes.

Acceptance requires all clean cases to warrant, every mutation to refuse, the weak trust-measurement authority to fail, deterministic replay, and no Gate-1A or production mutation.

Broad pressure testing remains deferred until every family is finalized.
