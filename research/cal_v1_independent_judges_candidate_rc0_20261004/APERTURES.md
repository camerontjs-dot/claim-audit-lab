# Judge information apertures

Each decisive lane is a one-shot subprocess. Its stdin is the envelope bytes for that arm and nothing else. The parent writes the next lane only after the previous stdout has been parsed and stored. Lane order is a schedule, not an information channel.

A lane may read:

- those stdin bytes;
- its own Python module and the frozen `claim_audit_lab` package when the lane is the kernel;
- the Python standard library and the already-installed runtime dependencies required to import that package.

A lane may not read:

- another lane's stdout, interpretation, or conclusion;
- `EXPECTATIONS.json`, `SEMANTIC_CASES.json`, or `POLICY.json`;
- the network, a model cache, or any evidence world other than the supplied passages.

Claim interpretation is a pure function of the claim string. Evidence interpretation is a pure function of each passage string. The comparison happens after both interpretations exist. Evidence text is not passed into the claim parser.

The kernel lane calls the frozen authoring function on the exact claim string. If authoring refuses, the lane seals `not_applicable` and does not invent a typed target by deleting scope. The kernel then runs only for a claim the frozen grammar actually accepts. Its measurement and warrant functions are the packaged ones. This candidate does not edit them.

Full raw source files are not in the envelope. The aperture record says the passage bundle is the available world, not a complete source archive. Truncation inside a lane is a failure. The lossy arm's rewrite happens in the parent before dispatch and is labeled on the arm, not hidden inside a lane.

`RC0_TRACE_OPEN=1` classifies files opened by a worker. The decisive runner turns that trace on. A worker that opens the expectation file or the seed file fails the run. Probe-only environment marks are not set on the decisive run.
