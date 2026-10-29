"""Read existing baseline metadata and list native packages without modifying client/server."""
from pathlib import Path
import csv, json, re, subprocess, collections, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CLIENT = ROOT.parent/'l2'
baseline = json.loads((ROOT/'research/amber-l2/reports/npcgrp-parsed.json').read_text(encoding='utf-8'))
templates = {}
for p in (ROOT/'server/game/data/stats/npcs').rglob('*.xml'):
    for n in ET.parse(p).getroot().iter('npc'):
        if n.get('id'):
            templates[int(n.get('id'))] = {'name':n.get('name',''), 'type':n.get('type','')}
groups = collections.defaultdict(list)
for row in baseline['rows']:
    mesh = row['mesh_name'].strip()
    if mesh:
        npc_id = row['npc_id']
        texture = [x['param_texture_name'] for x in row.get('texture_name_items', [])]
        groups[mesh].append({'id':npc_id, **templates.get(npc_id,{}), 'textures':texture})
models = [{'mesh':mesh, 'package':mesh.split('.')[0], 'npc_count':len(rows),
           'texture_variants':len({tuple(x['textures']) for x in rows}), 'npcs':rows}
          for mesh,rows in sorted(groups.items())]
assets = []
for package in ['LineageMonsters','LineageMonsters2','LineageMonsters3','LineageNpcs','LineageNPCs2','lineagenpcsev']:
    result = subprocess.run([str(ROOT/'research/amber-l2/tools/umodel.exe'), '-list','-game=l2','-path='+str(CLIENT),package+'.ukx'],capture_output=True,text=True,errors='replace',check=True)
    (OUT/(package+'.list.txt')).write_text(result.stdout,encoding='utf-8')
    meshes = re.findall(r'^\s*\d+\s+[0-9A-F]+\s+[0-9A-F]+\s+SkeletalMesh\s+(\S+)\s*$',result.stdout,re.M)
    assets.append({'package':package,'skeletal_mesh_count':len(meshes),'meshes':meshes})
report = {'source':'Existing original Interlude npcgrp baseline; custom client rows and playable race/armor packages excluded.',
          'npc_rows':baseline['count'], 'distinct_nonempty_mesh_references':len(models),
          'server_xml_templates':len(templates), 'native_packages':assets, 'models':models}
(OUT/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'modelos-npc.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer = csv.writer(f,delimiter=';')
    writer.writerow(['Malla','Paquete','NPC asociados','Variantes de texturas','Ejemplos de nombres','Ejemplos de IDs','Tipos'])
    for m in models:
        names = list(dict.fromkeys(x.get('name','') for x in m['npcs'] if x.get('name')))
        types = sorted({x.get('type','') for x in m['npcs'] if x.get('type')})
        writer.writerow([m['mesh'],m['package'],m['npc_count'],m['texture_variants'],', '.join(names[:8]),
                         ', '.join(str(x['id']) for x in m['npcs'][:12]),', '.join(types)])
print(json.dumps({'baseline_npc_rows':baseline['count'],'distinct_nonempty_mesh_references':len(models),
                  'server_xml_templates':len(templates),'package_counts':[{k:v for k,v in p.items() if k!='meshes'} for p in assets]}))
