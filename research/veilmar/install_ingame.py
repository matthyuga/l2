"""Back up and install the original Veilmar packages, generated geo and opt-in room."""
import pathlib,shutil,json,re,hashlib,datetime,sys,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar';CLIENT=ROOT.parent/'l2'
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package
sys.path.insert(0,str(D/'geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
assert (CLIENT/'system-hud/L2.exe').exists()
assert (D/'generated-geodata/17_24.l2j').stat().st_size==10964704
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
BACK=ROOT/'backups'/('veilmar-ingame-'+stamp);BACK.mkdir(parents=True)
manifest=dict(date=stamp,backup=str(BACK),files=[],geodata_toolkit_revision=None)
import subprocess
manifest['geodata_toolkit_revision']=subprocess.check_output(['git','-C',str(D/'geodata-toolkit'),'rev-parse','HEAD'],text=True).strip()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,data):
 path=pathlib.Path(path);before=path.exists();saved=None
 if before:
  saved=BACK/('client' if path.is_relative_to(CLIENT) else 'project')/path.relative_to(CLIENT if path.is_relative_to(CLIENT) else ROOT)
  saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
 entry=dict(path=str(path),existed=before,backup=str(saved) if saved else None,before_sha256=digest(path) if before else None)
 manifest['files'].append(entry)
 # Record rollback before each mutation, including new files.
 (BACK/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);entry['after_sha256']=digest(path)
 (BACK/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for folder,name in [('maps','17_24.unr'),('animations','Veilmar_A.ukx'),('staticmeshes','Veilmar_S.usx'),('textures','Veilmar_T.utx'),('sounds','Veilmar_SND.uax')]:
 source=D/'assets'/folder/name;write(CLIENT/folder/name,source.read_bytes())
write(ROOT/'server/game/data/geodata/17_24.l2j',(D/'generated-geodata/17_24.l2j').read_bytes())
pkg=Package(D/'assets/maps/17_24.unr');movers={pkg.props(e)['L2ServerObjectRealID']:pkg.props(e) for e in pkg.exports if pkg.ref(e['cl'])=='Engine.Mover'}
lib=MeshLibrary(str(D/'assets/staticmeshes'));door_lines=[];door_ids=[];door_audit=[]
for line in (D/'assets/doors info raw data.txt').read_text().splitlines():
 if not line.startswith('door_begin'):continue
 ident=int(re.search(r'object_id\s*=\s*(\d+)',line)[1]);p=movers[ident]
 pos=list(map(int,re.search(r'pos=\{([^}]+)\}',line)[1].split(';')))
 nodes=[list(map(int,v.split(';'))) for v in re.findall(r'\{(-?\d+;-?\d+;-?\d+)\}',line)[1:]]
 assert len(nodes)==4 and max(abs(a-b) for a,b in zip(pos,p['Location']))<2
 verts,tris=lib.get('Veilmar_S',p['StaticMesh'].split('.')[-1])
 assert verts,p['StaticMesh']
 matrix=actor_matrix(p.get('Rotation'),p.get('DrawScale'),p.get('DrawScale3D'))
 world=transform(verts,matrix,p['Location']);lo=min(v[2] for v in world);hi=max(v[2] for v in world)
 height=max(64,int(hi-lo+1));nodez=int(lo)
 attributes=dict(id=str(ident),name='veilmar_'+str(ident),open_method='1',height=str(height),baseHpMax='1000000',hp_showable='false',basePDef='644',baseMDef='518',pos=','.join(map(str,pos)),nodeZ=str(nodez),default_status='open')
 attributes.update({f'node{i+1}':','.join(map(str,n[:2])) for i,n in enumerate(nodes)})
 element=ET.Element('door',attributes);door_lines.append('\t'+ET.tostring(element,encoding='unicode'));door_ids.append(ident)
 door_audit.append(dict(id=ident,mover=p['StaticMesh'],height=height,nodeZ=nodez,pos=pos))
assert len(door_ids)==26 and len(set(door_ids))==26
instance='''<?xml version="1.0" encoding="UTF-8"?>
<instance id="3052" allowRandomWalk="false" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../xsd/instance.xsd">
 <activityTime val="1440" />
 <allowSummon val="true" />
 <emptyDestroyTime val="5" />
 <PvPInstance val="true" />
 <spawnPoints startPosType="FIXED"><Location x="-78552" y="212264" z="-2584" /></spawnPoints>
 <exitPoint x="83425" y="148585" z="-3406" />
 <doorlist>
'''+''.join(f'  <door id="{i}" />\n' for i in door_ids)+''' </doorlist>
</instance>
'''
for base in [ROOT/'server/game',ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
 doors=base/'data/Doors.xml'
 if not doors.exists():continue
 text=doors.read_text(encoding='utf-8');existing={int(e.attrib['id']) for e in ET.fromstring(text).findall('door')}
 assert not set(door_ids)&existing,'Veilmar door IDs already installed; review previous manifest instead of overwriting.'
 text=text.replace('</list>','\n\t<!-- Veilmar original movers: native IDs and mesh-derived collision heights. -->\n'+'\n'.join(door_lines)+'\n</list>')
 write(doors,text.encode('utf-8'))
 write(base/'data/instances/custom/veilmar_pvp.xml',instance.encode('utf-8'))
 write(base/'data/scripts/custom/VeilmarPvp/VeilmarPvp.java',(D/'VeilmarPvp.java').read_bytes())
 config=base/'config/Custom/WorldContent.ini'
 if config.exists():
  text=config.read_text(encoding='utf-8');text=re.sub(r'(?m)^(CustomScriptFolders\s*=\s*)([^\r\n]+)',lambda m:m[1]+m[2]+';VeilmarPvp',text)
  write(config,text.encode('utf-8'))
(D/'doors-conversion-audit.json').write_text(json.dumps(door_audit,indent=2))
(D/'installation.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(backup=str(BACK),installed_files=len(manifest['files']),doors=len(door_ids)),indent=2))
