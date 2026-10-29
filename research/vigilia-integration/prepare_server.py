from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
roots=['server/game','source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game'];files=[]
branch='''        if(action.equals("dragon")||action.startsWith("dragon ")||action.equals("vigilia")||action.startsWith("vigilia "))
        {
            int dx=146500,dy=52000,dz=12056;
            if(action.equals("dragon proa")||action.equals("vigilia proa"))dx=147400;
            else if(!action.equals("dragon")&&!action.equals("vigilia")&&!action.equals("dragon cubierta")&&!action.equals("vigilia cubierta"))
            {player.sendMessage(".muelle dragon | .muelle dragon proa | .muelle para regresar");return true;}
            int floor=GeoEngine.getInstance().getHeight(dx,dy,dz);
            if(Math.abs(floor-dz)>60){player.sendMessage("La cubierta de Vigilia del Dragon no esta disponible. Avisa al administrador.");return true;}
            player.teleToLocation(dx,dy,floor+24,0,0,false);
            player.sendMessage("Vigilia del Dragon: nave estacionada. .muelle dragon proa para ver el mascaron; .muelle para regresar.");
            return true;
        }
'''
zone='''<?xml version="1.0" encoding="UTF-8"?>
<list enabled="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../xsd/zones.xsd">
 <zone name="Vigilia Dragon Peace" type="PeaceZone" shape="Cuboid" minZ="9500" maxZ="16383">
  <node X="144000" Y="50900" /><node X="149100" Y="53100" />
 </zone>
 <zone name="Vigilia Dragon Respawn" type="RespawnZone" shape="Cuboid" minZ="9500" maxZ="16383">
  <node X="144000" Y="50900" /><node X="149100" Y="53100" />
  <race name="HUMAN" point="gludio_sky" /><race name="ELF" point="gludio_sky" /><race name="DARK_ELF" point="gludio_sky" /><race name="ORC" point="gludio_sky" /><race name="DWARF" point="gludio_sky" />
 </zone>
</list>
'''
for root in roots:
 rel=Path(root)/'data/scripts/custom/GludioSky/GludioSky.java';p=ROOT/rel;s=p.read_text(encoding='utf8');assert 'action.equals("dragon")' not in s
 anchor='        if(action.equals("coliseo")';assert anchor in s;s=s.replace(anchor,branch+anchor,1)
 old=next(l.strip() for l in s.splitlines() if l.strip().startswith('if(') and 'player.getX()<145000' in l)
 outside='(player.getX()<144000||player.getX()>149100||player.getY()<50900||player.getY()>53100||player.getZ()<9500)'
 s=s.replace(old,'if(('+old[3:-1]+') && '+outside+')',1)
 s=s.replace('.muelle | .muelle nave | .muelle aurelia | .muelle estado','.muelle | .muelle nave | .muelle aurelia | .muelle dragon | .muelle estado')
 s=s.replace('Resort: .muelle aurelia.','Resort: .muelle aurelia. Dragon: .muelle dragon.')
 q=D/'stage/project'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s,encoding='utf8');files.append(dict(relative=str(rel),before=hashlib.sha256(p.read_bytes()).hexdigest()))
 rel=Path(root)/'data/zones/vigilia_dragon.xml';p=ROOT/rel;assert not p.exists();q=D/'stage/project'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(zone,encoding='utf8');files.append(dict(relative=str(rel),before=None))
(D/'server-source-hashes.json').write_text(json.dumps(files,indent=2));print('Prepared dragon/vigilia commands and peace/respawn zones; Aurelia commands retained.')
