from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
roots=['server/game','source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']
files=[]
branch='''        if(action.equals("aurelia")||action.startsWith("aurelia ")||action.equals("resort"))
        {
            int ax=153400,ay=55800,az=12040;
            if(action.equals("aurelia a")){ax=156000;ay=55000;az=11296;}
            else if(action.equals("aurelia b")){ax=156000;ay=55000;az=10792;}
            else if(action.equals("aurelia puente")){ax=151700;ay=55000;az=11664;}
            else if(!action.equals("aurelia")&&!action.equals("aurelia cubierta")&&!action.equals("resort"))
            {player.sendMessage(".muelle aurelia | .muelle aurelia a | .muelle aurelia b | .muelle aurelia puente");return true;}
            int floor=GeoEngine.getInstance().getHeight(ax,ay,az);
            if(Math.abs(floor-az)>80){player.sendMessage("El suelo de Aurelia no esta disponible. Avisa al administrador.");return true;}
            player.teleToLocation(ax,ay,floor+24,0,0,false);
            player.sendMessage("Aurelia: nave resort estacionada. .muelle para regresar. Interiores: .muelle aurelia a / b / puente.");
            return true;
        }
'''
zone='''<?xml version="1.0" encoding="UTF-8"?>
<list enabled="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../xsd/zones.xsd">
 <zone name="Aurelia Resort Peace" type="PeaceZone" shape="Cuboid" minZ="9500" maxZ="16383">
  <node X="149800" Y="51000" /><node X="163200" Y="59000" />
 </zone>
 <zone name="Aurelia Resort Respawn" type="RespawnZone" shape="Cuboid" minZ="9500" maxZ="16383">
  <node X="149800" Y="51000" /><node X="163200" Y="59000" />
  <race name="HUMAN" point="gludio_sky" /><race name="ELF" point="gludio_sky" />
  <race name="DARK_ELF" point="gludio_sky" /><race name="ORC" point="gludio_sky" /><race name="DWARF" point="gludio_sky" />
 </zone>
</list>
'''
for root in roots:
 rel=Path(root)/'data/scripts/custom/GludioSky/GludioSky.java';p=ROOT/rel;s=p.read_text(encoding='utf8')
 assert 'action.equals("aurelia")' not in s,'Already patched'
 anchor='        if(action.equals("coliseo")'
 assert anchor in s;s=s.replace(anchor,branch+anchor,1)
 old='if(player.getX()<145000||player.getX()>154000||player.getY()<44000||player.getY()>50000||player.getZ()<9500)'
 new='if((player.getX()<145000||player.getX()>154000||player.getY()<44000||player.getY()>50000||player.getZ()<9500) && (player.getX()<149800||player.getX()>163200||player.getY()<51000||player.getY()>59000||player.getZ()<9500))'
 assert old in s;s=s.replace(old,new)
 s=s.replace('.muelle | .muelle nave | .muelle estado','.muelle | .muelle nave | .muelle aurelia | .muelle estado')
 s=s.replace('Aeronave: .muelle nave.','Aeronave: .muelle nave. Resort: .muelle aurelia.')
 q=D/'stage/project'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s,encoding='utf8')
 files.append(dict(relative=str(rel),before=hashlib.sha256(p.read_bytes()).hexdigest()))
 rel=Path(root)/'data/zones/aurelia_resort.xml';p=ROOT/rel;assert not p.exists()
 q=D/'stage/project'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(zone,encoding='utf8')
 files.append(dict(relative=str(rel),before=None))
(D/'server-source-hashes.json').write_text(json.dumps(files,indent=2))
print('Staged commands and peace/respawn zones in runtime, source and cloud overlay.')
