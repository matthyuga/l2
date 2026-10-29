from pathlib import Path
import xml.etree.ElementTree as E
r=Path(__file__).resolve().parents[2]
seen=set()
for p in (r/'server/game/data/stats/npcs').glob('*.xml'):
 for n in E.parse(p).getroot().findall('npc'):
  name=n.get('name','')
  if any(s in name for s in ('Merrow','Magnus','Seraphim','Soulless','Nightshade','Feline','Kai the Cat','Kat the Cat','Boxer','Corrupted','Reanimated','Dark Panther','Spectral Lord')) and name not in seen:
   seen.add(name);print(n.get('id'),name,'attack=',E.tostring(n.find('stats/attack'),encoding='unicode').strip(),'skills=',E.tostring(n.find('skillList'),encoding='unicode').strip() if n.find('skillList') is not None else '')
