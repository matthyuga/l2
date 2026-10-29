from pathlib import Path
import json,shutil,datetime,struct,urllib.request
root=Path(r'E:\l2-local');cat=root/'research/model-catalog';path=cat/'gallery.json'
raw=path.read_bytes();g=json.loads(raw)
key='custom_attack_robot'
assert not any(m['key']==key for m in g['models']), 'Robot already exists'
backup=root/'backups'/('attack-robot-catalog-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
(backup/'gallery.json').write_bytes(raw)
m={'key':key,'mesh':'AttackRobot.AttackRobot','package':'AttackRobot','category':'Personalizados','title':'Attack Robot · Robot de ataque','names':['Attack Robot','Robot de ataque','Robot rojo','Criatura mecánica'],'npcs':[],'npc_count':0,'types':['Robot'],'catalog_role':'monster','external_source':True,'native':False,'preview_only':True,'gltf':'exports/attack-robot/attack-robot.glb','thumbnail':'thumbs/custom_attack_robot.png','status':'ready','textured_materials':5,'material_count':5,'batch':'Tanda original','view_bounds':json.loads((root/'research/attack-robot-catalog/view-bounds.json').read_text()),'material_review':{'status':'complete','text':'Cinco texturas completas','missing_slots':[]},'note':'Robot de ataque rojo. Vista 3D en pose fija; esqueleto de 13 huesos, sin animaciones incluidas. Recurso visual externo, todavía sin NPC ni integración dentro de L2. Versión optimizada para el catálogo: 171.782 triángulos y cinco texturas 2K.','source_archive':'descarga de assets/attack-robot.zip'}
g['models'].append(m);g['model_count']=len(g['models'])
assert path.read_bytes()==raw,'Catalog changed during preparation'
path.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
new=json.loads(path.read_text(encoding='utf-8'))
assert new['models'][:-1]==json.loads(raw)['models']
assert len({m['key'] for m in new['models']})==len(new['models'])
b=(cat/m['gltf']).read_bytes();magic,version,total=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and total==len(b)
n,kind=struct.unpack_from('<II',b,12);doc=json.loads(b[20:20+n]);assert len(doc['images'])==5 and len(doc['skins'][0]['joints'])==13 and not doc.get('animations')
assert all('bufferView' in i for i in doc['images'])
report={'models_before':len(new['models'])-1,'models_after':len(new['models']),'existing_entries_unchanged':True,'unique_keys':True,'embedded_images':len(doc['images']),'skin_joints':13,'glb_bytes':len(b),'backup':str(backup),'url':'http://127.0.0.1:32280/?model=custom_attack_robot&view=3d'}
try:
 served=json.load(urllib.request.urlopen('http://127.0.0.1:32280/api/catalog',timeout=5))
 entry=next(i for i in served['models'] if i['key']==key);assert entry['has_thumbnail']
 for f in [m['gltf'],m['thumbnail']]:
  with urllib.request.urlopen('http://127.0.0.1:32280/'+f,timeout=10) as response: assert response.status==200;response.read()
 report['http_catalog_and_assets']='PASS'
except ConnectionRefusedError: report['http_catalog_and_assets']='Service offline'
(root/'research/attack-robot-catalog/verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
