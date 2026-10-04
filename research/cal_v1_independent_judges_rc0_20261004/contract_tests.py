"""Research apparatus for CAL #206. Self-test is NOT CAL qualification.

A candidate adapter exports collect(raw: bytes, lanes: list[dict]) -> list[dict]
and synthesize(raw: bytes, receipts: list[dict], policy: dict) -> dict.
The toy policy below tests mechanics, not calibrated semantic authority.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import io
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


RAW = canonical({"claim": "In 2025, Alpha had a higher rate than Beta.",
                 "evidence": [{"id": "p1", "text": "In 2025, Alpha had a higher rate than Beta."}]})


def receipt(pid: str, role: str = "relation", conclusion: str = "supports", **extra: Any) -> dict:
    return dict(process_id=pid, input_sha256=digest(RAW), execution="completed",
                applicability="applicable", role=role, conclusion=conclusion,
                warrant="qualified", material_loss=False, **extra)


def policy() -> dict:
    return {"profile": "toy-comparison", "minimum": "2", "lanes": {
        "a": {"role": "relation", "weight": "3", "group": "method-a", "required": False},
        "b": {"role": "relation", "weight": "1", "group": "method-b", "required": False},
        "scope": {"role": "guard", "weight": "0", "group": "scope", "required": True}}}


def rows() -> list[dict]:
    return [receipt("a"), receipt("b"), receipt("scope", "guard", "satisfied")]


class FixtureProbe:
    """Compliant toy transport/synthesis oracle, NOT a semantic implementation."""

    @staticmethod
    def collect(raw: bytes, lanes: list[dict]) -> list[dict]:
        found = []
        for lane in lanes:
            try:
                value = lane["call"](raw)
                found.append(json.loads(canonical(value)))
            except Exception as exc:
                value = receipt(lane["id"], lane["role"], "unresolved")
                value.update(input_sha256=digest(raw), execution="failed",
                             applicability="unknown", warrant="unqualified", error=type(exc).__name__)
                found.append(value)
        return sorted(found, key=lambda row: row["process_id"])

    @staticmethod
    def synthesize(raw: bytes, received: list[dict], config: dict) -> dict:
        spec = config["lanes"]
        ids = [r["process_id"] for r in received]
        if len(ids) != len(set(ids)) or set(ids) != set(spec):
            raise ValueError("incomplete or duplicate process set")
        minimum = Fraction(config["minimum"])
        if minimum <= 0:
            raise ValueError("invalid threshold")
        groups: dict[str, dict[str, Fraction]] = {}
        excluded: dict[str, str] = {}
        blockers: set[str] = set()
        for row in received:
            pid = row["process_id"]
            lane = spec[pid]
            if row["input_sha256"] != digest(raw) or row["role"] != lane["role"]:
                raise ValueError("foreign input or role")
            weight = Fraction(lane["weight"])
            if weight < 0:
                raise ValueError("negative weight")
            if row["execution"] not in {"completed", "failed"}:
                raise ValueError("execution vocabulary")
            if row["applicability"] not in {"applicable", "not_applicable", "unknown"}:
                raise ValueError("applicability vocabulary")
            if row["warrant"] not in {"qualified", "unqualified"} or type(row["material_loss"]) is not bool:
                raise ValueError("warrant or loss vocabulary")
            allowed = ({"supports", "refutes", "unresolved", "not_applicable"}
                       if lane["role"] == "relation" else
                       {"satisfied", "violated", "unresolved", "not_applicable"})
            if row["conclusion"] not in allowed:
                raise ValueError("local conclusion vocabulary")
            problem = None
            if row["execution"] == "failed":
                problem = "execution_failed"
            elif row["applicability"] == "unknown":
                problem = "unknown_applicability"
            elif row["applicability"] == "not_applicable":
                if row["conclusion"] != "not_applicable":
                    raise ValueError("not-applicable conclusion mismatch")
                problem = "not_applicable"
            elif row["warrant"] != "qualified":
                problem = "unqualified"
            elif row["material_loss"]:
                problem = "material_loss"
            elif row["conclusion"] == "unresolved":
                problem = "unresolved"
            if problem:
                excluded[pid] = problem
                if lane["required"] and problem != "not_applicable":
                    blockers.add("required_unknown")
                continue
            if lane["role"] == "guard":
                if row["conclusion"] == "violated" and lane["required"]:
                    blockers.add("guard_violation")
                excluded[pid] = "non_voting_guard"
                continue
            if row["conclusion"] not in {"supports", "refutes"}:
                raise ValueError("incoherent relation")
            if weight == 0:
                excluded[pid] = "zero_relevance"
                continue
            group = groups.setdefault(lane["group"], {})
            direction = row["conclusion"]
            group[direction] = max(group.get(direction, Fraction(0)), weight)
        scores = {k: sum((g.get(k, Fraction(0)) for g in groups.values()), Fraction(0))
                  for k in ("supports", "refutes")}
        if scores["supports"] and scores["refutes"]:
            blockers.add("material_conflict")
        outcome = "not_checkable"
        if not blockers:
            if scores["supports"] >= minimum:
                outcome = "supported"
            elif scores["refutes"] >= minimum:
                outcome = "contradicted"
        return {"conclusion": outcome, "scores": {k: str(v) for k, v in scores.items()},
                "blockers": sorted(blockers), "exclusions": excluded,
                "receipts": sorted(copy.deepcopy(received), key=lambda r: r["process_id"]),
                "policy_sha256": digest(canonical(config)), "input_sha256": digest(raw)}


ADAPTER: Any = FixtureProbe


class Contract(unittest.TestCase):
    def synth(self, data=None, config=None):
        return ADAPTER.synthesize(RAW, rows() if data is None else data, policy() if config is None else config)

    def dispatch(self, raw=RAW, failure=False):
        calls = []
        lanes = []
        for pid in ("a", "b", "scope"):
            def call(value, pid=pid):
                calls.append((pid, value))
                if failure and pid == "a":
                    raise RuntimeError("fixture failure")
                return receipt(pid, "guard" if pid == "scope" else "relation",
                               "satisfied" if pid == "scope" else "supports")
            lanes.append({"id": pid, "role": "guard" if pid == "scope" else "relation", "call": call})
        return ADAPTER.collect(raw, lanes), calls

    def test_all_lanes_run(self):
        result, calls = self.dispatch()
        self.assertEqual({p for p, _ in calls}, {"a", "b", "scope"})
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(result), 3)

    def test_original_bytes(self):
        _, calls = self.dispatch()
        for _, value in calls:
            self.assertIsInstance(value, bytes)
            self.assertEqual(value, RAW)

    def test_unsupported_claim_not_global_gate(self):
        raw = canonical({"claim": "An unfamiliar scoped claim.", "evidence": []})
        _, calls = self.dispatch(raw)
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(value == raw for _, value in calls))

    def test_failure_isolated(self):
        result, calls = self.dispatch(failure=True)
        self.assertEqual(len(calls), 3)
        self.assertEqual({r["process_id"] for r in result}, {"a", "b", "scope"})
        self.assertEqual(next(r for r in result if r["process_id"] == "a")["execution"], "failed")

    def test_receipts_snapshot(self):
        shared = receipt("a")
        def later(raw):
            shared["conclusion"] = "refutes"
            return receipt("b")
        out = ADAPTER.collect(RAW, [{"id": "a", "role": "relation", "call": lambda raw: shared},
                                    {"id": "b", "role": "relation", "call": later}])
        self.assertEqual(next(r for r in out if r["process_id"] == "a")["conclusion"], "supports")

    def test_positive(self):
        self.assertEqual(self.synth()["conclusion"], "supported")

    def test_negative(self):
        data = rows()
        data[0]["conclusion"] = data[1]["conclusion"] = "refutes"
        self.assertEqual(self.synth(data)["conclusion"], "contradicted")

    def test_late_conflict_not_majority(self):
        data = rows()
        data[1]["conclusion"] = "refutes"
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")
        self.assertIn("material_conflict", self.synth(data)["blockers"])

    def test_guard_blocks(self):
        data = rows()
        data[2]["conclusion"] = "violated"
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")

    def test_required_unknown_blocks(self):
        data = rows()
        data[2]["applicability"] = "unknown"
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")

    def test_optional_unknown_not_veto(self):
        data = rows()
        data[1].update(applicability="unknown", conclusion="unresolved")
        self.assertEqual(self.synth(data)["conclusion"], "supported")

    def test_failed_not_not_applicable(self):
        data = rows()
        data[2]["execution"] = "failed"
        result = self.synth(data)
        self.assertEqual(result["conclusion"], "not_checkable")
        self.assertEqual(result["exclusions"]["scope"], "execution_failed")

    def test_unqualified_excluded(self):
        data = rows()
        data[0]["warrant"] = "unqualified"
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")

    def test_loss_excluded(self):
        data = rows()
        data[0]["material_loss"] = True
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")

    def test_optional_loss_not_global_veto(self):
        data = rows()
        data[1]["material_loss"] = True
        self.assertEqual(self.synth(data)["conclusion"], "supported")

    def test_irrelevant_not_dilution(self):
        data, config = rows(), policy()
        for i in range(30):
            pid = f"irrelevant-{i}"
            data.append(receipt(pid, conclusion="not_applicable"))
            data[-1]["applicability"] = "not_applicable"
            config["lanes"][pid] = {"role": "relation", "weight": "100", "group": pid, "required": False}
        self.assertEqual(self.synth(data, config)["scores"], self.synth()["scores"])

    def test_clone_invariant(self):
        data, config = rows(), policy()
        data.append(receipt("a-copy"))
        config["lanes"]["a-copy"] = dict(config["lanes"]["a"])
        self.assertEqual(self.synth(data, config)["scores"], self.synth()["scores"])

    def test_claim_type_weight_changes(self):
        data, config = rows(), policy()
        data[1]["warrant"] = "unqualified"
        before = self.synth(data, config)
        config["profile"] = "toy-other-type"
        config["lanes"]["a"]["weight"] = "1"
        after = self.synth(data, config)
        self.assertEqual(before["conclusion"], "supported")
        self.assertEqual(after["conclusion"], "not_checkable")
        self.assertNotEqual(before["policy_sha256"], after["policy_sha256"])
        self.assertEqual(before["receipts"], after["receipts"])

    def test_self_weight_ignored(self):
        data = rows()
        data[0]["warrant"] = "unqualified"
        data[1]["claimed_weight"] = "1000"
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")

    def test_zero_relevance_no_vote(self):
        data, config = rows(), policy()
        data[1]["conclusion"] = "refutes"
        config["lanes"]["b"]["weight"] = "0"
        self.assertEqual(self.synth(data, config)["conclusion"], "supported")

    def test_all_abstain_not_success(self):
        data = rows()
        for row in data:
            row["applicability"] = row["conclusion"] = "not_applicable"
        self.assertEqual(self.synth(data)["conclusion"], "not_checkable")

    def test_missing_receipt_rejected(self):
        with self.assertRaises(ValueError): self.synth(rows()[:-1])

    def test_duplicate_receipt_rejected(self):
        with self.assertRaises(ValueError): self.synth(rows() + [rows()[0]])

    def test_foreign_receipt_rejected(self):
        data = rows()
        data[0]["input_sha256"] = "0" * 64
        with self.assertRaises(ValueError): self.synth(data)

    def test_role_substitution_rejected(self):
        data = rows()
        data[2]["role"] = "relation"
        with self.assertRaises(ValueError): self.synth(data)

    def test_negative_weight_rejected(self):
        config = policy()
        config["lanes"]["a"]["weight"] = "-1"
        with self.assertRaises(ValueError): self.synth(config=config)

    def test_invalid_applicability_rejected(self):
        data = rows()
        data[0]["applicability"] = "not_run"
        with self.assertRaises(ValueError): self.synth(data)

    def test_incoherent_not_applicable_rejected(self):
        data = rows()
        data[0]["applicability"] = "not_applicable"
        with self.assertRaises(ValueError): self.synth(data)

    def test_order_and_replay(self):
        one, two = self.synth(), self.synth(list(reversed(rows())))
        self.assertEqual(canonical(one), canonical(two))
        self.assertEqual(canonical(one), canonical(self.synth()))

    def test_inputs_not_mutated_and_receipts_retained(self):
        data, config = rows(), policy()
        saved = canonical([data, config])
        output = self.synth(data, config)
        self.assertEqual(saved, canonical([data, config]))
        self.assertEqual(output["receipts"], sorted(data, key=lambda r: r["process_id"]))
        self.assertEqual(output["policy_sha256"], digest(canonical(config)))


class EarlyRouter(FixtureProbe):
    @staticmethod
    def collect(raw, lanes): return FixtureProbe.collect(raw, lanes[:1])


class LossyFanout(FixtureProbe):
    @staticmethod
    def collect(raw, lanes): return FixtureProbe.collect(b'{"claim":"Alpha > Beta"}', lanes)


class SuppressFailure(FixtureProbe):
    @staticmethod
    def collect(raw, lanes): return [r for r in FixtureProbe.collect(raw, lanes) if r["execution"] != "failed"]


class Majority(FixtureProbe):
    @staticmethod
    def synthesize(raw, received, config):
        out = FixtureProbe.synthesize(raw, received, config)
        if "material_conflict" in out["blockers"]: out["conclusion"] = "supported"
        return out


class IgnoreGuard(FixtureProbe):
    @staticmethod
    def synthesize(raw, received, config):
        changed = copy.deepcopy(received)
        for row in changed:
            if row["role"] == "guard": row["conclusion"] = "satisfied"
        return FixtureProbe.synthesize(raw, changed, config)


class CloneBoost(FixtureProbe):
    @staticmethod
    def synthesize(raw, received, config):
        changed = copy.deepcopy(config)
        for pid in changed["lanes"]: changed["lanes"][pid]["group"] = pid
        return FixtureProbe.synthesize(raw, received, changed)


class AlwaysAbstain(FixtureProbe):
    @staticmethod
    def synthesize(raw, received, config):
        out = FixtureProbe.synthesize(raw, received, config)
        out["conclusion"] = "not_checkable"
        return out


def check(adapter) -> dict:
    global ADAPTER
    ADAPTER = adapter
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Contract))
    return {"tests": result.testsRun, "failures": [t._testMethodName for t, _ in result.failures],
            "errors": [t._testMethodName for t, _ in result.errors], "skips": len(result.skipped)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--selftest", action="store_true")
    mode.add_argument("--adapter", type=Path)
    args = parser.parse_args()
    if args.selftest:
        good = check(FixtureProbe)
        kills = {}
        for mutant, target in ((EarlyRouter, "test_all_lanes_run"),
                               (LossyFanout, "test_original_bytes"),
                               (SuppressFailure, "test_failure_isolated"),
                               (Majority, "test_late_conflict_not_majority"),
                               (IgnoreGuard, "test_guard_blocks"),
                               (CloneBoost, "test_clone_invariant"),
                               (AlwaysAbstain, "test_positive")):
            run = check(mutant)
            kills[mutant.__name__] = {"intended_test": target, "caught": target in run["failures"], "result": run}
        ok = not good["failures"] and not good["errors"] and all(k["caught"] for k in kills.values())
        report = {"evidence_class": "APPARATUS_SELFTEST_ONLY", "probe": good, "weak_controls": kills,
                  "candidate_executed": False, "passed": ok}
    else:
        spec = importlib.util.spec_from_file_location("candidate_adapter", args.adapter.resolve())
        if spec is None or spec.loader is None: raise RuntimeError("adapter cannot be loaded")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        run = check(module)
        ok = not run["failures"] and not run["errors"] and not run["skips"]
        report = {"evidence_class": "CANDIDATE_MECHANICAL_CONFORMANCE_ONLY", "result": run,
                  "adapter_sha256": digest(args.adapter.read_bytes()), "passed": ok,
                  "semantic_utility": "NOT_TESTED", "v1_readiness": "NOT_ESTABLISHED"}
    print(json.dumps(report, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
