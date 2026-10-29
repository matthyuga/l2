bl_info={'name':'Nexus L2 Animation Lab','author':'Nexus','version':(0,2,0),'blender':(3,5,0),'category':'Animation'}
import bpy,json,sys,subprocess,os
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty,FloatProperty,IntProperty,BoolProperty,PointerProperty,EnumProperty
ROOT=Path(__file__).parent
ADDON=ROOT.parent/'research/amber-l2/tools/psk_addon'
WRITER=ROOT.parent/'research/dust2-animation-study/native/write_l2_animation.py'
PSK=ROOT.parent/'research/amber-l2/exports/l2-reference/Fighter/SkeletalMesh/FFighter_m001_u.psk'
def rig(context):
 r=context.scene.nl2.rig
 if not r or r.type!='ARMATURE':raise ValueError('Selecciona el esqueleto en el panel')
 if r.constraints or any(p.constraints for p in r.pose.bones):raise ValueError('Hornea las restricciones antes de mezclar este rig')
 return r
def region(n):
 s=n.lower()
 if s=='bip01':return 'root'
 if any(t in s for t in ['pelvis','pony','skirt']):return 'pelvis'
 if any(t in s for t in ['thigh','calf','foot','toe']):return 'legs'
 if any(t in s for t in ['head','neck']):return 'head'
 if any(t in s for t in ['clavicle','upperarm','forearm','hand','finger']):return 'left' if '_l_' in s else 'right'
 if 'spine' in s:return 'torso'
 return 'other'
def sample(action,r,frame):
 r.animation_data.action=action
 for p in r.pose.bones:p.matrix_basis.identity()
 bpy.context.scene.frame_set(int(frame),subframe=frame%1)
 bpy.context.view_layer.update()
 return {p.name:p.matrix_basis.copy() for p in r.pose.bones}
def frame_at(action,t,speed,offset,loop):
 lo,hi=action.frame_range;span=max(1,hi-lo+1);f=lo+t*speed+offset
 return lo+(f-lo)%span if loop else max(lo,min(hi,f))
def mix(context):
 s=context.scene.nl2;r=rig(context);r.animation_data_create();a=bpy.data.actions.get(s.base);b=bpy.data.actions.get(s.overlay)
 if not a or not b:raise ValueError('Elige una animacion base y otra superior')
 known=set(r.pose.bones.keys())
 for action in [a,b]:
  used={fc.data_path.split('"')[1] for fc in action.fcurves if fc.data_path.startswith('pose.bones["')}
  if not used or not used.issubset(known):raise ValueError('La animacion no coincide con los huesos del rig')
 if r.animation_data.nla_tracks:raise ValueError('Desactiva/retira las pistas NLA antes de usar este mezclador')
 selected={p.name for p in r.pose.bones if p.bone.select}
 if s.only_selected and not selected:raise ValueError('Selecciona huesos en modo Pose para la mascara manual')
 name=bpy.path.clean_name(s.output_name) or 'Mezcla';action=bpy.data.actions.new(name);action.use_fake_user=True
 weights={k:getattr(s,k) for k in ['pelvis','legs','torso','head','left','right','other']};frames=[]
 oldaction=r.animation_data.action;oldframe=context.scene.frame_current
 try:
  first=sample(a,r,float(a.frame_range[0]));root=first.get('Bip01')
  for i in range(s.length):
   pa=sample(a,r,frame_at(a,i,s.base_speed,s.base_offset,s.loop));pb=sample(b,r,frame_at(b,i,s.overlay_speed,s.overlay_offset,s.loop));out={}
   for p in r.pose.bones:
    key=region(p.name);weight=0 if key=='root' else weights[key]
    if s.only_selected and p.name not in selected:weight=0
    if s.lock_pelvis and key in ['pelvis','legs']:weight=0
    la,qa,sa=pa[p.name].decompose();lb,qb,sb=pb[p.name].decompose()
    q=qa.slerp(qb,weight);loc=la.lerp(lb,weight);scale=sa.lerp(sb,weight)
    if key=='root' and s.fixed_root and root:loc,qa,scale=root.decompose();q=qa
    out[p.name]=(loc.copy(),q.copy(),scale.copy())
   frames.append(out)
  r.animation_data.action=action
  for i,poses in enumerate(frames,1):
   for p in r.pose.bones:
    loc,q,scale=poses[p.name];p.rotation_mode='QUATERNION';p.location=loc;p.rotation_quaternion=q;p.scale=scale
    p.keyframe_insert('location',frame=i);p.keyframe_insert('rotation_quaternion',frame=i);p.keyframe_insert('scale',frame=i)
  for fc in action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
  recipe={k:getattr(s,k) for k in ['base','overlay','length','base_speed','overlay_speed','base_offset','overlay_offset','loop','lock_pelvis','fixed_root','only_selected',*weights]};recipe['selected_bones']=sorted(selected) if s.only_selected else [];recipe['rig_bones']=list(known)
  action['nexus_recipe']=json.dumps(recipe,ensure_ascii=False);s.result=action.name
  context.scene.frame_start=1;context.scene.frame_end=s.length;context.scene.frame_set(1)
  return action
 except:
  r.animation_data.action=oldaction;context.scene.frame_set(oldframe);bpy.data.actions.remove(action);raise
