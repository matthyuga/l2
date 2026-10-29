import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,stage=new File(root,'exports/contract/combat-vfx-v9')
def factory=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v9/*.u','research/amber-l2/exports/contract/combat-vfx-v9/*.usk','../l2/system-hud/*.u','../l2/system/*.u','../l2/animations/*.usk','../l2/systextures/*.utx']))
def value={o,n->o.@properties.find{it.name==n}?.getAt(0)}
def axis={o,n,a,b->def v=value(o,n);if(v==null)return 0;def av=v.find{it.name==a}?.getAt(0);return av?.find{it.name==b}?.getAt(0)?:0}
def range={o,n,b->value(o,n).find{it.name==b}.getAt(0)}
int checks=0
def check={ok,label->assert ok:label;checks++}
new UnrealPackage(new File(stage,'AmberParticlesV9.u'),true).withCloseable{up->
 def obj={n->factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==n})}
 check(value(obj('SkyVolley'),'Emitters').size()==100,'exactly 50 rising meshes and tips')
 for(int i=0;i<50;i++){
  def o=obj('SkyVolley.P'+i*2)
  check(axis(o,'StartVelocityRange','Z','Min')==650,'rising arrow direction')
  check(i==0||Math.abs(range(o,'InitialDelayRange','Min')-i*0.04)<0.0001,'rising arrow timing')
 }
 for(String prefix:['Rain','FireRain'])for(int wave=1;wave<=3;wave++){
  String n=prefix+wave;int count=wave==3?16:17
  check(value(obj(n),'Emitters').size()==count*(prefix=='FireRain'?4:2),n+' exact mesh count')
  for(int i=0;i<count;i++){
   def o=obj(n+'.P'+i*(prefix=='FireRain'?4:2))
   check(Math.hypot(axis(o,'StartLocationRange','X','Min'),axis(o,'StartLocationRange','Y','Min'))<=200,'falling arrow inside actual damage circle')
   check(axis(o,'StartVelocityRange','Z','Min')==-600&&Math.abs(range(o,'LifetimeRange','Min')-0.650)<0.0001,'fall time matches server damage')
  }
 }
 for(String n:['ArrowUp','ArrowDown','ArrowForward']){
  int ref=value(obj(n),'Materials')[0].find{it.name=='Material'}.getAt(0)
  check(up.objectReference(ref).objectFullName.startsWith('AmberMaterialsV9.'),'mesh references encoded installed palette')
 }
 for(String prefix:['Rain','FireRain'])for(int wave=1;wave<=3;wave++){
  String n=prefix+wave
  def refs=value(obj(n),'Emitters');int flames=0
  refs.each{ref->def e=up.objectReference(ref);if(e.fullClassName=='Engine.SpriteEmitter'){
   def o=factory.getOrCreateObject(e);int tex=value(o,'Texture');if(up.objectReference(tex).objectInnerFullName=='Flame')flames++
  }}
  check(flames==(prefix=='FireRain'?(wave==3?16:17)*2:0),'ordinary rain has no flames, incendiary rain has two flames on every arrow')
 }
 for(int level=1;level<=16;level++){
  def o=obj('FireShot'+level+'.P1');check(axis(o,'StartSizeRange','X','Min')==12,'direct fire arrow carries larger visible flame')
  check(value(o,'UseSizeScale')==true,'fire changes shape during flight')
 }
 check(value(obj('Mark'),'Emitters').size()==1,'area uses smooth radial texture with halo and fill')
 check(value(obj('Mark.P0'),'UseDirectionAs')==4,'ground texture uses plane normal');check(value(obj('Mark.P0'),'UseSizeScale')==true,'ground area grows during charge');
 for(int i=0;i<1;i++)check(Math.abs(range(obj('Mark.P'+i),'LifetimeRange','Min')-5.8)<0.0001,'area covers charge and final impact')
 up.exportTable.findAll{it.fullClassName in ['Engine.MeshEmitter','Engine.SpriteEmitter']}.each{e->
  def o=factory.getOrCreateObject(e)
  check(value(o,'ForcedMaxParticles')==true,'client detail setting cannot reduce one arrow to zero');check(value(o,'CoordinateSystem')==1,'explicit native relative coordinate system')
  if(e.fullClassName=='Engine.MeshEmitter')check(value(o,'RenderTwoSided')==true,'mesh renders from either side')
 }
}
new UnrealPackage(new File(stage,'DamageGlyphsV3.u'),true).withCloseable{up->
 check(up.exportTable.count{it.fullClassName=='Engine.SpriteEmitter'}==400,'complete glyph catalog')
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  def o=factory.getOrCreateObject(e);check(value(o,'ForcedMaxParticles')==true,'digit count forced')
  check(axis(o,'StartLocationRange','Z','Min')==0,'remove extra 110-unit height')
  check(axis(o,'StartVelocityRange','Z','Min')==16,'gentle upward drift')
  check(value(o,'FadeOut')==true&&value(o,'FadeIn')==true&&value(o,'FadeOutStartTime')==0.5f,'smooth appearance and disappearance')
  check(value(o,'UseSizeScale')==true,'digit expands and contracts')
  def curve=value(o,'SizeScale');check(curve.size()==5,'five animation keyframes')
  float peak=curve[1].find{it.name=='RelativeSize'}.getAt(0)
  boolean critical=e.objectInnerFullName.startsWith('Dmg_1_')||e.objectInnerFullName.startsWith('Dmg_3_')
  check(Math.abs(peak-(critical?1.65:1.22))<0.001,'critical has stronger expansion')
 }
}
new UnrealPackage(new File(stage,'AmberEffectsV9.usk'),true).withCloseable{up->
 def obj={n->factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==n})}
 for(String n:['Mark','SkyVolley']+(1..3).collectMany{w->['Rain'+w,'FireRain'+w]}+(1..16).collect{'FireShot'+it}){
  def o=obj(n);check(o.@properties.size()==1&&o.@properties[0].name=='CastingActions',n+' native instant casting path')
 }
 for(String n:['Mark']+(1..3).collectMany{w->['Rain'+w,'FireRain'+w]}){
  def o=obj(n+'Action');check(value(o,'bSpawnOnTarget')==true&&value(o,'bRelativeToCylinder')==true&&value(o,'bSizeScale')==false,'fixed ground location and literal radius')
 }
 up.exportTable.findAll{it.objectInnerFullName.startsWith('Dmg_')&&it.objectInnerFullName.endsWith('Action')}.each{e->
  def o=factory.getOrCreateObject(e);check(value(o,'AttachOn')==0&&value(o,'bRelativeToCylinder')==true&&!value(o,'offset'),'glyph has no trail socket or extra scaled height')
 }
 for(int w=1;w<=3;w++)for(String prefix:['Rain','FireRain'])check(Math.abs(value(obj(prefix+w+'ImpactAction'),'SpawnDelay')-0.650)<0.0001,'impact at actual arrival')
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def cat=new AmberCatalog(new File(stage,'skillgrp.raw'),schemas,'skillgrp.xml','ScionsOfDestiny')
def nativeItem=cat.rows.find{it.skill_id==2033&&it.skill_level==1}
cat.rows.findAll{it.skill_id in [19007,19008,19009,19010,19012,19600]||it.skill_id>=19200&&it.skill_id<=19599}.each{r->
 for(String field:['operate_type','mp_consume','cast_range','cast_style','hit_time','is_magic','animation','extra_eff','rumble_self','rumble_target'])check(r[field]==nativeItem[field],'visual uses native instant item activation fields')
 check(r.description.startsWith('AmberEffectsV9.'),'all visuals resolve to new package')
}
def messages=new AmberCatalog(new File(stage,'systemmsg.raw'),schemas,'systemmsg.xml','Interlude')
messages.rows.findAll{it.id>=2200&&it.id<=2207}.each{check(it.scrnmsg==''&&it.lftime==0&&it.bkg==0,'old fixed screen overlay disabled')}
println 'PASS: '+checks+' package/catalog checks; client visual confirmation remains required.'
