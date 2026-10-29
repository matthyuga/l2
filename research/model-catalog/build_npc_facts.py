"""Extract actual NPC template levels/types, without changing the game."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,datetime

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'server/game/data/stats/npcs'
facts={};sources=[]
for p in sorted(DATA.rglob('*.xml')):
 root=ET.parse(p).getroot()
 if root.get('enabled','true').lower()=='false':continue
 for n in root.findall('npc'):
  if not n.get('id'):continue
  key=n.get('id')
  if key in facts:raise ValueError('Duplicate NPC template '+key)
  level=n.get('level')
  facts[key]={'level':int(level) if level and level.isdigit() else None,'type':n.get('type',''),'race':n.findtext('race',''),'source':p.relative_to(ROOT).as_posix()}
 sources.append(p.relative_to(ROOT).as_posix())
output=Path(__file__).with_name('npc-facts.json')
output.write_text(json.dumps({'generated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'description':'Nivel y tipo de las plantillas del servidor local. No representan necesariamente los stats oficiales sin modificar.','npcs':facts,'sources':sources},ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({'npc_templates':len(facts),'levels':sum(f['level'] is not None for f in facts.values()),'files':len(sources)}))
