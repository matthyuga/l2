from pathlib import Path
import urllib.request, json, hashlib, zipfile, shutil
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'verified-download-20261015'
DEST.mkdir(exist_ok=True)
rows=json.loads((ROOT/'downloads.json').read_text(encoding='utf-8-sig'))
records=[]
for row in rows:
    req=urllib.request.Request(row['url'],headers={'User-Agent':'HELLGAMES-source-review'})
    with urllib.request.urlopen(req,timeout=45) as response:b=response.read()
    digest=hashlib.sha256(b).hexdigest()
    if digest!=row['sha256']:raise RuntimeError('Source mismatch: '+row['path'])
    p=DEST/'external/orion'/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    records.append({**row,'verified_again':True})
    print('Verified download',row['path'],flush=True)
license_url='https://raw.githubusercontent.com/Hl4p3x/L2jOrion_Interlude_C6/0daf83956edc9402dda235cd69f97d1d13cb82a7/LICENSE'
with urllib.request.urlopen(urllib.request.Request(license_url,headers={'User-Agent':'HELLGAMES-source-review'}),timeout=45) as response:b=response.read()
(DEST/'external/orion/LICENSE').write_bytes(b)
records.append({'path':'LICENSE','url':license_url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
base=Path('E:/l2-local/source/L2J_Mobius_CT_0_Interlude')
local_paths=['java/org/l2jmobius/gameserver/entity/zone/type/FlagPvPZone.java','java/org/l2jmobius/gameserver/entity/zone/type/ArenaZone.java','java/org/l2jmobius/gameserver/entity/zone/form/ZoneNPoly.java','java/org/l2jmobius/gameserver/taskmanagers/PvpFlagTaskManager.java']
for rel in local_paths:
    src=base/rel
    if not src.exists():continue
    p=DEST/'local-mobius-reference'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
    records.append({'path':'local-mobius-reference/'+rel,'source':str(src),'bytes':src.stat().st_size,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
xml=DEST/'external/orion/L2jOrion_Datapack/game/data/xml/zones/RandomZone.xml'
zones=[]
for zone in ET.parse(xml).getroot().findall('zone'):
    stats={s.attrib['name']:s.attrib['val'] for s in zone.findall('stat')}
    locs=[list(map(int,s.split(','))) for s in stats.get('locs','').split(';') if s.strip()]
    zones.append({'name':zone.attrib['name'],'shape':zone.attrib.get('shape'),'minZ':int(zone.attrib['minZ']),'maxZ':int(zone.attrib['maxZ']),'seconds':int(stats['time']),'autoPvpFlag':stats.get('autoPvpFlag'),'spawns':locs,'polygon':[{k:int(v) for k,v in n.attrib.items()} for n in zone.findall('node')]})
(DEST/'zones.json').write_text(json.dumps(zones,indent=2),encoding='utf-8')
(DEST/'download-manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
readme='''# PvP flag y zonas: paquete para adaptar a HELLGAMES

Descarga verificada 15/10/2026. No instalado ni ejecutado.

external/orion contiene fuentes y configuraciones de L2jOrion Interlude del commit 0daf83956edc9402dda235cd69f97d1d13cb82a7. Incluye auto-flag, reloj y rotacion aleatoria. NO trae votos de siguiente mapa ni la salida vulnerable de cuatro segundos. Necesita adaptacion a Mobius; no copiar como reemplazo del core. Licencia Orion incluida.

local-mobius-reference contiene copias de la infraestructura ya presente en nuestro source. FlagPvPZone es una clase de zona, no un catalogo de mapas. Su salida limpia inmediatamente el flag; necesita coordinarse con nuestra franja vulnerable y el flag previo de combate.

Las zonas de ejemplo no son mapas nuevos: definen contornos y spawns sobre el mundo Interlude. No se descargaron UNR, geodata ni un cliente diferente. zones.json contiene los limites y spawns extraidos del XML sin activarlos.

Zonas incluidas en RandomZone.xml (45 minutos cada una):
'''
for z in zones:readme+='- '+z['name']+'\n'
readme+='''
El XML no incluye Elven ni la playa de Primeval. Se pueden definir para nuestro sistema; no hay obligacion de adoptar estas siete zonas. Elven ya tiene sala local, independiente de este paquete.

El foro Mobius topic11872 (Pvp Flag Zone) devolvio 403 al intentar descargarlo. No se incluye como parche obtenido. Su fragmento indexado menciona Primeval, aplica Noblesse y limpia flag; no es adecuado para instalar directamente siguiendo nuestras reglas.

download-manifest.json conserva URLs, hashes y referencias locales. Los seis archivos previamente adquiridos se volvieron a descargar y coincidieron con sus SHA256. Estos hashes dan trazabilidad, no garantizan compatibilidad ni calidad del codigo.

Siguiente etapa: adaptar flag al controlador de salas conservando estado, preparar configuracion de mapas y votacion al terminar el tiempo. Este paquete es material fuente para esa integracion, no un sistema CS completo listo para instalar.
'''
(DEST/'LEEME.md').write_text(readme,encoding='utf-8')
out=ROOT.parent/'HELLGAMES-PVP-FLAG-fuentes-20261015.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(DEST))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    count=len(z.infolist())
print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'files':count,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zones':[z['name'] for z in zones]},indent=2))
