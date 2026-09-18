# CAL Event Occurrence Measurement Machinery RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

Parent: terminal event-occurrence Gate-0 head `245cf7481b4340fc17b80f7000d1663c2769e012`.
Typed-contract authority remains `eaef6c19dbe897e70af89b24d8599cfa05c335a1`.

## Question

What proposal machinery can recover direct event occurrence with actor/action/object/polarity bindings while refusing attribution, modality, deontic language, plans, order-only mentions, role reversal, and evidence-about-documentation?

Compare bounded event grammar, broad dependency extraction, and a conservative gated hybrid.

MUST_HANDLE covers direct positive/negative events, several actor/action/object bindings, and a simple explicit time binding.
DIAGNOSTIC covers passive voice, passive negation, open-vocabulary action, nominalized occurrence, and terse event-log syntax.
FAIL_CLOSED covers reporting/quotation, possibility, obligation, intention, event-order sentences, documentation statements, disjunction/conjunction, and state descriptions.

A path qualifies only with exact MUST_HANDLE output, zero unsafe FAIL_CLOSED claims, no wrong DIAGNOSTIC claims, exact replay/metamorphics, and no production `src/` changes.

A pass is measurement only. Independent source completion/warrant remains Gate-1B.
