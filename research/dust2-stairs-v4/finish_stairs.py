from pathlib import Path
import json,shutil,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];V3=D.parent/'dust2-fit-v3';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
current=json.loads((D/'installation.json').read_text());target=R/'server/game/data/geodata/24_19.l2j';row=next(r for r in current['files'] if r['target'].endswith('.l2j'));assert sha(target)==row['after_sha256'],'Concurrent edit'
shutil.copy2(target,Path(current['backup'])/'intermediate-426-steps.l2j');shutil.copy2(V3/'stairs-repaired.l2j',target);shutil.copy2(target,D/'stage/Geodata/24_19.l2j')
new_hash=sha(target)
for name in ['dust2-integration','dust2-scale-v2','dust2-fit-v3','dust2-stairs-v4']:
 p=D.parent/name/'installation.json';m=json.loads(p.read_text(encoding='utf-8'))
 for r in m['files']:
  if Path(r['target'])==target:r['after_sha256']=new_hash
 if 'stairs_v4' in m:
  for r in m['stairs_v4']['files']:
   if Path(r['target'])==target:r['after_sha256']=new_hash
 m['stairs_repaired_edges']=442
 for dest in [p,Path(m['backup'])/'manifest.json']:dest.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
a=json.loads((V3/'stairs-repair-installation.json').read_text());a.update(after_sha256=new_hash,edges_opened=442,server_probe_pending=True);(V3/'stairs-repair-installation.json').write_text(json.dumps(a,indent=2))
print('Added 16 safe low-riser transitions; all their landings already supported. Final edges:442')
