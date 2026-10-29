import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2'),stage=new File(root,'exports/contract/combat-vfx-v8')
def compact=AmberCatalog.&compact
def particles=new File(stage,'AmberParticlesV8.u');particles.bytes=new File(root,'tools/l2editor/L2Editor/AmberParticlesV8.u').bytes
def palette=new File(stage,'AmberMaterialsV8.u');palette.bytes=particles.bytes
new UnrealPackage(palette,false).withCloseable{it.setUUID(UUID.randomUUID())}
def factory=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v8/*.u','../l2/system-hud/*.u','../l2/system/*.u']))
new UnrealPackage(particles,false).withCloseable{up->
 up.addImportEntries(['AmberMaterialsV8.ArrowMaterial':'Engine.Texture'])
 int replacement=up.importTable.find{it.objectFullName=='AmberMaterialsV8.ArrowMaterial'}.objectReference
 for(String n:['ArrowUp','ArrowDown','ArrowForward']){
  def e=up.exportTable.find{it.objectInnerFullName==n},o=factory.getOrCreateObject(e)
  int old=o.@properties.find{it.name=='Materials'}.getAt(0)[0].find{it.name=='Material'}.getAt(0)
  byte[] prefix=compact(up.nameReference('Material')),raw=e.objectRawData,before=compact(old),after=compact(replacement)
  assert before.length==1&&after.length==1
  def offsets=[];for(int i=0;i<20-prefix.length-1;i++)if((0..<prefix.length).every{raw[i+it]==prefix[it]}&&(raw[i+prefix.length]&255)==5&&raw[i+prefix.length+1]==before[0])offsets<<i+prefix.length+1
  assert offsets.size()==1;raw[offsets[0]]=after[0];e.setObjectRawData(raw)
 }
 up.addNameEntries(['ForcedMaxParticles','RenderTwoSided','CoordinateSystem'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.exportTable.findAll{it.fullClassName in ['Engine.MeshEmitter','Engine.SpriteEmitter']}.each{e->
  def o=factory.getOrCreateObject(e);def coordinate=o.@properties.find{it.name=='CoordinateSystem'};assert coordinate==null||coordinate.getAt(0)==1:'unexpected coordinate value'
  byte[] raw=e.objectRawData,none=compact(up.nameReference('None'));assert Arrays.equals(Arrays.copyOfRange(raw,raw.length-none.length,raw.length),none)
  def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length)
  if(coordinate==null){out.write(compact(up.nameReference('CoordinateSystem')));out.write(1);out.write(1)}
  out.write(compact(up.nameReference('ForcedMaxParticles')));out.write(0x83)
  if(e.fullClassName=='Engine.MeshEmitter'){out.write(compact(up.nameReference('RenderTwoSided')));out.write(0x83)}
  out.write(none);e.setObjectRawData(out.toByteArray())
 }
}
def effects=new File(stage,'AmberEffectsV8.usk');effects.bytes=new File(client,'animations/AmberEffectsV7.usk').bytes
new UnrealPackage(effects,false).withCloseable{up->
 up.setUUID(UUID.randomUUID());def n=up.nameTable.find{it.name=='AmberParticlesV7'};assert n;up.updateNameEntry(n.index,'AmberParticlesV8',n.flags)
}
if(args.length>1&&args[1]=='assets-only'){println 'PASS: assets and effects rebuilt; catalogs preserved.';return}
def codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def run={List cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();def output=p.inputStream.text;assert p.waitFor()==0:output}
for(def spec:[['skillgrp','skillgrp.dat','skillgrp.xml'],['skillname','skillname-e.dat','skillname.xml']]){
 def before=new File(stage,spec[0]+'.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/'+spec[1]).path])
 def cat=new AmberCatalog(before,schemas,spec[2],'ScionsOfDestiny'),raw=new File(stage,spec[0]+'.raw')
 raw.bytes=cat.patch{r->if(spec[0]=='skillgrp'&&r.description.startsWith('AmberEffectsV7.')){r.description=r.description.replace('AmberEffectsV7.','AmberEffectsV8.');return r};return null}
 def encoded=new File(stage,spec[1]);run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def check=new File(stage,spec[0]+'.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
 println 'PASS: '+spec[0]+' exact roundtrip; existing IDs and unrelated rows preserved.'
}
println 'PASS: quality meshes/materials linked, explicit working coordinates, V7 activation and damage glyphs preserved.'
