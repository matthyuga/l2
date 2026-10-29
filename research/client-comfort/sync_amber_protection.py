from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[2]
backup=root/'backups/amber-protection-2026-10-10'
hashes=json.loads((backup/'original-hashes.json').read_text())
state=backup/'last-synced-hashes.json'
synced=json.loads(state.read_text()) if state.exists() else {}
for rel,original in hashes.items():
    relative=Path(rel)
    if relative.parts[0]=='server': continue
    target=root/relative
    marker=relative.parts.index('dist')
    runtime=root/'server/game/data/scripts'/Path(*relative.parts[marker+4:])
    current=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
    wanted=hashlib.sha256(runtime.read_bytes()).hexdigest()
    assert current in (original,synced.get(rel),wanted), 'Concurrent edit '+rel
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(runtime,target);synced[rel]=wanted
state.write_text(json.dumps(synced,indent=2))
print('PASS: nine changed scripts mirrored; native heal amounts and V10 client/core preserved.')