class NL2Settings(bpy.types.PropertyGroup):
 advanced:BoolProperty(name='Mostrar ajustes avanzados',default=False)
 model_label:StringProperty(name='Modelo',default='Fighter mujer de ejemplo')
 status:StringProperty(default='Elige base y capa, despues genera una mezcla')

 rig:PointerProperty(type=bpy.types.Object,poll=lambda self,o:o.type=='ARMATURE')
 base:StringProperty(name='Base')
 overlay:StringProperty(name='Capa superior')
 result:StringProperty(name='Resultado')
 output_name:StringProperty(name='Nombre',default='Montura_Conjuro')
 length:IntProperty(name='Fotogramas',default=120,min=2,max=1800)
 base_speed:FloatProperty(name='Velocidad base',default=1,min=.05,max=4)
 overlay_speed:FloatProperty(name='Velocidad superior',default=1,min=.05,max=4)
 base_offset:FloatProperty(name='Desfase base',default=0,min=-1800,max=1800)
 overlay_offset:FloatProperty(name='Desfase superior',default=0,min=-1800,max=1800)
 loop:BoolProperty(name='Repetir clips al mezclarlos',default=True)
 fixed_root:BoolProperty(name='Fijar raiz al inicio de la base',default=True)
 lock_pelvis:BoolProperty(name='Conservar pelvis y piernas de la base',default=True)
 only_selected:BoolProperty(name='Aplicar capa solo a huesos seleccionados',default=False)
 pelvis:FloatProperty(name='Pelvis',default=0,min=0,max=1,subtype='FACTOR')
 legs:FloatProperty(name='Piernas',default=0,min=0,max=1,subtype='FACTOR')
 torso:FloatProperty(name='Torso',default=.6,min=0,max=1,subtype='FACTOR')
 head:FloatProperty(name='Cabeza',default=.5,min=0,max=1,subtype='FACTOR')
 left:FloatProperty(name='Brazo izquierdo',default=1,min=0,max=1,subtype='FACTOR')
 right:FloatProperty(name='Brazo derecho',default=1,min=0,max=1,subtype='FACTOR')
 other:FloatProperty(name='Otros huesos',default=0,min=0,max=1,subtype='FACTOR')
