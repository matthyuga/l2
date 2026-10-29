import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import java.nio.ByteBuffer
import java.nio.ByteOrder
def root=new File(args[0]),project=root.parentFile.parentFile,stage=new File(root,'exports/mmd-variants-20261023')
def factory=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/mmd-variants-20261023/*.ukx','../l2/system-hud/*.u','../l2/system/*.u','../l2/animations/*.ukx']))
def val={o,n->o.@properties.find{it.name==n}?.getAt(0)}
int checks=0;def check={condition,message->assert condition:message;checks++}
for(String pkg:['AmberMMD10','AmberMMD14'])new UnrealPackage(new File(stage,pkg+'.ukx'),true).withCloseable{up->
 check(up.exportTable.count{it.fullClassName=='Engine.Shader'}==8,'eight independent materials')
 check(up.exportTable.count{it.fullClassName=='Engine.Texture'}==6,'six texture assets')
 check(up.importTable.any{it.objectFullName=='L2AmberArcherMotion.FFighter_anim'},'uses working bow animation package')
 byte[] raw=up.exportTable.find{it.objectInnerFullName=='AmberNPC'}.objectRawData;def bb=ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN)
 check(bb.getFloat(80)==26.5f&&bb.getInt(88)==49152,'native female origin/rotation')
 up.exportTable.findAll{it.fullClassName=='Engine.Shader'}.each{e->
  def o=factory.getOrCreateObject(e)
  check(val(o,'TwoSided')==true&&val(o,'ZWrite')==true&&val(o,'AlphaTest')==true,'masked material writes depth from both sides')
  check(val(o,'AlphaRef')==128&&val(o,'OutputBlending')==1,'alpha cutout128')
  check(val(o,'Diffuse')==val(o,'SelfIllumination'),'preserve toon base colors independent of map lighting')
  check(up.objectReference(val(o,'Diffuse')).fullClassName=='Engine.Texture','base texture resolves')
 }
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def cat=new AmberCatalog(new File(stage,'npcgrp.raw'),schemas,'npcgrp.xml','Interlude')
for(def spec:[[59020,'AmberMMD10'],[59021,'AmberMMD14']]){
 def row=cat.rows.find{it.npc_id==spec[0]};check(row!=null,'new display record exists');check(row.class_name=='AmberActorsV1.AmberArcher','same tested bow actor sockets');check(row.mesh_name==spec[1]+'.AmberNPC','correct model');check(row.texture_name==8,'all8 slots bound')
 check(row.texture_name_items.every{it.param_texture_name.startsWith(spec[1]+'.')&&it.param_texture_name.endsWith('Shader')},'no old Koikatsu textures reused')
}
println 'PASS: '+checks+' native package/catalog checks.'
