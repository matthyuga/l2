"""Build passive native fake-player mannequins; reuse installed item templates only."""
from pathlib import Path
import json,collections,copy,re,math,unicodedata,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];OUT=ROOT/'showcase';OUT.mkdir(exist_ok=True)
m=json.loads((ROOT/'installation.json').read_text());items=m['items'];byid={x['id']:x for x in items};packs={p['key']:p for p in m['packs']};xml={}
for p in (PROJECT/'server/game/data/stats/items').glob('*.xml'):
 for e in ET.parse(p).getroot().findall('item'):xml[int(e.get('id'))]=e
rows={}
for name in ['weapongrp','armorgrp']:
 for line in (ROOT/'stage'/(name+'.add.txt')).read_text(encoding='utf-8').splitlines()[1:]:
  r=line.split('\t');rows[int(r[1])]=r
def clean(s):return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().strip()
def shortpack(key):
 return {'b1-06-leviathan':'Leviathan','b1-03-fafurion-weapons-with-effects-level-3':'Fafurion L3','b2-06-pandorium-blue-green-red':'Pandorium','b2-07-dynasty-armor-with-shoulders-v1-5':'Dynasty shoulders','b2-04-blaze-pack-armor-weapon-helmet-wings':'Blaze','b2-05-vesper-red-armor-weapon-helmet-wings':'Vesper Red','b3-02-valakas-red-and-blue-effect':'Valakas','b3-06-ixion-titanium-armor-weapons':'Ixion Titanium','b3-08-saint-seiya-armor':'Saint Seiya','b2-10-19-helmet-pack':'Helmet collection'}.get(key,clean(packs[key]['name']).split(':')[0][:24])
defaults={'equipHead':6378,'equipChest':6373,'equipLegs':6374,'equipGloves':6375,'equipFeet':6376,'equipRHand':0,'equipLHand':0,'equipHair':0,'equipHair2':0}
slots={'head':'equipHead','chest':'equipChest','onepiece':'equipChest','legs':'equipLegs','gloves':'equipGloves','feet':'equipFeet','hair':'equipHair'}
weapons=[];shields=[];seen={};duplicates={}
for i in items:
 if i['kind']!='weapon':continue
 r=rows[i['id']];sig=(i['pack'],tuple(r[26:32]),r[39],r[58],r[59])
 if sig in seen:duplicates[i['id']]=seen[sig];continue
 seen[sig]=i['id'];(shields if i['server_type']=='Armor' else weapons).append(i)
armors=[];covered=set();usedweapons=set();assignedshields=set()
for key,pack in packs.items():
 arm=[i for i in items if i['pack']==key and i['kind']=='armor'];torsos=[i for i in arm if i['bodypart'] in ('chest','onepiece')]
 for idx,body in enumerate(torsos):
  equip=defaults.copy();equip.update(equipRHand=0,equipLHand=0,equipHead=0,equipLegs=0 if body['bodypart']=='onepiece' else 6374)
  own=[body];equip['equipChest']=body['id']
  for part in ['head','legs','gloves','feet']:
   if part=='legs' and body['bodypart']=='onepiece':continue
   candidates=[i for i in arm if i['bodypart']==part]
   if not candidates:continue
   if len(candidates)==len(torsos):candidate=candidates[idx]
   else:
    tokens=set(re.findall(r'(?:t\d{2,5}|heavy|light|robe|blue|green|red)', ' '.join(rows[body['id']]).lower()))
    def score(i):
     other=set(re.findall(r'(?:t\d{2,5}|heavy|light|robe|blue|green|red)', ' '.join(rows[i['id']]).lower()))
     return (len(tokens&other),-abs(body['id']-i['id']))
    candidate=max(candidates,key=score)
   equip[slots[part]]=candidate['id'];own.append(candidate)
  if key=='b3-08-saint-seiya-armor':
   helmet=next((i for i in arm if i['old_id']==30000+(body['old_id']-26400)),None)
   if helmet:equip['equipHead']=0;equip['equipHair']=helmet['id'];own.append(helmet)
  same=[w for w in weapons if w['pack']==key and w['id'] not in usedweapons]
  w=next(iter(same),next((w for w in weapons if w['id'] not in usedweapons),None))
  if w:equip['equipRHand']=w['id'];usedweapons.add(w['id']);own.append(w)
  at=int(rows[body['id']][326]);role={0:'Uniforme',1:'Ligera',2:'Pesada',3:'Tunica'}[at]
  label=f'{shortpack(key)} {role} {idx+1}'
  if key=='b3-08-saint-seiya-armor':
   torso_refs=' '.join(rows[body['id']][24:304]);match=re.search(r'SaintSeiya([A-Za-z]+)\.',torso_refs)
   label='Saint Seiya '+(match[1] if match else str(idx+1))
  armors.append({'label':label,'category':'SETS','pack':key,'equip':equip,'items':[i['id'] for i in own],'role':role,'sex':'FEMALE' if idx%2 else 'MALE','classId':10 if at==3 else 0});covered.update(i['id'] for i in own)
