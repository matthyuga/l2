from pathlib import Path
import json,zipfile,hashlib
root=Path('E:/l2-local');s=Path(__file__).resolve().parent
m=json.loads((root/'research/pvp-rounds/installation.json').read_text());baseline=Path(m['core_baseline']['backup'])
patches={}
for name in ['20261015-elven-position-sync','20261015-pvp-rounds']:
    folder=root/'server/pending-core-patches'/name
    assert (folder/'.applied').exists(),name
    for p in folder.rglob('*.class'):patches[p.relative_to(folder).as_posix()]=p.read_bytes()
with zipfile.ZipFile(baseline) as old,zipfile.ZipFile(root/'server/libs/GameServer.jar') as current:
    oldnames=set(old.namelist());names=set(current.namelist());assert not oldnames-names,'Missing baseline entries'
    for name in names:
        expected=patches[name] if name in patches else old.read(name) if name in oldnames else b'' if name.endswith('/') else None
        assert current.read(name)==expected,name
result={'status':'PASS','staged_classes_applied':len(patches),'all_other_core_entries_preserved':True,'core_sha256':hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest()}
(s/'activation-core-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
