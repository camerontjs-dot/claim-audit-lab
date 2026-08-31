# RC7B Failure Localization Results

Terminal localization state: **`INCONCLUSIVE_LOCALIZATION`**

## Cohorts

- both correct: 66
- agree but wrong: 58
- disagree: 56
- disagreement subtypes: `{'a_correct_b_wrong': 13, 'a_wrong_b_correct': 16, 'both_wrong': 27}`

## Surface-generalization penalty

- A construction error rate: 0.463
- A paraphrase error rate: 0.648
- A paraphrase penalty: 0.185
- B construction error rate: 0.241
- B paraphrase error rate: 0.426
- B paraphrase penalty: 0.185

## Agree-but-wrong concentration

- semantic failing-key top-3 coverage: 0.448
- semantic failing-key distinct count: 5
- affected families: ['only_permission', 'role_binding']
- residual families outside top-3 keys: ['only_permission', 'role_binding']

Greedy keys:
- `role_binding|predicate|(none)`: +12 unique agree-but-wrong cases
- `only_permission|only_population_may|necessary_permission_condition`: +8 unique agree-but-wrong cases
- `only_permission|membership|explicit_nonmembership_assertion`: +6 unique agree-but-wrong cases

## Mutation localization

- failed by either implementation: 11 / 30
- top-3 mutation-signature coverage: 1.000
- `quantifier|quantifier`: 6 failures
- `role_binding|object,subject`: 5 failures

## Highest-signal field × warrant keys

- `only_permission|entity|named_entity_reference`: occurrences=60, agree_wrong=16, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `only_permission|population|named_population_reference`: occurrences=60, agree_wrong=16, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `only_permission|predicate|permission_predicate_reference`: occurrences=60, agree_wrong=16, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `only_permission|only_population_may|necessary_permission_condition`: occurrences=56, agree_wrong=15, A_sem_err=24, B_sem_err=24, shared_sem_err=24, disagreements=0
- `role_binding|predicate|(none)`: occurrences=12, agree_wrong=12, A_sem_err=12, B_sem_err=12, shared_sem_err=12, disagreements=0
- `role_binding|object|(none)`: occurrences=12, agree_wrong=12, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `role_binding|polarity|(none)`: occurrences=12, agree_wrong=12, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `role_binding|subject|(none)`: occurrences=12, agree_wrong=12, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `role_binding|object|passive_role_binding`: occurrences=18, agree_wrong=9, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `role_binding|polarity|explicit_negation`: occurrences=9, agree_wrong=9, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `role_binding|predicate|event_predicate_reference`: occurrences=27, agree_wrong=9, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0
- `role_binding|subject|passive_role_binding`: occurrences=18, agree_wrong=9, A_sem_err=0, B_sem_err=0, shared_sem_err=0, disagreements=0

## Representative agree-but-wrong cases

- `RB7-OOD-05` [out_of_jurisdiction/out_of_jurisdiction]: If technicians inspect the vessel, reviewers may release batch a.
  - semantic failure keys: []
- `RB7-OOD-06` [out_of_jurisdiction/out_of_jurisdiction]: Every technician except Mira inspected the vessel.
  - semantic failure keys: []
- `RB7-OOD-07` [out_of_jurisdiction/out_of_jurisdiction]: Mira was an inspector before the cutoff.
  - semantic failure keys: []
- `RB7-OOD-08` [out_of_jurisdiction/out_of_jurisdiction]: Inspectors are a subclass of reviewers.
  - semantic failure keys: []
- `RB7-OOD-13` [out_of_jurisdiction/out_of_jurisdiction]: If technicians inspect the vessel, reviewers may release batch a.
  - semantic failure keys: []
- `RB7-OOD-14` [out_of_jurisdiction/out_of_jurisdiction]: Every technician except Mira inspected the vessel.
  - semantic failure keys: []
- `RB7-OOD-15` [out_of_jurisdiction/out_of_jurisdiction]: Mira was an inspector before the cutoff.
  - semantic failure keys: []
- `RB7-OOD-16` [out_of_jurisdiction/out_of_jurisdiction]: Inspectors are a subclass of reviewers.
  - semantic failure keys: []
- `RB7-OOD-21` [out_of_jurisdiction/out_of_jurisdiction]: If technicians inspect the vessel, reviewers may release batch a.
  - semantic failure keys: []
- `RB7-OOD-22` [out_of_jurisdiction/out_of_jurisdiction]: Every technician except Mira inspected the vessel.
  - semantic failure keys: []
- `RB7-OOD-23` [out_of_jurisdiction/out_of_jurisdiction]: Mira was an inspector before the cutoff.
  - semantic failure keys: []
- `RB7-OOD-24` [out_of_jurisdiction/out_of_jurisdiction]: Inspectors are a subclass of reviewers.
  - semantic failure keys: []

## Representative disagreement cases

- `RB7-OOD-03` [a_correct_b_wrong; out_of_jurisdiction/out_of_jurisdiction]: Seventy percent of technicians inspected the vessel.
- `RB7-OOD-11` [a_correct_b_wrong; out_of_jurisdiction/out_of_jurisdiction]: Seventy percent of technicians inspected the vessel.
- `RB7-OOD-19` [a_correct_b_wrong; out_of_jurisdiction/out_of_jurisdiction]: Seventy percent of technicians inspected the vessel.
- `RB7-OP-002` [a_wrong_b_correct; only_permission/construction]: Permission to release batch a is restricted to licensed inspectors. Noah belongs to the licensed inspectors. Noah does not have permission to release batch a.
- `RB7-OP-004` [both_wrong; only_permission/construction]: Anyone permitted to approve dossier must belong to the release officers. Tomas's non-membership in the release officers is confirmed. The record explicitly allows Tomas to approve dossier.
- `RB7-OP-008` [both_wrong; only_permission/construction]: Permission to unlock archive is restricted to certified reviewers. Noah's non-membership in the certified reviewers is confirmed. The record explicitly forbids Noah from unlock archive.
- `RB7-OP-010` [both_wrong; only_permission/construction]: Anyone permitted to sign certificate must belong to the licensed inspectors. Tomas belongs to the licensed inspectors. Tomas has permission to sign certificate.
- `RB7-OP-011` [both_wrong; only_permission/construction]: To be permitted to sign certificate, a person must belong to the release officers. The record excludes Lena from the release officers. Permission for Lena to sign certificate is denied.
- `RB7-OP-012` [both_wrong; only_permission/construction]: The release officers are a necessary class for permission to sign certificate. Omar's non-membership in the release officers is confirmed. Whether Omar is permitted to sign certificate is unknown.
- `RB7-OP-014` [a_wrong_b_correct; only_permission/construction]: Permission to release batch a is restricted to quality approvers. Noah belongs to the quality approvers. Noah does not have permission to release batch a.
- `RB7-OP-016` [both_wrong; only_permission/construction]: Anyone permitted to approve dossier must belong to the certified reviewers. Tomas's non-membership in the certified reviewers is confirmed. The record explicitly allows Tomas to approve dossier.
- `RB7-OP-020` [both_wrong; only_permission/paraphrase]: Permission to unlock archive is restricted to release officers. Noah's non-membership in the release officers is confirmed. The record explicitly forbids Noah from unlock archive.

## Interpretation boundary

This analysis localizes observed failures. It does not establish that adding rules will repair them, and it does not establish that language interpretation is intrinsically probabilistic.

No production authorization.
