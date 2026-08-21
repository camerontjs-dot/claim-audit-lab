// GENERATED FILE — do not edit by hand.
// Produced by scripts/gen_docs_traces.py from sealed CAL receipts in
// outputs/2026-08-02-chunk-granularity-probe/ and .../qms-claim-generation/.
// payload sha256[:16] = 718a2ec186f436b7
window.CAL_TRACES = {
  "summary": {
    "n": 12,
    "floorTotal": 2,
    "floorRescued": 2,
    "entailTotal": 10,
    "entailRescued": 0,
    "meanNeutralFine": 0.9976,
    "meanNeutralSection": 0.9963,
    "fineTopMin": 0.473,
    "fineTopMax": 0.783,
    "retrievalFloor": 0.4,
    "supportedThreshold": 0.7,
    "generated": "2026-08-19"
  },
  "cases": [
    {
      "id": "SOP-FAC-060_v2.0::states::00",
      "doc": "SOP-FAC-060",
      "rel": "states",
      "claim": "The Technical Operations Director holds explicit authority to approve technical methods for directive MATRIX-0060 within the Department of Autoclave Steam Sterilization.",
      "basis": "Section 3 explicitly states that the Technical Operations Director approves technical methods for MATRIX-0060 in that department.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-FAC-060_v2.0#s03",
            "score": 0.70199
          },
          {
            "pid": "SOP-FAC-060_v2.0#s02",
            "score": 0.591053
          },
          {
            "pid": "SOP-FAC-060_v2.0#s06",
            "score": 0.49153
          },
          {
            "pid": "SOP-FAC-060_v2.0#s01",
            "score": 0.461794
          },
          {
            "pid": "SOP-FAC-060_v2.0#s04",
            "score": 0.411736
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-FAC-060_v2.0#s03u00",
            "score": 0.782792
          },
          {
            "pid": "SOP-FAC-060_v2.0#s02u00",
            "score": 0.582997
          },
          {
            "pid": "SOP-FAC-060_v2.0#s06u01",
            "score": 0.513516
          },
          {
            "pid": "SOP-FAC-060_v2.0#s01u00",
            "score": 0.48669
          },
          {
            "pid": "SOP-FAC-060_v2.0#s04u00",
            "score": 0.430911
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-MFG-017_v1.0::states::00",
      "doc": "SOP-MFG-017",
      "rel": "states",
      "claim": "During flow velocity balancing execution, the Manufacturing Lead is tasked with inspecting Cleanroom Suite 117-B and verifying calibration tags on unit MFG-SYS-1017.",
      "basis": "Section 3 explicitly states that the Manufacturing Lead inspects Cleanroom Suite 117-B and verifies calibration tags on MFG-SYS-1017.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-017_v1.0#s04",
            "score": 0.549805
          },
          {
            "pid": "SOP-MFG-017_v1.0#s03",
            "score": 0.541302
          },
          {
            "pid": "SOP-MFG-017_v1.0#s02",
            "score": 0.504084
          },
          {
            "pid": "SOP-MFG-017_v1.0#s01",
            "score": 0.416167
          },
          {
            "pid": "SOP-MFG-017_v1.0#s05",
            "score": 0.379527
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-017_v1.0#s03u01",
            "score": 0.715809
          },
          {
            "pid": "SOP-MFG-017_v1.0#s04u00",
            "score": 0.542613
          },
          {
            "pid": "SOP-MFG-017_v1.0#s01u02",
            "score": 0.527661
          },
          {
            "pid": "SOP-MFG-017_v1.0#s04u01",
            "score": 0.483694
          },
          {
            "pid": "SOP-MFG-017_v1.0#s02u00",
            "score": 0.458943
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.994140625,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-MFG-059_v1.0::entails::01",
      "doc": "SOP-MFG-059",
      "rel": "entails",
      "claim": "A batch of Kappa-Elixir 100mL Pediatric Oral Liquid exhibiting a dissolved oxygen level below forty percent cannot pass final quality containment verification.",
      "basis": "The document mandates DO >= 40% and states that any excursion beyond this limit triggers mandatory quality containment and immediate QA hold.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-059_v1.0#s05",
            "score": 0.632012
          },
          {
            "pid": "SOP-MFG-059_v1.0#s03",
            "score": 0.569206
          },
          {
            "pid": "SOP-MFG-059_v1.0#s04",
            "score": 0.512723
          },
          {
            "pid": "SOP-MFG-059_v1.0#s02",
            "score": 0.484859
          },
          {
            "pid": "SOP-MFG-059_v1.0#s01",
            "score": 0.219551
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.98974609375,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-059_v1.0#s04u02",
            "score": 0.76669
          },
          {
            "pid": "SOP-MFG-059_v1.0#s02u01",
            "score": 0.749651
          },
          {
            "pid": "SOP-MFG-059_v1.0#s03u02",
            "score": 0.714945
          },
          {
            "pid": "SOP-MFG-059_v1.0#s05u00",
            "score": 0.623858
          },
          {
            "pid": "SOP-MFG-059_v1.0#s06u00",
            "score": 0.262918
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99560546875,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-MFG-102_v1.0::entails::01",
      "doc": "SOP-MFG-102",
      "rel": "entails",
      "claim": "Any detected excursion outside the 2.0\u00b0C to 8.0\u00b0C range during continuous telemetry monitoring automatically results in a Quality Hold.",
      "basis": "Combining continuous telemetry monitoring requirements (Section 2) with out-of-spec escalation rules (Section 4.5) logically necessitates a Quality Hold.",
      "missKind": "no_evidence",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-102_v1.0#s00",
            "score": 0.384976
          },
          {
            "pid": "SOP-MFG-102_v1.0#s04",
            "score": 0.372721
          },
          {
            "pid": "SOP-MFG-102_v1.0#s05",
            "score": 0.328249
          },
          {
            "pid": "SOP-MFG-102_v1.0#s01",
            "score": 0.320631
          },
          {
            "pid": "SOP-MFG-102_v1.0#s03",
            "score": 0.278444
          }
        ],
        "rules": [
          "A2_retrieval_empty"
        ],
        "verdict": "not_checkable",
        "reason": "no_evidence",
        "entail": 0.0,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-102_v1.0#s04u04",
            "score": 0.676788
          },
          {
            "pid": "SOP-MFG-102_v1.0#s00u01",
            "score": 0.426494
          },
          {
            "pid": "SOP-MFG-102_v1.0#s00u00",
            "score": 0.382604
          },
          {
            "pid": "SOP-MFG-102_v1.0#s01u01",
            "score": 0.372595
          },
          {
            "pid": "SOP-MFG-102_v1.0#s04u03",
            "score": 0.353013
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "supported",
        "reason": null,
        "entail": 0.9609375,
        "signal": "entail",
        "nPassages": 20
      },
      "rescued": true
    },
    {
      "id": "SOP-MFG-147_v1.0::states::00",
      "doc": "SOP-MFG-147",
      "rel": "states",
      "claim": "The Production Engineer assigned to MFG-SYS-1147 manages suite utilities within Cleanroom Suite 107-D while supervising equipment maintenance.",
      "basis": "Section 3 explicitly states that the Production Engineer manages suite utilities in Cleanroom Suite 107-D and supervises maintenance on MFG-SYS-1147.",
      "missKind": "no_evidence",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-147_v1.0#s01",
            "score": 0.397111
          },
          {
            "pid": "SOP-MFG-147_v1.0#s03",
            "score": 0.392285
          },
          {
            "pid": "SOP-MFG-147_v1.0#s02",
            "score": 0.346243
          },
          {
            "pid": "SOP-MFG-147_v1.0#s04",
            "score": 0.341941
          },
          {
            "pid": "SOP-MFG-147_v1.0#s06",
            "score": 0.262472
          }
        ],
        "rules": [
          "A2_retrieval_empty"
        ],
        "verdict": "not_checkable",
        "reason": "no_evidence",
        "entail": 0.0,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-147_v1.0#s03u01",
            "score": 0.923729
          },
          {
            "pid": "SOP-MFG-147_v1.0#s01u02",
            "score": 0.719003
          },
          {
            "pid": "SOP-MFG-147_v1.0#s04u00",
            "score": 0.591119
          },
          {
            "pid": "SOP-MFG-147_v1.0#s02u01",
            "score": 0.447472
          },
          {
            "pid": "SOP-MFG-147_v1.0#s02u00",
            "score": 0.270731
          }
        ],
        "rules": [
          "B5_degree",
          "C6c_inferred"
        ],
        "verdict": "supported",
        "reason": null,
        "entail": 0.99609375,
        "signal": "entail",
        "nPassages": 20
      },
      "rescued": true
    },
    {
      "id": "SOP-CSV-155_v3.0::entails::01",
      "doc": "SOP-CSV-155",
      "rel": "entails",
      "claim": "Electronic records generated during the pressure differential calibration of equipment CSV-SYS-1155 fall under the regulatory scope of 21 CFR Part 11.",
      "basis": "Section 2 states SOP-CSV-155 enforces 21 CFR Part 11 requirements for pressure differential calibration on CSV-SYS-1155 across Audit Trail Verification.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-CSV-155_v3.0#s01",
            "score": 0.60247
          },
          {
            "pid": "SOP-CSV-155_v3.0#s02",
            "score": 0.601011
          },
          {
            "pid": "SOP-CSV-155_v3.0#s04",
            "score": 0.506984
          },
          {
            "pid": "SOP-CSV-155_v3.0#s00",
            "score": 0.481589
          },
          {
            "pid": "SOP-CSV-155_v3.0#s03",
            "score": 0.46203
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.9921875,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-CSV-155_v3.0#s02u00",
            "score": 0.641066
          },
          {
            "pid": "SOP-CSV-155_v3.0#s01u00",
            "score": 0.582693
          },
          {
            "pid": "SOP-CSV-155_v3.0#s01u02",
            "score": 0.547561
          },
          {
            "pid": "SOP-CSV-155_v3.0#s03u01",
            "score": 0.496314
          },
          {
            "pid": "SOP-CSV-155_v3.0#s00u01",
            "score": 0.478243
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.9970703125,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-MFG-009_v3.0::entails::01",
      "doc": "SOP-MFG-009",
      "rel": "entails",
      "claim": "Operational parameters falling below the fifty percent dissolved oxygen swab residue threshold require an immediate manufacturing halt on equipment MFG-SYS-1009.",
      "basis": "Section 4.5 states parameter breaches beyond DO >= 50% mandate an immediate Quality Hold.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-009_v3.0#s01",
            "score": 0.621495
          },
          {
            "pid": "SOP-MFG-009_v3.0#s00",
            "score": 0.620503
          },
          {
            "pid": "SOP-MFG-009_v3.0#s04",
            "score": 0.59656
          },
          {
            "pid": "SOP-MFG-009_v3.0#s02",
            "score": 0.555831
          },
          {
            "pid": "SOP-MFG-009_v3.0#s05",
            "score": 0.527205
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-009_v3.0#s00u00",
            "score": 0.640502
          },
          {
            "pid": "SOP-MFG-009_v3.0#s04u03",
            "score": 0.62641
          },
          {
            "pid": "SOP-MFG-009_v3.0#s00u01",
            "score": 0.614956
          },
          {
            "pid": "SOP-MFG-009_v3.0#s01u01",
            "score": 0.603042
          },
          {
            "pid": "SOP-MFG-009_v3.0#s05u00",
            "score": 0.553967
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.9990234375,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-MFG-099_v2.0::entails::01",
      "doc": "SOP-MFG-099",
      "rel": "entails",
      "claim": "A recorded dissolved oxygen chromatographic signal-to-noise ratio of thirty percent during manufacturing mandates initiating an immediate Quality Hold.",
      "basis": "Section 4.5 states deviations from DO >= 40% mandate an immediate Quality Hold; 30% is below 40% and thus necessarily triggers a hold.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-099_v2.0#s05",
            "score": 0.526913
          },
          {
            "pid": "SOP-MFG-099_v2.0#s00",
            "score": 0.510065
          },
          {
            "pid": "SOP-MFG-099_v2.0#s01",
            "score": 0.44869
          },
          {
            "pid": "SOP-MFG-099_v2.0#s04",
            "score": 0.441656
          },
          {
            "pid": "SOP-MFG-099_v2.0#s02",
            "score": 0.391548
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99462890625,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-099_v2.0#s00u01",
            "score": 0.528757
          },
          {
            "pid": "SOP-MFG-099_v2.0#s05u00",
            "score": 0.514762
          },
          {
            "pid": "SOP-MFG-099_v2.0#s00u00",
            "score": 0.497682
          },
          {
            "pid": "SOP-MFG-099_v2.0#s01u01",
            "score": 0.484185
          },
          {
            "pid": "SOP-MFG-099_v2.0#s04u03",
            "score": 0.381292
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.9970703125,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-MFG-142_v2.0::entails::01",
      "doc": "SOP-MFG-142",
      "rel": "entails",
      "claim": "Any observed temperature value outside the range of 2.5\u00b0C to 4.5\u00b0C during particulate camera calibration automatically mandates filing a formal CAPA.",
      "basis": "Sections 4.5 and 5 state out-of-limit values beyond 2.5\u00b0C to 4.5\u00b0C initiate escalation and non-conformances require immediate CAPA filing.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-MFG-142_v2.0#s01",
            "score": 0.482968
          },
          {
            "pid": "SOP-MFG-142_v2.0#s00",
            "score": 0.422609
          },
          {
            "pid": "SOP-MFG-142_v2.0#s02",
            "score": 0.401585
          },
          {
            "pid": "SOP-MFG-142_v2.0#s04",
            "score": 0.382159
          },
          {
            "pid": "SOP-MFG-142_v2.0#s05",
            "score": 0.376081
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-MFG-142_v2.0#s01u00",
            "score": 0.473167
          },
          {
            "pid": "SOP-MFG-142_v2.0#s02u00",
            "score": 0.47096
          },
          {
            "pid": "SOP-MFG-142_v2.0#s00u01",
            "score": 0.459528
          },
          {
            "pid": "SOP-MFG-142_v2.0#s04u01",
            "score": 0.428137
          },
          {
            "pid": "SOP-MFG-142_v2.0#s01u01",
            "score": 0.427594
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.998046875,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-QC-088_v3.0::entails::01",
      "doc": "SOP-QC-088",
      "rel": "entails",
      "claim": "If a defrost cycle during stability chamber testing reaches seven hours, production personnel must initiate an immediate Quality Hold.",
      "basis": "The document caps defrost cycles at 6 hours and mandates an immediate Quality Hold for breaches beyond 6 hours, which logically includes 7 hours.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-QC-088_v3.0#s00",
            "score": 0.573126
          },
          {
            "pid": "SOP-QC-088_v3.0#s05",
            "score": 0.543838
          },
          {
            "pid": "SOP-QC-088_v3.0#s01",
            "score": 0.543103
          },
          {
            "pid": "SOP-QC-088_v3.0#s04",
            "score": 0.437763
          },
          {
            "pid": "SOP-QC-088_v3.0#s02",
            "score": 0.337843
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99755859375,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-QC-088_v3.0#s00u01",
            "score": 0.621348
          },
          {
            "pid": "SOP-QC-088_v3.0#s04u03",
            "score": 0.620925
          },
          {
            "pid": "SOP-QC-088_v3.0#s01u01",
            "score": 0.603416
          },
          {
            "pid": "SOP-QC-088_v3.0#s00u00",
            "score": 0.602271
          },
          {
            "pid": "SOP-QC-088_v3.0#s05u00",
            "score": 0.547954
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-SCM-056_v3.0::entails::01",
      "doc": "SOP-SCM-056",
      "rel": "entails",
      "claim": "Any commercial batch of Eta-Patch 15mg Transdermal System failing to meet the maximum allowable pressure decay rate standard automatically triggers a root cause analysis.",
      "basis": "Sections 4.5 and 5 state that pressure decay rate excursions trigger Quality Containment, which mandates an immediate root cause analysis.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-SCM-056_v3.0#s05",
            "score": 0.66964
          },
          {
            "pid": "SOP-SCM-056_v3.0#s04",
            "score": 0.420889
          },
          {
            "pid": "SOP-SCM-056_v3.0#s00",
            "score": 0.40415
          },
          {
            "pid": "SOP-SCM-056_v3.0#s03",
            "score": 0.369909
          },
          {
            "pid": "SOP-SCM-056_v3.0#s01",
            "score": 0.335438
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.998046875,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-SCM-056_v3.0#s05u00",
            "score": 0.627373
          },
          {
            "pid": "SOP-SCM-056_v3.0#s04u02",
            "score": 0.584795
          },
          {
            "pid": "SOP-SCM-056_v3.0#s02u01",
            "score": 0.551025
          },
          {
            "pid": "SOP-SCM-056_v3.0#s03u02",
            "score": 0.538326
          },
          {
            "pid": "SOP-SCM-056_v3.0#s00u01",
            "score": 0.436123
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99951171875,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    },
    {
      "id": "SOP-SCM-186_v3.0::entails::01",
      "doc": "SOP-SCM-186",
      "rel": "entails",
      "claim": "Manufacturing a batch of Eta-Patch 15mg Transdermal System requires verifying calibration certification for equipment SCM-SYS-1186 prior to starting production.",
      "basis": "Step 4.1 requires verifying calibration certification before step 4.3 executes batch manufacturing.",
      "missKind": "no_entail_signal",
      "section": {
        "retrieval": [
          {
            "pid": "SOP-SCM-186_v3.0#s02",
            "score": 0.60475
          },
          {
            "pid": "SOP-SCM-186_v3.0#s04",
            "score": 0.574322
          },
          {
            "pid": "SOP-SCM-186_v3.0#s03",
            "score": 0.504485
          },
          {
            "pid": "SOP-SCM-186_v3.0#s05",
            "score": 0.487661
          },
          {
            "pid": "SOP-SCM-186_v3.0#s01",
            "score": 0.407606
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99658203125,
        "signal": "neutral",
        "nPassages": 7
      },
      "fine": {
        "retrieval": [
          {
            "pid": "SOP-SCM-186_v3.0#s02u01",
            "score": 0.726838
          },
          {
            "pid": "SOP-SCM-186_v3.0#s04u02",
            "score": 0.656086
          },
          {
            "pid": "SOP-SCM-186_v3.0#s03u02",
            "score": 0.646316
          },
          {
            "pid": "SOP-SCM-186_v3.0#s04u00",
            "score": 0.532709
          },
          {
            "pid": "SOP-SCM-186_v3.0#s05u00",
            "score": 0.487794
          }
        ],
        "rules": [
          "B5_degree"
        ],
        "verdict": "not_checkable",
        "reason": "no_entail_signal",
        "entail": 0.99853515625,
        "signal": "neutral",
        "nPassages": 20
      },
      "rescued": false
    }
  ]
};
