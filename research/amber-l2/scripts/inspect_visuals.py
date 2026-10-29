import bpy, json, pathlib
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'exports/amber-imported.blend'))
report=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name not in {'Body.baked','Outfit 00.baked'}: continue
    entry={'object':o.name,'shape_keys':[(k.name,k.value) for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [],'materials':[]}
    for i,m in enumerate(o.data.materials):
        polygons=[p for p in o.data.polygons if p.material_index==i]
        uv=[o.data.uv_layers.active.data[j].uv[:] for p in polygons for j in p.loop_indices]
        entry['materials'].append({'index':i,'name':m.name,'faces':len(polygons),'blend':m.blend_method,
          'uv_min':[min(x[a] for x in uv) for a in range(2)] if uv else [],'uv_max':[max(x[a] for x in uv) for a in range(2)] if uv else [],
          'nodes':[(n.name,n.type, n.image.name if n.type=='TEX_IMAGE' and n.image else '') for n in m.node_tree.nodes],
          'mapping':{n.name:{s.name:list(s.default_value) for s in n.inputs if s.name in ('Location','Rotation','Scale')} for n in m.node_tree.nodes if n.type=='MAPPING'},
          'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]})
    report.append(entry)
(R/'reports/visual-inputs.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('VISUAL_INPUTS',json.dumps([(x['object'],[(n,v) for n,v in x['shape_keys'] if v!=0],[(m['name'],m['faces'],m['uv_min'],m['uv_max']) for m in x['materials']]) for x in report]))
import sys
sys.path.insert(0,str(R/'tools/psk_addon'))
from io_scene_psk_psa.psa.reader import PsaReader
reader=PsaReader(str(R/'exports/npc-reference/LineageNpcs/MeshAnimation/a_traderB_FHuman_anim.psa'))
print('NPC_SEQUENCES',list(reader.sequences))
print('MAPPING_NODES',[(m['name'],m['mapping']) for e in report for m in e['materials']])
import struct
for relative in ('AmberNPC.psk','npc-reference/LineageNpcs/SkeletalMesh/a_traderB_FHuman_m00.psk','l2-reference/Fighter/SkeletalMesh/FFighter_m001_u.psk'):
    d=(R/'exports'/relative).read_bytes(); position=0
    while position<len(d):
        n,k,s,c=struct.unpack_from('<20siii',d,position); position+=32
        if n.startswith(b'PNTS'):
            pts=list(struct.iter_unpack('<fff',d[position:position+s*c]))
            print('BOUNDS',relative,[(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)])
        position+=s*c
