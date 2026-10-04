from __future__ import annotations
import hashlib, json
from pathlib import Path

root=Path(__file__).resolve().parent
freeze=json.loads((root/'FREEZE.json').read_text())
errors=[]
for rel, expected in freeze['files'].items():
    p=root/rel
    if p.is_symlink() or not p.is_file():
        errors.append(f'missing or symlink: {rel}'); continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got != expected: errors.append(f'hash mismatch: {rel}')
print(json.dumps({'evidence_class':'PREPARATION_KIT_INTEGRITY_ONLY','files_checked':len(freeze['files']),'errors':errors,'passed':not errors,'candidate_executed':False},sort_keys=True))
raise SystemExit(1 if errors else 0)