def focus_model(context):
 r=rig(context)
 bpy.ops.object.select_all(action='DESELECT')
 related=[o for o in context.scene.objects if o==r or (o.type=='MESH' and any(m.type=='ARMATURE' and m.object==r for m in o.modifiers))]
 for o in related:o.hide_set(False);o.select_set(True)
 context.view_layer.objects.active=r
 for area in context.screen.areas if context.screen else []:
  if area.type=='VIEW_3D':
   with context.temp_override(area=area,region=next(x for x in area.regions if x.type=='WINDOW')):bpy.ops.view3d.view_selected(use_all_regions=False)
def reference_signature():
 d=json.loads((ROOT.parent/'research/dust2-animation-study/retarget/rig-inventory.json').read_text())['l2'][0]['bones']
 return {x['name']:x['parent'] for x in d}
def validate_rig(r):
 expected=reference_signature();got={b.name:b.parent.name if b.parent else None for b in r.data.bones}
 if got!=expected:raise ValueError('Este modelo necesita adaptar su esqueleto. Esta version mezcla Fighter mujer (76 huesos); cargar no convierte otras razas automaticamente')
class NL2Focus(bpy.types.Operator):
 bl_idname='nl2.focus';bl_label='Centrar modelo'
 def execute(self,context):
  try:focus_model(context);return {'FINISHED'}
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
class NL2LoadModel(bpy.types.Operator,ImportHelper):
 bl_idname='nl2.load_model';bl_label='Cargar modelo';bl_options={'REGISTER','UNDO'}
 filter_glob:StringProperty(default='*.psk;*.fbx;*.glb;*.gltf;*.blend',options={'HIDDEN'})
 def execute(self,context):
  before=set(bpy.data.objects);actions=set(bpy.data.actions);oldrig=context.scene.nl2.rig
  try:
   ext=Path(self.filepath).suffix.lower()
   if ext=='.psk':bpy.ops.import_scene.psk(filepath=self.filepath)
   elif ext=='.fbx':bpy.ops.import_scene.fbx(filepath=self.filepath)
   elif ext in ['.glb','.gltf']:bpy.ops.import_scene.gltf(filepath=self.filepath)
   elif ext=='.blend':
    with bpy.data.libraries.load(self.filepath,link=False) as (src,dst):dst.objects=list(src.objects)
    for o in dst.objects:
     if o:context.collection.objects.link(o)
   else:raise ValueError('Formato de modelo no admitido')
   objects=set(bpy.data.objects)-before;rigs=[o for o in objects if o.type=='ARMATURE']
   if len(rigs)!=1:raise ValueError('El archivo debe contener exactamente un esqueleto; para objetos sin rig usa Cargar objeto / montura')
   r=rigs[0];validate_rig(r)
   for o in before:
    if o==oldrig or (o.type=='MESH' and any(m.type=='ARMATURE' and m.object==oldrig for m in o.modifiers)):o.hide_set(True)
   context.scene.nl2.rig=r;context.scene.nl2.model_label=Path(self.filepath).name;context.scene.nl2.result=''
   context.scene.nl2.status='Modelo compatible cargado. Elige sus animaciones.'
   focus_model(context);return {'FINISHED'}
  except Exception as e:
   for o in set(bpy.data.objects)-before:bpy.data.objects.remove(o,do_unlink=True)
   for a in set(bpy.data.actions)-actions:
    if not a.users:bpy.data.actions.remove(a)
   self.report({'ERROR'},str(e));return {'CANCELLED'}
