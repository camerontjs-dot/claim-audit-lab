"""FastAPI / HTTP backend for Claim Audit Lab Visual Workbench & Interactive Inspector.

Provides REST APIs for:
1. Live interactive audits with DeBERTa NLI and atomic decomposition.
2. Exploring official real FDA evidence bundles (PILOT-001).
3. Browsing and evaluating dual benchmarks (Clean Canonical vs Realistic Messy).
4. Explainable abstention diagnosis and triage suggestions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from claim_audit_lab.ui.reasons import derive_reason
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
)
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit, run_default_explicit_claim_audit

# Offline flags. Set after the first-party imports, matching the original
# module order, so the audit runner sees them before any model is loaded.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

app = FastAPI(title="Claim Audit Lab Workbench", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Repository workbench root, derived from this module's location.
# (Previously this also mutated sys.path on import; that is the caller's job.)
workbench_dir = Path(__file__).resolve().parents[3]

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

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


# Request / Response Schemas
class PassageInput(BaseModel):
    passage_id: str
    text: str


class LiveAuditRequest(BaseModel):
    claim_text: str
    passages: list[PassageInput]
    mode: Literal["auto", "whole_only", "atomic_only"] = "auto"
    atoms: list[str] | None = None
    operator: Literal["single", "all_of"] = "all_of"


@app.post("/api/audit")
def audit_claim(req: LiveAuditRequest) -> dict[str, Any]:
    config = load_default_audit_config()
    passages = [Passage(passage_id=p.passage_id, text=p.text) for p in req.passages]

    # 1. Whole-Claim Audit
    whole_trace = run_default_audit(
        AuditRequest(
            claim_id="live-whole",
            claim_text=req.claim_text,
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

    # 2. Atomic Audit
    # Determine atoms
    if req.atoms and len(req.atoms) > 0:
        raw_atoms = req.atoms
    else:
        # Simple auto-split on conjunctions
        lowered = req.claim_text.lower()
        is_coord = any(marker in lowered for marker in (" and ", " as well as ", ", including "))
        if is_coord and len(req.claim_text) > 40:
            normalized = req.claim_text.replace(" as well as ", " and ").replace(
                ", including ", " and "
            )
            raw_atoms = [p.strip() for p in normalized.split(" and ")]
            raw_atoms = [p if p.endswith(".") else p + "." for p in raw_atoms if len(p) > 3]
        else:
            raw_atoms = [req.claim_text]

    atom_objs = [
        ExplicitClaimAtom(
            atom_id=f"atom-{i + 1}",
            claim_text=text,
            provenance=AtomProvenance(
                origin="operator_declared",
                reference_id="live-ui",
                reference_sha256="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            ),
        )
        for i, text in enumerate(raw_atoms)
    ]

    explicit_trace = run_default_explicit_claim_audit(
        ExplicitClaimRequest(
            parent_claim_id="live-parent",
            parent_claim_text=req.claim_text,
            operator="all_of" if len(atom_objs) > 1 else "single",
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
                        "p_neutral": max(0.0, 1.0 - (e.p_entail or 0.0) - (e.p_contradict or 0.0)),
                    }
                    for e in atrace.entailment
                ],
            }
        )

    return {
        "claim_text": req.claim_text,
        "mode": req.mode,
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


@app.get("/api/bundles")
def list_bundles() -> dict[str, Any]:
    if not PILOT_BUNDLES_DIR.exists():
        return {"bundles": []}
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
    return {"bundles": bundles}


@app.get("/api/bundle/{bundle_id}")
def get_bundle(bundle_id: str) -> dict[str, Any]:
    bdir = PILOT_BUNDLES_DIR / bundle_id
    if not bdir.exists():
        raise HTTPException(status_code=404, detail="Bundle not found")

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
    return {"bundle_id": bundle_id, "claims": claims}


@app.get("/api/benchmarks")
def get_benchmarks() -> dict[str, Any]:
    clean_file = BENCHMARKS_DIR / "clean_canonical_reference.json"
    messy_file = BENCHMARKS_DIR / "realistic_prose_messy.json"

    clean_data = json.loads(clean_file.read_text()) if clean_file.exists() else {}
    messy_data = json.loads(messy_file.read_text()) if messy_file.exists() else {}

    return {
        "clean_canonical": clean_data,
        "realistic_messy": messy_data,
    }


@app.get("/", response_class=HTMLResponse)
def get_index() -> HTMLResponse:
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    return HTMLResponse(
        content="<h1>Claim Audit Lab Workbench Initializing...</h1>", status_code=200
    )


# Mount static
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
