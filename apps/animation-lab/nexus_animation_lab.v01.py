bl_info={'name':'Nexus L2 Animation Lab','author':'Nexus','version':(0,1,0),'blender':(3,5,0),'category':'Animation'}
import bpy,json,sys,subprocess,os
from pathlib import Path
from bpy.props import StringProperty,FloatProperty,IntProperty,BoolProperty,PointerProperty
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
 s=context.scene.nl2;r=rig(context);a=bpy.data.actions.get(s.base);b=bpy.data.actions.get(s.overlay)
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
 bl_label='Nexus L2 Animation Lab';bl_idname='NL2_PT_MAIN';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Nexus L2'
 def draw(self,context):
  l=self.layout;s=context.scene.nl2;l.label(text='Fighter mujer | Editor por capas');l.prop(s,'rig');l.prop_search(s,'base',bpy.data,'actions');l.prop_search(s,'overlay',bpy.data,'actions');l.prop(s,'output_name');l.prop(s,'length')
  for k in ['base_speed','overlay_speed','base_offset','overlay_offset']:l.prop(s,k)
  l.prop(s,'loop');l.separator();l.label(text='Peso de la capa superior (0 = base)')
  for k in ['pelvis','legs','torso','head','left','right','other']:l.prop(s,k,slider=True)
  for k in ['fixed_root','lock_pelvis','only_selected']:l.prop(s,k)
  l.operator('nl2.mix',icon='ACTION');l.operator('nl2.play',icon='PLAY');l.prop(s,'result');l.operator('nl2.recipe',icon='FILE_REFRESH');l.operator('nl2.export',icon='EXPORT');l.label(text='Exporta recursos; no instala en L2',icon='INFO')
classes=[NL2Settings,NL2Mix,NL2Recipe,NL2Play,NL2Export,NL2Panel]
def register():
 for c in classes:bpy.utils.register_class(c)
 bpy.types.Scene.nl2=PointerProperty(type=NL2Settings)
def unregister():
 del bpy.types.Scene.nl2
 for c in reversed(classes):bpy.utils.unregister_class(c)
if __name__=='__main__':register()
