from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3];backup=root/'backups/amber-ui-rain-2026-10-10'
state=backup/'mirror-state.json';synced=json.loads(state.read_text()) if state.exists() else {}
paths=[Path('game/data/scripts/custom/AmberContract')/n for n in ('AmberContract.java','AmberAssist.java','AmberContractVerification.java')]+[Path('game/data/scripts/custom/SkillCatalog/SkillCatalog.java'),Path('game/data/stats/skills/custom/amber_contract.xml')]
for rel in paths:
    runtime=root/'server'/rel;wanted=hashlib.sha256(runtime.read_bytes()).hexdigest()
    original=hashlib.sha256((backup/'server'/rel.name).read_bytes()).hexdigest()
    for base in ('source/L2J_Mobius_CT_0_Interlude','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'):
        target=root/base/'dist'/rel;key=str(target.relative_to(root));current=hashlib.sha256(target.read_bytes()).hexdigest()
        assert current in (original,wanted,synced.get(key)), 'Concurrent mirror edit: '+key
        saved=backup/'mirrors'/key;saved.parent.mkdir(parents=True,exist_ok=True)
        if not saved.exists():shutil.copy2(target,saved)
        shutil.copy2(runtime,target);synced[key]=wanted
state.write_text(json.dumps(synced,indent=2));print('PASS: five runtime sources/data mirrored with concurrency guards.')