class NL2LoadProp(bpy.types.Operator,ImportHelper):
 bl_idname='nl2.load_prop';bl_label='Cargar objeto / montura de referencia';bl_options={'REGISTER','UNDO'}
 filter_glob:StringProperty(default='*.obj;*.glb;*.gltf;*.fbx;*.blend',options={'HIDDEN'})
 def execute(self,context):
  try:
   ext=Path(self.filepath).suffix.lower()
   if ext=='.obj':bpy.ops.import_scene.obj(filepath=self.filepath)
   elif ext=='.fbx':bpy.ops.import_scene.fbx(filepath=self.filepath)
   elif ext in ['.glb','.gltf']:bpy.ops.import_scene.gltf(filepath=self.filepath)
   elif ext=='.blend':
    with bpy.data.libraries.load(self.filepath,link=False) as (src,dst):dst.objects=list(src.objects)
    for o in dst.objects:
     if o:context.collection.objects.link(o)
   else:raise ValueError('Formato de referencia no admitido')
   context.scene.nl2.status='Referencia cargada: ajusta posicion, giro y escala en la vista3D';return {'FINISHED'}
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
class NL2LoadMotion(bpy.types.Operator,ImportHelper):
 bl_idname='nl2.load_motion';bl_label='Cargar animaciones';bl_options={'REGISTER','UNDO'}
 filter_glob:StringProperty(default='*.psa;*.blend',options={'HIDDEN'})
 def execute(self,context):
  before=set(bpy.data.actions);old=None;r=None
  try:
   r=rig(context);validate_rig(r);r.animation_data_create();old=r.animation_data.action
   ext=Path(self.filepath).suffix.lower()
   if ext=='.psa':
    from io_scene_psk_psa.psa.reader import PsaReader
    from io_scene_psk_psa.psa.importer import import_psa,PsaImportOptions
    reader=PsaReader(self.filepath)
    source={b.name.decode('cp1252').rstrip('\0') for b in reader.bones}
    if source!=set(r.pose.bones.keys()):raise ValueError('Los huesos del PSA no coinciden con este modelo. Primero hay que adaptar el movimiento')
    options=PsaImportOptions();options.should_use_fake_user=True;options.sequence_names=list(reader.sequences);import_psa(context,reader,r,options)
   elif ext=='.blend':
    with bpy.data.libraries.load(self.filepath,link=False) as (src,dst):dst.actions=list(src.actions)
   else:raise ValueError('Carga PSA o acciones de un archivo Blender. Clips Unity/Koikatsu requieren extraccion y adaptacion previa')
   added=list(set(bpy.data.actions)-before);known=set(r.pose.bones.keys());valid=[]
   for a in added:
    used={fc.data_path.split('"')[1] for fc in a.fcurves if fc.data_path.startswith('pose.bones["')}
    if used and used.issubset(known):a.use_fake_user=True;valid.append(a)
    else:bpy.data.actions.remove(a)
   if not valid:raise ValueError('No se encontro ninguna animacion compatible')
   if not context.scene.nl2.base:context.scene.nl2.base=valid[0].name
   context.scene.nl2.overlay=valid[0].name;context.scene.nl2.status=str(len(valid))+' animaciones cargadas; elige cual quieres usar'
   self.report({'INFO'},context.scene.nl2.status);return {'FINISHED'}
  except Exception as e:
   if r and r.animation_data:r.animation_data.action=old
   for a in set(bpy.data.actions)-before:bpy.data.actions.remove(a)
   self.report({'ERROR'},str(e));return {'CANCELLED'}
  finally:
   if r and r.animation_data:r.animation_data.action=old
class NL2Preview(bpy.types.Operator):
 bl_idname='nl2.preview';bl_label='Ver animacion'
 which:EnumProperty(items=[('base','Base',''),('overlay','Capa',''),('result','Resultado','')])
 def execute(self,context):
  try:
   r=rig(context);a=bpy.data.actions.get(getattr(context.scene.nl2,self.which))
   if not a:raise ValueError('Primero elige una animacion')
   r.animation_data_create();r.animation_data.action=a;context.scene.frame_start=int(a.frame_range[0]);context.scene.frame_end=int(a.frame_range[1]);context.scene.frame_set(context.scene.frame_start);focus_model(context)
   context.scene.nl2.status='Viendo '+a.name+'; pulsa Reproducir para animarla';return {'FINISHED'}
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}

