import pathlib,hashlib,re,json
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];live=ROOT/'server/game';stage=D/'stage/server';hashes=[]
rel='data/scripts/custom/GludioSky/GludioSky.java';p=live/rel;text=p.read_text();assert 'action.equals("nave")' not in text
text=text.replace('151000','154000')
branch='''        if(action.equals("nave")||action.equals("barco"))
        {
            int floor=GeoEngine.getInstance().getHeight(152000,46700,12040);
            if(Math.abs(floor-12040)>100){player.sendMessage("La cubierta de la aeronave no esta disponible.");return true;}
            player.teleToLocation(152000,46700,floor+24,0,0,false);
            player.sendMessage("Aeronave en pruebas, estacionada. .muelle para volver al muelle; .muelle coliseo para bajar.");
            return true;
        }
'''
text=text.replace('        if(action.equals("coliseo")',branch+'        if(action.equals("coliseo")')
text=text.replace('.muelle | .muelle estado | .muelle coliseo','.muelle | .muelle nave | .muelle estado | .muelle coliseo')
text=text.replace('New characters arrive at the floating dock.','New characters arrive at the floating dock; .muelle nave reaches the docked airship.')
text=text.replace('Destino del muelle: 149000,46700,12021. .muelle para subir; .muelle coliseo para bajar.','Muelle: 149000,46700,12021. Aeronave: .muelle nave. .muelle para regresar; .muelle coliseo para bajar.')
q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text);hashes.append(dict(relative=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
rel='data/zones/gludio_sky.xml';p=live/rel;text=p.read_text();assert '151000' in text;text=text.replace('151000','154000');q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text);hashes.append(dict(relative=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(D/'server-source-hashes.json').write_text(json.dumps(hashes,indent=2));print('Staged .muelle nave and matching peace/respawn extent; new-character spawn unchanged.')
