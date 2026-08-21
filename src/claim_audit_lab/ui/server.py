"""Standard library HTTP server for Claim Audit Lab Visual Workbench.

Zero external dependencies (pure Python http.server), reliable across all environments.
Serves the visual UI and REST APIs for live audits, bundle exploration, and benchmarks.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import yaml

from claim_audit_lab.ui.reasons import derive_reason
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
)
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit, run_default_explicit_claim_audit

# Repository workbench root, derived from this module's location.
# (Previously this also mutated sys.path on import; that is the caller's job --
# see scripts/launch_ui.py, which sets up its own path before importing this.)
workbench_dir = Path(__file__).resolve().parents[3]

# Offline flags. Set after the first-party imports, matching the original
# module order, so the audit runner sees them before any model is loaded.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

STATIC_DIR = Path(__file__).resolve().parent / "static"
PILOT_BUNDLES_DIR = (
    workbench_dir.parent.parent
    / "scaffold-claims-study"
    / "workbench"
    / "reproduce"
    / "build"
    / "pilot-001-v2-audit"
    / "bundles"
)
BENCHMARKS_DIR = workbench_dir.parent / "benchmarks"


class ClaimLabHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            index_file = STATIC_DIR / "index.html"
            if index_file.exists():
                content = index_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "index.html not found")
            return

        elif path == "/api/bundles":
            if not PILOT_BUNDLES_DIR.exists():
                self._send_json({"bundles": []})
                return
            bundles = []
            for bdir in sorted(PILOT_BUNDLES_DIR.iterdir()):
                if bdir.is_dir() and bdir.name.startswith("rsh-"):
                    claims_dir = bdir / "claims"
                    n_claims = len(list(claims_dir.glob("*.yaml"))) if claims_dir.exists() else 0
                    bundles.append(
                        {
                            "bundle_id": bdir.name,
                            "claim_count": n_claims,
                            "title": f"FDA CGMP Quality Systems Bundle ({bdir.name})",
                        }
                    )
            self._send_json({"bundles": bundles})
            return

        elif path.startswith("/api/bundle/"):
            bundle_id = path[len("/api/bundle/") :]
            bdir = PILOT_BUNDLES_DIR / bundle_id
            if not bdir.exists():
                self._send_json({"error": "Bundle not found"}, status=404)
                return

            claims_dir = bdir / "claims"
            claims = []
            if claims_dir.exists():
                for cfile in sorted(claims_dir.glob("*.yaml")):
                    with open(cfile) as fp:
                        cdata = yaml.safe_load(fp)
                    claims.append(
                        {
                            "claim_id": cdata["claim_id"],
                            "claim_text": cdata["claim_text"],
                            "passages": [
                                {
                                    "passage_id": p.get("passage_id", ""),
                                    "source_id": p.get("source_id", ""),
                                    "text": p.get("passage_text", ""),
                                    "section": p.get("section", ""),
                                }
                                for p in cdata.get("evidence_passages", [])
                            ],
                        }
                    )
            self._send_json({"bundle_id": bundle_id, "claims": claims})
            return

        elif path == "/api/benchmarks":
            clean_file = BENCHMARKS_DIR / "clean_canonical_reference.json"
            messy_file = BENCHMARKS_DIR / "realistic_prose_messy.json"
            clean_data = json.loads(clean_file.read_text()) if clean_file.exists() else {}
            messy_data = json.loads(messy_file.read_text()) if messy_file.exists() else {}
            self._send_json(
                {
                    "clean_canonical": clean_data,
                    "realistic_messy": messy_data,
                }
            )
            return

        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/audit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            req_data = json.loads(body.decode("utf-8"))

            claim_text = req_data.get("claim_text", "")
            raw_passages = req_data.get("passages", [])
            mode = req_data.get("mode", "auto")

            config = load_default_audit_config()
            passages = [
                Passage(passage_id=p.get("passage_id", f"p_{i}"), text=p.get("text", ""))
                for i, p in enumerate(raw_passages)
            ]

            # Whole-claim audit
            whole_trace = run_default_audit(
                AuditRequest(
                    claim_id="live-whole",
                    claim_text=claim_text,
                    passages=passages,
                    audit_config=config,
                )
            )
            whole_diag = derive_reason(whole_trace)
            whole_entailments = [
                {
                    "passage_id": e.passage_id,
                    "label": e.label,
                    "score": e.score,
                    "p_entail": e.p_entail,
                    "p_contradict": e.p_contradict,
                    "p_neutral": max(0.0, 1.0 - (e.p_entail or 0.0) - (e.p_contradict or 0.0)),
                }
                for e in whole_trace.entailment
            ]

            # Atomic decomposition
            lowered = claim_text.lower()
            is_coord = any(
                marker in lowered for marker in (" and ", " as well as ", ", including ")
            )
            if mode != "whole_only" and is_coord and len(claim_text) > 40:
                normalized = claim_text.replace(" as well as ", " and ").replace(
                    ", including ", " and "
                )
                raw_atoms = [p.strip() for p in normalized.split(" and ") if len(p.strip()) > 3]
                if len(raw_atoms) > 1:
                    atom_objs = [
                        ExplicitClaimAtom(
                            atom_id=f"atom-{i + 1}",
                            claim_text=text if text.endswith(".") else text + ".",
                            provenance=AtomProvenance(
                                origin="operator_declared",
                                reference_id="live-ui",
                                reference_sha256="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                            ),
                        )
                        for i, text in enumerate(raw_atoms)
                    ]
                    operator: Literal["single", "all_of"] = "all_of"
                else:
                    atom_objs = [
                        ExplicitClaimAtom(
                            atom_id="atom-1",
                            claim_text=claim_text,
                            provenance=AtomProvenance(
                                origin="operator_declared",
                                reference_id="live-ui",
                                reference_sha256="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                            ),
                        )
                    ]
                    operator = "single"
            else:
                atom_objs = [
                    ExplicitClaimAtom(
                        atom_id="atom-1",
                        claim_text=claim_text,
                        provenance=AtomProvenance(
                            origin="operator_declared",
                            reference_id="live-ui",
                            reference_sha256="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        ),
                    )
                ]
                operator = "single"

            explicit_trace = run_default_explicit_claim_audit(
                ExplicitClaimRequest(
                    parent_claim_id="live-parent",
                    parent_claim_text=claim_text,
                    operator=operator,
                    atoms=atom_objs,
                    passages=passages,
                    audit_config=config,
                )
            )
            atomic_diag = derive_reason(explicit_trace)

            atom_results = []
            for a in explicit_trace.atom_audits:
                atrace = a.audit_trace
                atom_results.append(
                    {
                        "atom_id": a.atom_id,
                        "claim_text": a.claim_text,
                        "verdict": atrace.verdict.support_verdict,
                        "entailments": [
                            {
                                "passage_id": e.passage_id,
                                "label": e.label,
                                "score": e.score,
                                "p_entail": e.p_entail,
                                "p_contradict": e.p_contradict,
                                "p_neutral": max(
                                    0.0,
                                    1.0 - (e.p_entail or 0.0) - (e.p_contradict or 0.0),
                                ),
                            }
                            for e in atrace.entailment
                        ],
                    }
                )

            resp = {
                "claim_text": claim_text,
                "mode": mode,
                "whole_claim": {
                    "verdict": whole_trace.verdict.support_verdict,
                    "diagnostics": whole_diag,
                    "entailments": whole_entailments,
                },
                "atomic": {
                    "verdict": explicit_trace.verdict.support_verdict,
                    "operator": explicit_trace.parent_aggregation.rule_id,
                    "diagnostics": atomic_diag,
                    "atoms": atom_results,
                },
            }
            self._send_json(resp)
        else:
            self.send_error(404, "Not Found")


def run_server(port: int = 8765) -> None:
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, ClaimLabHandler)
    print(f"🚀 Claim Audit Lab UI online at http://127.0.0.1:{port}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
