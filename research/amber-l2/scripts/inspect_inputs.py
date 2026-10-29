import hashlib
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
vrm = pathlib.Path(r'D:\codex periferico\VSeeFace\CodexAvatars\amber_MVP_001_auto.vrm')
data = vrm.read_bytes()
magic, version, length = struct.unpack_from('<4sII', data)
assert magic == b'glTF' and length == len(data)
json_length, json_type = struct.unpack_from('<II', data, 12)
doc = json.loads(data[20:20+json_length])
report = {
    'source': str(vrm), 'sha256': hashlib.sha256(data).hexdigest(),
    'nodes': len(doc.get('nodes', [])), 'meshes': len(doc.get('meshes', [])),
    'materials': len(doc.get('materials', [])), 'textures': len(doc.get('textures', [])),
    'skins': [{'joints': len(s['joints'])} for s in doc.get('skins', [])],
    'human_bones': doc.get('extensions', {}).get('VRM', {}).get('humanoid', {}).get('humanBones', []),
    'material_properties': doc.get('extensions', {}).get('VRM', {}).get('materialProperties', []),
}
for bone in report['human_bones']:
    bone['name'] = doc['nodes'][bone['node']]['name']
(ROOT / 'reports' / 'amber-vrm-input.json').write_text(json.dumps(report, indent=2), encoding='utf8')
(ROOT / 'exports' / 'amber-source.glb').write_bytes(data)
print(json.dumps({k: v for k, v in report.items() if k not in ('human_bones', 'material_properties')}))