profiles=armors[:]
for w in weapons:
 if w['id'] in usedweapons:continue
 equip=defaults.copy();equip['equipRHand']=w['id']
 name=clean(w['name']);label=name if len(name)>3 and not name.endswith(str(w['old_id'])) else shortpack(w['pack'])+' '+{'SWORD':'Sword','BLUNT':'Staff' if w['base'] in (6366,6579) else 'Blunt','BOW':'Bow','DAGGER':'Dagger','POLE':'Spear','DUAL':'Dual','DUALFIST':'Fist'}.get(xml[w['id']].find("set[@name='weapon_type']").get('val'),'Weapon')
 profiles.append({'label':label,'category':'ARMAS','pack':w['pack'],'equip':equip,'items':[w['id']],'role':'Arma','sex':'MALE','classId':0});covered.add(w['id'])
# Shields use existing one-handed weapon stands; no incompatible two-handed combination.
free=[p for p in profiles if p['equip']['equipRHand'] and byid[p['equip']['equipRHand']]['bodypart']=='rhand']
for shield in shields:
 p=next((p for p in free if p['pack']==shield['pack'] and not p['equip']['equipLHand']),next((p for p in free if not p['equip']['equipLHand']),None))
 assert p is not None,'Not enough one-handed display stands for shields'
 p['equip']['equipLHand']=shield['id'];p['items'].append(shield['id']);covered.add(shield['id'])
# Expose remaining individual helmets and hair accessories on weapon-only stands.
loose=[i for i in items if i['kind']=='armor' and i['bodypart'] in ('head','hair') and i['id'] not in covered]
free=[p for p in profiles if p['category']=='ARMAS']
for i,p in zip(loose,free):
 p['equip']['equipHead']=0;p['equip'][slots[i['bodypart']]]=i['id'];p['items'].append(i['id']);p['label']=shortpack(i['pack'])+' '+('Casco' if i['bodypart']=='head' else 'Accesorio')+' '+str(i['id']);covered.add(i['id'])
assert len(loose)<=len(free)
reserved=set()
for f in (PROJECT/'server/game/data/stats/npcs').rglob('*.xml'):
 reserved.update(int(e.get('id')) for e in ET.parse(f).getroot().findall('npc'))
assert not reserved.intersection(range(62000,62000+len(profiles)))
# Four concentric arcs within the central square, with clear cardinal corridors.
locations=[]
for radius,count in [(460,32),(635,44),(810,56),(985,68)]:
 for k in range(count):
  angle=2*math.pi*(k+.5)/count
  x=round(81920+radius*math.cos(angle));y=round(148608+radius*math.sin(angle))
  if abs(x-81920)<65 or abs(y-148608)<65:continue
  locations.append((x,y,-3400,round(((angle+math.pi)%(2*math.pi))/(2*math.pi)*65536)%65536))
assert len(profiles)<=len(locations),(len(profiles),len(locations))
nr=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../../xsd/npcs.xsd'})
sr=ET.Element('list',{'enabled':'true','xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../xsd/spawns.xsd'});spawn=ET.SubElement(sr,'spawn',{'name':'EquipmentShowcaseGiran'})
base=ET.parse(PROJECT/'server/game/data/stats/npcs/custom/fpc_passive.xml').getroot().find('npc')
for idx,(p,loc) in enumerate(zip(profiles,locations)):
 p.update(npc_id=62000+idx,x=loc[0],y=loc[1],z=loc[2],heading=loc[3]);n=copy.deepcopy(base);n.set('id',str(p['npc_id']));n.set('name',f'E{idx+1:03d} {clean(p["label"])[:34]}');n.set('title',(p['category']+' | '+shortpack(p['pack']))[:42]);n.set('level','80')
 n.find('race').text='HUMAN';n.find('sex').text=p['sex'];n.find('status').attrib.update({'talkable':'false','undying':'true','attackable':'false','targetable':'true','showName':'true','randomWalk':'false','randomAnimation':'false','canMove':'false'})
 fpc=n.find('fakePlayer');fpc.attrib.clear();fpc.attrib.update({k:str(v) for k,v in p['equip'].items()});fpc.attrib.update({'classId':str(p['classId']),'hair':'0','hairColor':'0','face':'0','nameColor':'16777215','titleColor':str(0x88FFCC if p['category']=='SETS' else 0xFFDD88),'fakePlayerTalkable':'false','weaponEnchantLevel':'0','armorEnchantLevel':'0'})
 ET.SubElement(n,'acquire',{'exp':'0','sp':'0'});nr.append(n)
 ET.SubElement(spawn,'npc',{k:str(v) for k,v in {'id':p['npc_id'],'x':p['x'],'y':p['y'],'z':p['z'],'heading':p['heading'],'respawnDelay':60,'chaseRange':0}.items()})
def write(root,path):
 path.parent.mkdir(parents=True,exist_ok=True);ET.indent(root,space='\t');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
write(nr,OUT/'data/stats/npcs/custom/equipment_showcase.xml');write(sr,OUT/'data/lab/world-spawns/EquipmentShowcase.xml')
report={'count':len(profiles),'armor_stands':len(armors),'weapon_visuals':len(weapons),'shield_visuals':len(shields),'loose_head_hair':len(loose),'profiles':profiles,'duplicate_item_visuals':duplicates,'center':[81920,148608,-3400],'coverage':sorted(covered),'not_visually_equippable':[i['id'] for i in items if i['bodypart'] in ('neck','rear;lear','rfinger;lfinger')],'geodata':'22_22 region absent; positions placed inside central square using existing map and native town coordinates; visual verification pending'}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print({k:v for k,v in report.items() if k not in ('profiles','duplicate_item_visuals','coverage','not_visually_equippable')})
