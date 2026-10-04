# Independent-judge candidate RC0

Research-only vertical for CAL #206. The preparation kit is the neighbouring directory and is not imported as this implementation.

`adapter.py` is the mechanical collect/synthesize transport. The semantic lanes are `kernel_lane.py`, `comparison_relation.py`, `constraint_guard.py`, and `event_order.py`. `worker.py` runs one lane as its own process. Toy weights in `POLICY.json` are not calibrated.

Bring-up on invented sentences:

```sh
python research/cal_v1_independent_judges_candidate_rc0_20261004/instrument_selfcheck.py
```

After the candidate commit is clean, the decisive commands are:

```sh
python research/cal_v1_independent_judges_rc0_20261004/contract_tests.py \
  --adapter research/cal_v1_independent_judges_candidate_rc0_20261004/adapter.py
python research/cal_v1_independent_judges_candidate_rc0_20261004/isolation_probe.py
python research/cal_v1_independent_judges_candidate_rc0_20261004/semantic_runner.py
```

Those runners refuse to overwrite `execution/isolation-01` or `execution/decisive-01`.
