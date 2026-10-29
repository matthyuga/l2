from pathlib import Path
import hashlib,shutil,json
root=Path(__file__).resolve().parents[2]
backup=root/'backups/amber-target-policy-2026-10-10'
hashes=json.loads((backup/'original-hashes.json').read_text())
state=backup/'last-synced-hashes.json'
synced=json.loads(state.read_text()) if state.exists() else {}
files=[Path('AmberContract')/name for name in ('AmberContract.java','AmberServitor.java','AmberAssist.java','AmberContractVerification.java')]+[Path('LabCombatPilots/LabCombatPilots.java')]
for rel in files:
    runtime=root/'server/game/data/scripts/custom'/rel
    original=hashes[str(runtime.relative_to(root))]
    for base in (root/'source/L2J_Mobius_CT_0_Interlude',root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'):
        target=base/'dist/game/data/scripts/custom'/rel
        if target.exists():
            current=hashlib.sha256(target.read_bytes()).hexdigest()
            assert current in (original,hashlib.sha256(runtime.read_bytes()).hexdigest(),synced.get(str(target))),'Concurrent edit: '+str(target)
            saved=backup/target.relative_to(root);saved.parent.mkdir(parents=True,exist_ok=True)
            if not saved.exists():shutil.copy2(target,saved)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(runtime,target)
        synced[str(target)]=hashlib.sha256(runtime.read_bytes()).hexdigest()
state.write_text(json.dumps(synced,indent=2))
print('PASS: five changed sources mirrored; V10 visuals and client/core untouched.')
