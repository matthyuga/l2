import bpy,json,math
from pathlib import Path
D=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(D.parent/'vigilia-clan-v3/Vigilia-clan-v3.blend'),load_ui=False,use_scripts=False)
materials=[];lines=[];vertices=[];faces=[];vi=0
deps=bpy.context.evaluated_depsgraph_get()
for col in bpy.data.collections:
 if col.name!='01_AERONAVE_EXPORT':continue
 for obj in col.objects:
  if obj.type not in {'MESH','CURVE','FONT'} or obj.name.startswith('Escala_humana'):continue
  e=obj.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles()
  for v in me.vertices:
   p=obj.matrix_world@v.co;vertices.append(tuple(p))
  for t in me.loop_triangles:
   m=me.materials[t.material_index] if me.materials else None
   key=m.name if m else 'Default'
   if key not in [x['name'] for x in materials]:materials.append(dict(name=key,color=list(m.diffuse_color) if m else [1,1,1,1]))
   mi=next(i for i,x in enumerate(materials) if x['name']==key)
   faces.append(([vi+i+1 for i in t.vertices],mi+1))
  vi+=len(me.vertices);e.to_mesh_clear()
for v in vertices:lines.append('v '+' '.join(f'{x:.7f}' for x in v))
for i in range(len(materials)):lines.append(f'vt {(i%8+.5)/8} {(i//8+.5)/8}')
for f,m in faces:lines.append('f '+' '.join(f'{i}/{m}' for i in f))
(D/'HGVigiliaV3.obj').write_text('\n'.join(lines))
(D/'palette.json').write_text(json.dumps(materials,indent=2))
im=bpy.data.images.new('VigiliaAtlas',width=512,height=512,alpha=False)
def srgb(c):return 12.92*c if c<.0031308 else 1.055*c**(1/2.4)-.055
pixels=[]
for y in range(512):
 for x in range(512):
  idx=y//64*8+x//64;c=materials[idx]['color'] if idx<len(materials) else [1,1,1,1]
  pixels.extend([srgb(c[0]),srgb(c[1]),srgb(c[2]),1])
im.pixels=pixels;im.filepath_raw=str(D/'VigiliaAtlas.tga');im.file_format='TARGA_RAW';im.save()
(D/'export-audit.json').write_text(json.dumps(dict(vertices=len(vertices),triangles=len(faces),materials=len(materials)),indent=2))
print('AURELIA_SOURCE_EXPORTED',len(vertices),len(faces))
