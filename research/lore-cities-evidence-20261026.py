from pathlib import Path
import hashlib,json,re
base=Path('E:/l2-local/server/game/data')
out=Path('E:/l2-local/research/lore-ciudades-20261026');out.mkdir(exist_ok=True)
sel={
'Talking Island':['html/default/30008.htm','html/default/30017.htm','html/default/30311.htm','html/default/30311-1.htm','html/default/30406.htm','html/guard/30039-1.htm','html/guard/30041-1.htm','html/guard/30043-1.htm','html/guard/30045.htm','html/guard/30046-1.htm'],
'Gludin':['html/guard/30379.htm','html/guard/30379-1.htm','html/guard/30379-2.htm','html/guard/30381.htm','html/guard/30382-1.htm','html/guard/30382-3.htm'],
'Gludio':['html/guard/30334.htm','html/guard/30336-1.htm','html/guard/30346-1.htm','html/guard/30383-1.htm','html/default/30405-1.htm','html/default/30405-2.htm','html/default/30417.htm'],
'Dion':['html/guard/30452-1.htm'],
'Giran':['html/guard/30709-2.htm'],
'Oren':['html/guard/30710-1.htm','html/guard/30710-2.htm'],
'Aden':['html/guard/30870.htm','html/guard/30871-1.htm','html/guard/30875.htm'],
'Goddard':['html/guard/31293.htm','html/guard/31296.htm','html/guard/31296-2.htm','html/villagemaster/31279.htm'],
'Schuttgart':['html/guard/31987-1.htm','html/villagemaster/31977.htm','scripts/quests/Q00117_TheOceanOfDistantStars/32052-03.htm','scripts/quests/Q00117_TheOceanOfDistantStars/32052-05.htm']}
entries=[];missing=[]
for city,paths in sel.items():
 for rel in paths:
  p=base/rel
  if not p.exists():missing.append(str(p));continue
  raw=p.read_bytes();html=raw.decode('utf-8',errors='replace');plain=re.sub('<[^>]+>',' ',html);plain=re.sub(r'\s+',' ',plain).strip()
  entries.append(dict(city=city,path=str(p),sha256=hashlib.sha256(raw).hexdigest(),text=plain))
(out/'evidencia-local.json').write_text(json.dumps(dict(date='2026-10-26',scope='Static local datapack text, not live server observations',entries=entries,missing=missing),ensure_ascii=False,indent=2),encoding='utf8')
report=Path('E:/l2-local/research/LORE-CIUDADES-INVESTIGACION-20261026.md').read_text(encoding='utf8')
for city in sel:assert ('## '+city) in report
assert not missing,missing
print(json.dumps(dict(local_sources=len(entries),cities=len(sel),missing=missing,report_words=len(report.split())),ensure_ascii=False))