class NL2Preset(bpy.types.Operator):
 bl_idname='nl2.preset';bl_label='Elegir partes';bl_options={'REGISTER','UNDO'}
 kind:EnumProperty(items=[('ARMS','Solo brazos',''),('UPPER','Torso y brazos',''),('ALL','Cuerpo completo',''),('LEGS','Solo piernas','')])
 def execute(self,context):
  s=context.scene.nl2
  for k in ['pelvis','legs','torso','head','left','right','other']:setattr(s,k,0.)
  for k in {'ARMS':['left','right'],'UPPER':['torso','head','left','right'],'ALL':['pelvis','legs','torso','head','left','right','other'],'LEGS':['pelvis','legs']}[self.kind]:setattr(s,k,1.)
  s.lock_pelvis=self.kind in ['ARMS','UPPER'];s.only_selected=False;s.status='Partes elegidas. Genera la mezcla para verla.';return {'FINISHED'}

class NL2Mix(bpy.types.Operator):
 bl_idname='nl2.mix';bl_label='Generar mezcla y previsualizar';bl_options={'REGISTER','UNDO'}
 def execute(self,context):
  try:a=mix(context);self.report({'INFO'},'Mezcla creada: '+a.name);return {'FINISHED'}
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
class NL2Recipe(bpy.types.Operator):
 bl_idname='nl2.recipe';bl_label='Cargar receta del resultado'
 def execute(self,context):
  try:
   s=context.scene.nl2;a=bpy.data.actions.get(s.result)
   if not a or 'nexus_recipe' not in a:raise ValueError('El resultado no contiene receta')
   data=json.loads(a['nexus_recipe'])
   for k,v in data.items():
    if hasattr(s,k):setattr(s,k,v)
   for p in rig(context).pose.bones:p.bone.select=p.name in data.get('selected_bones',[])
   return {'FINISHED'}
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
class NL2Play(bpy.types.Operator):
 bl_idname='nl2.play';bl_label='Reproducir / Pausar'
 def execute(self,context):bpy.ops.screen.animation_play();return {'FINISHED'}
class NL2Export(bpy.types.Operator):
 bl_idname='nl2.export';bl_label='Exportar PSA + UKX + receta'
 def execute(self,context):
  try:
   s=context.scene.nl2;r=rig(context);a=bpy.data.actions.get(s.result)
   if not a or 'nexus_recipe' not in a:raise ValueError('Genera una mezcla antes de exportar')
   target=ROOT/'exports'/bpy.path.clean_name(a.name)
   if target.exists():raise ValueError('Ya existe esa exportacion. Genera otra mezcla con nombre nuevo')
   target.mkdir(parents=True)
   if str(ADDON) not in sys.path:sys.path.insert(0,str(ADDON))
   from io_scene_psk_psa.psa.builder import build_psa,PsaBuildOptions,PsaBuildSequence
   from io_scene_psk_psa.psa.writer import write_psa
   oldactive=context.view_layer.objects.active;oldaction=r.animation_data.action;context.view_layer.objects.active=r
   try:
    opt=PsaBuildOptions();opt.animation_data=r.animation_data;seq=PsaBuildSequence();seq.name=a.name;seq.nla_state.action=a;seq.nla_state.frame_start=int(a.frame_range[0]);seq.nla_state.frame_end=int(a.frame_range[1]);seq.fps=context.scene.render.fps/context.scene.render.fps_base;opt.sequences=[seq]
    psa=target/(a.name+'.psa');write_psa(build_psa(context,opt),str(psa))
   finally:context.view_layer.objects.active=oldactive;r.animation_data.action=oldaction
   recipe=json.loads(a['nexus_recipe']);(target/'recipe.json').write_text(json.dumps(recipe,indent=2,ensure_ascii=False),encoding='utf8')
   # Use existing standalone writer; export only, never install into game.
   command=[r'C:\Users\KEVIN\AppData\Local\Programs\Python\Python310\python.exe',str(WRITER),str(psa),str(target/(a.name+'.ukx')),'--skeleton',str(PSK),'--name',a.name]
   import shutil
   if not Path(command[0]).exists():command[0]=shutil.which('python') or 'python'
   p=subprocess.run(command,capture_output=True,text=True,timeout=60,creationflags=0x08000000 if os.name=='nt' else 0)
   (target/'export-log.txt').write_text(p.stdout+p.stderr,encoding='utf8')
   if p.returncode:raise ValueError('PSA/receta guardados; UKX fallo. Ver export-log.txt')
   self.report({'INFO'},'Exportado en '+str(target));return {'FINISHED'}
  except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}
