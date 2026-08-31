# RC7D cohort apparatus note

The held-out cohort commit `4a5148bce7d861815a08fcdf8623a7e9e28fa367` contains 74 cases but its final self-check mistakenly asserts 86.

This was detected **before evaluation**. The case list, source strings, gold semantic dimensions, atoms, group assignments, and composition expectations are unchanged.

The evaluator is authorized to materialize that exact cohort file and replace only the terminal source-text assertion:

`assert len(CASES) == 86, len(CASES)`

with

`assert len(CASES) == 74, len(CASES)`

in memory before executing the module.

This is a non-semantic apparatus repair. The original defective cohort commit remains preserved. Any other change to the cohort bytes is not authorized for this run.
