from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,collections
base=Path(__file__).resolve().parent
zones=json.loads((base/'zones.json').read_text(encoding='utf8'))
out=base/'server/custom/ExplorationWalking';out.mkdir(parents=True,exist_ok=True)
root=E.Element('nativeZones',dict(version='1',source='ZoneName-e.dat; l2zonename.utx',tileSize='32768',maskSize='128'))
for r in zones:
    E.SubElement(root,'zone',dict(record=str(r['id']),id=hashlib.sha256(r['name'].encode()).hexdigest()[:16],name=r['name'],color=str(r['color']),tileX=str(r['map_x']),tileY=str(r['map_y']),bottom=str(r['bottom']),top=str(r['top'])))
E.indent(root);(out/'native-zones.xml').write_bytes(E.tostring(root,encoding='utf-8',xml_declaration=True))
(out/'zone-masks.bin').write_bytes((base/'zone-masks.bin').read_bytes())
inventory=json.loads((base/'mask-inventory.json').read_text());tiles={(t['x'],t['y']):set(t['colors']) for t in inventory}
reach=[];unreferenced=[]
for r in zones:
    present=any(r['color'] in s for s in tiles.values()) if r['color']<200 else r['color'] in tiles.get((r['map_x'],r['map_y']),set())
    (reach if present else unreferenced).append(r)
report=dict(records=len(zones),names=len({z['name'] for z in zones}),masks=len(tiles),mask_referenced_records=len(reach),mask_referenced_names=len({z['name'] for z in reach}),unreferenced_records=unreferenced,
            inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('E:/l2/system-hud/ZoneName-e.dat'),Path('E:/l2/system-hud/huntingzone-e.dat'),Path('E:/l2/systextures/l2zonename.utx')]})
inactive=[r for r in reach if int(r['bottom']//1)+1>=r['top']]
active=[r for r in reach if r not in inactive]
report.update(inactive_height_records=inactive,active_records=len(active),active_names=len({r['name'] for r in active}))
(base/'coverage.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print({k:v for k,v in report.items() if k not in ['inputs','unreferenced_records']})
