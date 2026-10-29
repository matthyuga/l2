from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;ROOT=D.parents[1];files=[]
for root in ['server/game','source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
 rel=Path(root)/'data/scripts/custom/GludioSky/GludioSky.java';p=ROOT/rel;s=p.read_text(encoding='utf8')
 anchor='            if(action.equals("dragon proa")||action.equals("vigilia proa"))dx=147400;'
 assert anchor in s
 s=s.replace(anchor,anchor+'''
            else if(action.equals("dragon galeria")||action.equals("vigilia galeria")){dx=146700;dz=12760;}
            else if(action.equals("dragon capitan")||action.equals("vigilia capitan")){dx=145500;dz=12384;}
            else if(action.equals("dragon habitacion")||action.equals("vigilia habitacion"))dx=145650;''')
 s=s.replace('.muelle dragon proa | .muelle para regresar','.muelle dragon proa | .muelle dragon galeria | .muelle dragon capitan | .muelle dragon habitacion')
 s=s.replace('Vigilia del Dragon: nave estacionada. .muelle dragon proa para ver el mascaron; .muelle para regresar.','Vigilia del Dragon V2: nave de clan. Contramaestres para cambiar de cubierta; .muelle para regresar.')
 output={str(rel):s}
 output[str(Path(root)/'data/scripts/custom/GludioSky/VigiliaCrew.java')]=(D/'VigiliaCrew.java').read_text()
 tree=ET.parse(ROOT/root/'data/stats/npcs/custom/pvp_rooms.xml');n=tree.getroot().find('npc');assert n is not None
 n.set('id','902710');n.set('name','Contramaestre');n.set('title','Vigilia del Dragon');n.set('displayId','30146')
 output[str(Path(root)/'data/stats/npcs/custom/vigilia_crew.xml')]='<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(tree.getroot(),encoding='unicode')
 for relative,text in output.items():
  target=ROOT/relative
  if 'VigiliaCrew.java' in relative or 'vigilia_crew.xml' in relative:assert not target.exists(),relative
  q=D/'stage/project'/relative;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text,encoding='utf8')
  files.append(dict(relative=relative,before=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None))
(D/'server-source-hashes.json').write_text(json.dumps(files,indent=2));print('Staged V2 destinations and three steward NPCs in existing GludioSky script folder')
