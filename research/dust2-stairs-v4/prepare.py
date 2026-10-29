from pathlib import Path
import json,sys,struct,shutil,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];V3=D.parent/'dust2-fit-v3';C=R.parent/'l2';sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(D/'stage/Geodata').mkdir(parents=True,exist_ok=True);shutil.copy2(R/'server/game/data/geodata/24_19.l2j',D/'stage/Geodata/24_19.l2j')
shutil.copy2(V3/'visual-floors.json',D/'visual-floors.json');shutil.copy2(V3/'geodata-audit.json',D/'geodata-audit.json')
(D/'source-hashes.json').write_text(json.dumps({str(C/'Maps/24_19.unr'):sha(C/'Maps/24_19.unr'),str(R/'server/game/data/geodata/24_19.l2j'):sha(R/'server/game/data/geodata/24_19.l2j')},indent=2))
m=Edit(C/'Maps/24_19.unr');disabled=[]
for i,e in enumerate(m.exports):
 if e['name'].startswith(('HGDust2V3Floor','HGDust2V3Wall')):
  disabled.append(i+1);changes={n:m.boolean(n,False) for n in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']};m.replace(e,change_props(m,e,changes))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;n=r.num('i');assert r.num('i')==n;refs=[r.compact() for _ in range(n)];end=r.p;refs=[v for v in refs if v not in set(disabled)]
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(refs),len(refs))+b''.join(ci(v) for v in refs)+m.b[end:level['offset']+level['size']]);m.save(D/'stage/Maps/24_19.unr')
for folder in ['native-floor','native-walls']:
 for file in ['build.py','verify.py']:
  s=(V3/folder/file).read_text(encoding='utf-8').replace('HGDust2V3','HGDust2V4').replace('<=24','<=32')
  if folder=='native-floor':s=s.replace('assert len(covered)==30372',"assert len(covered)==json.loads((D/'audit.json').read_text())['reachable_layers']")
  else:
   s=s.replace('assert len(seen)==30372',"assert len(seen)==json.loads((BASE/'native-floor/audit.json').read_text())['reachable_layers']")
  if folder=='native-walls' and file=='build.py':s=s.replace('h>z+24','h>z+32')
  p=D/folder/file;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
s=(V3/'check_clearance.py').read_text().replace('<=16','<=32');(D/'check_clearance.py').write_text(s)
print('Prepared replacement support and walls for all newly reachable stair landings')
