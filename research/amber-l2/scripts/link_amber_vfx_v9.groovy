import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2'),stage=new File(root,'exports/contract/combat-vfx-v9')
def compact=AmberCatalog.&compact
def particles=new File(stage,'AmberParticlesV9.u');particles.bytes=new File(root,'tools/l2editor/L2Editor/AmberParticlesV9.u').bytes
def palette=new File(stage,'AmberMaterialsV9.u');palette.bytes=particles.bytes
new UnrealPackage(palette,false).withCloseable{it.setUUID(UUID.randomUUID())}
def factory=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v9/*.u','../l2/system-hud/*.u','../l2/system/*.u']))
new UnrealPackage(particles,false).withCloseable{up->
 up.addImportEntries(['AmberMaterialsV9.ArrowMaterial':'Engine.Texture'])
 int replacement=up.importTable.find{it.objectFullName=='AmberMaterialsV9.ArrowMaterial'}.objectReference
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
def glyphs=new File(stage,'DamageGlyphsV3.u');glyphs.bytes=new File(root,'tools/l2editor/L2Editor/DamageGlyphsV3.u').bytes
def force=new ProcessBuilder(new File(project,'tools/jdk-25.0.4.1+1/bin/java.exe').path,'-cp',new File(project,'tools/XDAT_NEW/xdat_editor/dist/*').path+';'+new File(root,'scripts').path,'groovy.ui.GroovyMain',new File(root,'scripts/force_client_particles.groovy').path,glyphs.path).redirectErrorStream(true).start()
def forceOut=force.inputStream.text;assert force.waitFor()==0:forceOut;println forceOut.trim()
def effects=new File(stage,'AmberEffectsV9.usk');effects.bytes=new File(client,'animations/AmberEffectsV8.usk').bytes
new UnrealPackage(effects,false).withCloseable{up->
 up.setUUID(UUID.randomUUID());def n=up.nameTable.find{it.name=='AmberParticlesV8'};assert n;up.updateNameEntry(n.index,'AmberParticlesV9',n.flags);def g=up.nameTable.find{it.name=='DamageGlyphsV2'};assert g;up.updateNameEntry(g.index,'DamageGlyphsV3',g.flags)
}
if(args.length>1&&args[1]=='assets-only'){println 'PASS: assets and effects rebuilt; catalogs preserved.';return}
def codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def run={List cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();def output=p.inputStream.text;assert p.waitFor()==0:output}
for(def spec:[['skillgrp','skillgrp.dat','skillgrp.xml'],['skillname','skillname-e.dat','skillname.xml']]){
 def before=new File(stage,spec[0]+'.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/'+spec[1]).path])
 def cat=new AmberCatalog(before,schemas,spec[2],'ScionsOfDestiny'),raw=new File(stage,spec[0]+'.raw')
 raw.bytes=cat.patch{r->if(spec[0]=='skillgrp'&&r.description.startsWith('AmberEffectsV8.')){r.description=r.description.replace('AmberEffectsV8.','AmberEffectsV9.');return r};return null}
 def encoded=new File(stage,spec[1]);run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def check=new File(stage,spec[0]+'.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
 println 'PASS: '+spec[0]+' exact roundtrip; existing IDs and unrelated rows preserved.'
}
println 'PASS: stronger fire and lower animated glyphs; working activation preserved.'

// Remove only the obsolete damage screen overlays; keep their chat messages.
def before=new File(stage,'systemmsg.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/systemmsg-e.dat').path])
def cat=new AmberCatalog(before,schemas,'systemmsg.xml','Interlude')
cat.rows.findAll{it.id>=2200&&it.id<=2210}.each{println 'OLD_DAMAGE '+it.findAll{k,v->k in ['id','message','scrnmsg','win','font','lftime','bkg','anim']}}
def changed=[]
def raw=new File(stage,'systemmsg.raw');raw.bytes=cat.patch{r->
 if(r.id>=2200&&r.id<=2207){r.scrnmsg='';r.lftime=0;r.bkg=0;changed<<r.id;return r}
 return null
}
assert changed.containsAll([2200L,2201L,2202L,2203L]):'missing old outgoing damage overlays'
def finalCat=new AmberCatalog(raw,schemas,'systemmsg.xml','Interlude')
cat.rows.eachWithIndex{r,i->
 assert r.message==finalCat.rows[i].message:'chat damage text preserved'
 if(!(r.id in changed))assert Arrays.equals(Arrays.copyOfRange(cat.data,r._start,r._end),Arrays.copyOfRange(finalCat.data,finalCat.rows[i]._start,finalCat.rows[i]._end)):'unrelated system message changed'
}
def encoded=new File(stage,'systemmsg-e.dat');run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def check=new File(stage,'systemmsg.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
println 'PASS: old damage overlays disabled, chat and unrelated messages preserved, exact roundtrip.'
