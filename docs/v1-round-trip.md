# CAL v1 Apparatus Round Trip

This engineering check builds Evidence Bundler's sealed synthetic C-A fixture into a
C-B bundle, explicitly opts that copy into CAL's `v1-retrieve-entail` pipeline, audits
it with pinned run metadata, and reloads the audited copy through both public loaders.

It does not modify the Evidence Bundler checkout. All generated artifacts land in a
temporary directory.

## Prerequisites

- Claim Audit Lab is the current directory and has a populated `.venv` with the `v1`
  dependencies.
- Evidence Bundler is available in a separate checkout with its own populated `.venv`.
- `EVIDENCE_BUNDLER_WORKBENCH` points to that checkout. The path can be anywhere.

```bash
export CAL_WORKBENCH="$PWD"
export EVIDENCE_BUNDLER_WORKBENCH="/path/to/evidence-bundler"
export ROUND_TRIP_DIR="${ROUND_TRIP_DIR:-$(mktemp -d)}"
export BUNDLE_DIR="$ROUND_TRIP_DIR/evidence-bundle-b16"
export AUDIT_OUT="$ROUND_TRIP_DIR/cal-output"
```

The placeholder Evidence Bundler path is intentional; do not copy a machine-specific
path into scripts or test configuration.

## 1. Build the C-B fixture bundle

```bash
"$EVIDENCE_BUNDLER_WORKBENCH/.venv/bin/python" -m evidence_bundler.cli \
  build-fixture-bundle \
  "$EVIDENCE_BUNDLER_WORKBENCH/tests/fixtures/scaffold-run-minimal" \
  --output "$BUNDLE_DIR"
```

## 2. Select v1 and reseal the bundle

Pipeline selection is part of the sealed C-B audit policy. Changing it requires three
linked updates: recompute `audit_config.config_hash`, copy that hash into
`bundle_manifest.audit_config_hash`, and reseal `SHA256SUMS` plus
`bundle.bundle_hash`.

```bash
"$CAL_WORKBENCH/.venv/bin/python" - "$BUNDLE_DIR" <<'PY'
from pathlib import Path
import sys

from claim_audit_lab.contracts.serialization import (
    hash_audit_config_file,
    load_yaml_mapping,
    reseal_bundle,
    yaml_to_string,
)

bundle_dir = Path(sys.argv[1]).resolve()
config_path = bundle_dir / "audit_config.yaml"
config = load_yaml_mapping(config_path)
config["pipeline"] = "v1-retrieve-entail"
config_path.write_text(yaml_to_string(config), encoding="utf-8")

config_hash = hash_audit_config_file(config_path)
config["config_hash"] = config_hash
config_path.write_text(yaml_to_string(config), encoding="utf-8")

manifest_path = bundle_dir / "bundle_manifest.yaml"
manifest = load_yaml_mapping(manifest_path)
manifest["audit_config_hash"] = config_hash
manifest_path.write_text(yaml_to_string(manifest), encoding="utf-8")

reseal_bundle(bundle_dir)
print(config_hash)
PY
```

## 3. Audit with pinned metadata

```bash
"$CAL_WORKBENCH/.venv/bin/claim-audit" audit-bundle "$BUNDLE_DIR" \
  --out-dir "$AUDIT_OUT" \
  --audit-run-id b16-round-trip \
  --audited-at 2026-06-29T00:00:00Z

export AUDITED_DIR="$AUDIT_OUT/$(basename "$BUNDLE_DIR")-audited"
```

The received/generated bundle remains untouched after this point; CAL writes and
reseals a separate audited copy.

## 4. Reload through both APIs

```bash
"$CAL_WORKBENCH/.venv/bin/python" - "$AUDITED_DIR" "$ROUND_TRIP_DIR" <<'PY'
from pathlib import Path
import sys

from claim_audit_lab.contracts.bundle_loader import load_bundle
from claim_audit_lab.v1 import load_audited

audited_dir = Path(sys.argv[1]).resolve()
scratch = Path(sys.argv[2]).resolve()

cb_bundle = load_bundle(audited_dir, deviations_dir=scratch / "cb-deviations")
v1_bundle = load_audited(audited_dir, deviations_dir=scratch / "v1-deviations")

claim = next(claim for claim in cb_bundle.claims if claim.claim_id == "clm-001")
trace = v1_bundle.traces["clm-001"]

assert claim.audit.audit_support_verdict == "supported"
assert trace.verdict.support_verdict == "supported"
assert trace.verdict.support_verdict_reason is None
assert trace.support_signal.label == "entail"

print("C-B verdict:", claim.audit.audit_support_verdict)
print("v1 verdict:", trace.verdict.support_verdict)
print("v1 reason sub-label:", trace.verdict.support_verdict_reason)
PY
```

`load_bundle` remains the fail-closed C-B loader. `load_audited` calls it first, then
strictly validates every `claims/*.audit-trace.json` as an `AuditTrace` and checks that
each trace binds to the matching extracted claim.

## Expected Result and Limitation

The Evidence Bundler fixture has no expected-outputs file. The B16 expectation is
therefore explicit rather than attributed to a nonexistent artifact: `clm-001` says
that accelerated approval applications should include 30-day accelerated stability
data, and its sole synthetic passage directly states the same proposition. The pinned
CAL v1 run deterministically produces C-B `supported`, v1 `supported`, no
`support_verdict_reason` sub-label, and an `entail` support signal. The integration test
locks those labels without pinning an incidental model score.

The source text explicitly says it is synthetic and not FDA guidance. This round trip
proves sealed-artifact handling, routing, deterministic writeback, and dual-loader
compatibility only. It does not validate retrieval quality, regulatory correctness,
research qualification, or fitness for regulated use.
