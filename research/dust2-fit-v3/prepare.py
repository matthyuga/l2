"""Isolated revision after Kevin's V2 door/feet feedback; never rerun V2 installers."""
from pathlib import Path
import sys,json,shutil,struct,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];V2=R/'research/dust2-scale-v2';C=R.parent/'l2'
sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((V2/'installation.json').read_text(encoding='utf-8'))
assert all(sha(r['target'])==r['after_sha256'] for r in m['files'])
(D/'source-hashes.json').write_text(json.dumps({r['target']:sha(r['target']) for r in m['files']},indent=2))
b=json.loads((V2/'build-audit.json').read_text());b.update(scale=.32,goldsrc_scale=1.,previous_goldsrc_scale=.625)
(D/'build-audit.json').write_text(json.dumps(b,indent=2))
(D/'stage/StaticMeshes').mkdir(parents=True,exist_ok=True);shutil.copy2(V2/'stage/StaticMeshes/HGDust2Arena.usx',D/'stage/StaticMeshes/HGDust2Arena.usx')
m=Edit(C/'Maps/24_19.unr');disabled=[]
for i,e in enumerate(m.exports):
 if e['name'].startswith('HGDust2ArenaDustPart'):
  m.replace(e,change_props(m,e,{'DrawScale':m.float('DrawScale',.32)}))
 elif e['name'].startswith(('HGDust2V2Floor','HGDust2V2Wall')):
  disabled.append(i+1);changes={n:m.boolean(n,False) for n in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']};m.replace(e,change_props(m,e,changes))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;n=r.num('i');assert r.num('i')==n;refs=[r.compact() for _ in range(n)];end=r.p;refs=[v for v in refs if v not in set(disabled)]
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(refs),len(refs))+b''.join(ci(v) for v in refs)+m.b[end:level['offset']+level['size']]);m.save(D/'stage/Maps/24_19.unr')
s=(V2/'build_geodata.py').read_text(encoding='utf-8').replace('.625','1.0').replace('cfg.AGENT_HEIGHT=64','cfg.AGENT_HEIGHT=80').replace('cfg.LAYER_MERGE=8','cfg.LAYER_MERGE=8.1').replace('z-22.5+43.35','z-36+43.35')
# Preserve exact visual heights before the mandatory 8u geodata quantization.
s=s.replace('layers={};rejected=0','layers={};rejected=0;exact={}')
s=s.replace('ls.append(z&~7)','ls.append(z&~7);exact[(gx,gy,z&~7)]=z-43.0')
s += "\n(D/'visual-floors.json').write_text(json.dumps([[*k,v] for k,v in exact.items()]))\n"
(D/'build_geodata.py').write_text(s,encoding='utf-8')
print('FIT_V3_PREPARED',len(disabled),'V2 collision references removed; GoldSrc scale 1.0')
