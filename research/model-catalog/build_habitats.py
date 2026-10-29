"""Index documented NPC appearances without changing the game or gallery catalog.

Named spawn files are source classifications, not a complete official bestiary.
Grid files retain their raw sector; selected landmark surroundings are explicitly
approximate and consider height so underground inhabitants are not placed above.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib,datetime,collections

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game/data'
OUT=Path(__file__).resolve().parent/'habitats.json'
REGIONS={'Aden':'Aden','Dion':'Dion','Giran':'Giran','Gludin':'Gludin','Gludio':'Gludio','Goddard':'Goddard','Hunters':'Hunters Village','Innadril':'Innadril / Heine','Rune':'Rune','Schuttgart':'Schuttgart','TalkingIsland':'Talking Island','DarkElfTerritory':'Dark Elven Village','ElvenTerritory':'Elven Village','DwarvenTerritory':'Dwarven Village','OrcTerritory':'Orc Village','Catacombs':'Catacumbas y necrópolis','SevenSigns':'Seven Signs','Castles':'Castillos','Others':'Sectores sin clasificación nominal'}
SPECIAL={'TurekOrcs':'Orc Barracks / Turek Orcs','AdenNPCs':'Aden - habitantes','DionNPCs':'Dion - habitantes','GiranNPCs':'Giran - habitantes','GludioNPCs':'Gludio - habitantes','GludinVillageNPCs':'Gludin - habitantes','FloranVillageNPCs':'Floran - habitantes','HeineNPCs':'Heine - habitantes','VarkaSlenosOutpost':'Varka Silenos Outpost','PavelArchaic':'Pavel Ruins','GiantsCave':"Giant's Cave",'ForgeOfGods':'Forge of the Gods','BrekasStronghold':"Breka's Stronghold"}
def label(stem):
 return SPECIAL.get(stem,re.sub(r'(?<=[a-z0-9])(?=[A-Z])',' ',stem).replace('NPCs',' - habitantes'))
zones={}; index=collections.defaultdict(dict); audit=[]; excluded=collections.Counter()
def add(npc_id,key,region,name,method,source,xyz=None):
 zones.setdefault(key,{'id':key,'region':region,'name':name,'method':method})
 entry=index[str(npc_id)].setdefault(key,{'zone':key,'sources':set(),'records':0,'example':xyz})
 entry['sources'].add(source);entry['records']+=1
for file in sorted((DATA/'spawns').rglob('*.xml')):
 rel=file.relative_to(DATA).as_posix(); folder=file.parent.name;stem=file.stem
 root=ET.parse(file).getroot()
 if root.get('enabled','true').lower()=='false':excluded['disabled_files']+=1;continue
 if stem in {'FakePlayers','SoloArena','TreasureBoxes','Gremlins'}:excluded['non_geographic_files']+=1;continue
 audit.append({'path':rel,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 grid=bool(re.fullmatch(r'\d+_\d+(?:_.*)?',stem))
 for spawn in root.findall('spawn'):
  if spawn.get('enabled','true').lower()=='false':continue
  for npc in spawn.findall('npc'):
   npc_id=int(npc.get('id','0'))
   # Lab/custom IDs are not evidence for classic habitats.
   if not (1<=npc_id<40000):excluded['custom_spawn_records']+=1;continue
   xyz=[int(npc.get(k)) for k in ['x','y','z']] if all(npc.get(k) is not None for k in ['x','y','z']) else None
   region=REGIONS.get(folder,folder)
   if grid:
    add(npc_id,'grid:'+stem,region,'Cuadrícula '+stem,'grid',rel,xyz)
    if xyz:
     x,y,z=xyz
     # Center from the local administrative destination. Radius is an editorial
     # surroundings search, not an extracted official polygon.
     for tag,name,cx,cy,radius in [('despair','Ruins of Despair',-19120,136816,8000),('agony','Ruins of Agony',-42628,119766,7500)]:
      if -5000<=z<=0 and (x-cx)**2+(y-cy)**2<=radius**2:
       add(npc_id,'near:'+tag,'Gludio',name+' - entorno aproximado','approximate',rel,xyz)
   else:
    if folder=='Castles':region=stem
    if stem=='FloranVillageNPCs':region='Dion'
    add(npc_id,'spawn:'+folder+'/'+stem,region,label(stem),'named_file',rel,xyz)
for npc,zs in index.items():
 for entry in zs.values():entry['sources']=sorted(entry['sources'])
 zone_entries=list(zs.values());index[npc]=zone_entries
for zone in zones.values():zone['npc_count']=sum(any(e['zone']==zone['id'] for e in zs) for zs in index.values())
result={'generated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_root':str(DATA),'description':'Apariciones de la copia local de Mobius Interlude. No certifica el canon ni incluye todos los spawns creados por scripts.','methods':{'named_file':'Grupo con nombre en los archivos de apariciones','grid':'Sólo consta la cuadrícula del mapa','approximate':'Cercanía a un destino administrativo; no es un límite oficial de zona'},'approximate_landmarks':[{'name':'Ruins of Despair','center':[-19120,136816],'radius':8000,'z_range':[-5000,0]},{'name':'Ruins of Agony','center':[-42628,119766],'radius':7500,'z_range':[-5000,0]}],'zones':sorted(zones.values(),key=lambda z:(z['region'],z['name'])),'npcs':dict(index),'sources':audit,'excluded':dict(excluded)}
OUT.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(json.dumps({'zones':len(zones),'npc_ids':len(index),'source_files':len(audit),'output':str(OUT),'approximate':{z['name']:z['npc_count'] for z in zones.values() if z['method']=='approximate'}},ensure_ascii=False))
