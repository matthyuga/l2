import bpy,json,pathlib
D=pathlib.Path(r'E:/l2-local/research/airships/external-downloads/fantasy-steampunk-airship');bpy.ops.wm.open_mainfile(filepath=str(D/'airship-probe-optimized.blend'),load_ui=False,use_scripts=False)
p={}
for o in bpy.context.scene.objects:
 if o.type=='MESH':p[o.name]=[(u.name,u.active_render,u.active) for u in o.data.uv_layers]
for m in bpy.data.materials:
 if m.use_nodes:
  p[m.name]=dict(uv_nodes=[(n.type,getattr(n,'uv_map','')) for n in m.node_tree.nodes if n.type in ('UVMAP','TEX_COORD')],links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
pathlib.Path(r'E:/l2-local/research/airship-integration/source-material-links.json').write_text(json.dumps(p,indent=2))
