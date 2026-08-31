# RC7D-D Cohort Apparatus Note

Before any evaluator was authored or any scientific execution occurred, the first held-out cohort commit `10443e795d55f0643ad5b23816a8881c63d01e75` was found to contain a terminal bookkeeping assertion inconsistent with its authored contents: 82 cases were present, not 84; 62 were mixed-semantic and 30 of those were flagged novel, below the preregistered >=50% novel-mixed requirement.

The case contents are preserved unchanged. The accepted cohort loader removes only the failing assertion statements from that frozen source and appends exactly two additional novel mixed `subclass + permission` cases authored before evaluator construction. This yields 84 total cases, 64 mixed cases, and 32 novel mixed cases. No reader or validator code is modified after any held-out case exists.

This is a pre-evaluation apparatus correction, not a scientific rerun or post-result corpus repair.