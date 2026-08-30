from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED_SHA256="820b5a64cf4187998f2c4b416293c8fd0a577b564cab31be22dddd4ace822d23"


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("path"); a=p.parse_args(); raw=Path(a.path).read_bytes(); data=json.loads(raw)
    assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA256
    cases=data["cases"]; assert len(cases)==100
    assert sum(c["expected_status"]=="resolved" for c in cases)==70
    assert sum(c["expected_status"]=="unknown" for c in cases)==30
    fam={}
    for c in cases: fam[c["family"]]=fam.get(c["family"],0)+1
    for name in ("membership_rule","subclass","only_permission","quantifier","group_scope","role_binding","temporal_membership","ambiguous_reference","insufficient_authority","ontology_escape"):
        assert fam[name]==10, (name,fam.get(name))
    assert len(data["mutation_pairs"])==12
    ids={c["case_id"] for c in cases}; assert len(ids)==100
    for pair in data["mutation_pairs"]: assert pair["a"] in ids and pair["b"] in ids
    print(json.dumps({"status":"ok","sha256":EXPECTED_SHA256,"families":fam},sort_keys=True))

if __name__=="__main__": main()