class NL2Panel(bpy.types.Panel):
 bl_label='Editor de animaciones L2';bl_idname='NL2_PT_MAIN';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Nexus L2'
 def draw(self,context):
  l=self.layout;s=context.scene.nl2
  box=l.box();box.label(text='1. Modelo',icon='OUTLINER_OB_ARMATURE');box.operator('nl2.load_model',icon='FILE_FOLDER');box.label(text=s.model_label);box.operator('nl2.focus',icon='VIEWZOOM');box.operator('nl2.load_prop',icon='OUTLINER_OB_MESH')
  box=l.box();box.label(text='2. Animaciones',icon='ACTION');box.operator('nl2.load_motion',icon='FILE_FOLDER');box.label(text='Base: movimiento que conservas');box.prop_search(s,'base',bpy.data,'actions',text='Base');box.label(text='Capa: movimiento que agregas');box.prop_search(s,'overlay',bpy.data,'actions',text='Capa');row=box.row(align=True);row.operator('nl2.preview',text='Ver base',icon='HIDE_OFF').which='base';row.operator('nl2.preview',text='Ver capa',icon='HIDE_OFF').which='overlay'
  box=l.box();box.label(text='3. Partes que toma la capa',icon='MOD_ARMATURE')
  row=box.row(align=True);row.operator('nl2.preset',text='Solo brazos').kind='ARMS';row.operator('nl2.preset',text='Torso y brazos').kind='UPPER'
  row=box.row(align=True);row.operator('nl2.preset',text='Cuerpo completo').kind='ALL';row.operator('nl2.preset',text='Solo piernas').kind='LEGS'
  box.label(text='0% = base / 100% = capa')
  for k in ['head','torso','left','right','pelvis','legs']:box.prop(s,k,slider=True)
  box.prop(s,'lock_pelvis');box.prop(s,'length');box.prop(s,'output_name')
  box=l.box();box.label(text='4. Vista previa y resultado',icon='PLAY');box.operator('nl2.mix',icon='ACTION');row=box.row(align=True);row.operator('nl2.play',icon='PLAY');row.operator('nl2.focus',text='Centrar');box.prop(s,'result');box.operator('nl2.preview',text='Ver resultado').which='result';box.operator('nl2.recipe',icon='FILE_REFRESH');box.operator('nl2.export',icon='EXPORT');box.label(text='Exporta archivos; no instala en el juego')
  l.prop(s,'advanced',icon='PREFERENCES')
  if s.advanced:
   box=l.box();box.prop(s,'rig')
   for k in ['base_speed','overlay_speed','base_offset','overlay_offset','loop','fixed_root','only_selected','other']:box.prop(s,k)
  l.label(text=s.status)
classes=[NL2Settings,NL2Focus,NL2LoadModel,NL2LoadProp,NL2LoadMotion,NL2Preview,NL2Preset,NL2Mix,NL2Recipe,NL2Play,NL2Export,NL2Panel]
def register():
 for c in classes:bpy.utils.register_class(c)
 bpy.types.Scene.nl2=PointerProperty(type=NL2Settings)
def unregister():
 del bpy.types.Scene.nl2
 for c in reversed(classes):bpy.utils.unregister_class(c)
if __name__=='__main__':register()

