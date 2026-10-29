import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,stage=new File(root,'exports/contract/combat-vfx-v5');stage.mkdirs()
def particles=new File(stage,'AmberParticlesV5.u');particles.bytes=new File(root,'exports/contract/combat-vfx-v4/AmberParticlesV4.u').bytes
def glyphs=new File(stage,'DamageGlyphsV1.u');glyphs.bytes=new File(root,'tools/l2editor/L2Editor/DamageGlyphsV1.u').bytes
def f=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v5/*.u','../l2/system-hud/*.u','../l2/system/*.u','../l2/systextures/*.utx']))
new UnrealPackage(particles,false).withCloseable{up->
 up.setUUID(UUID.randomUUID());up.addImportEntries(['AmberFireTexturesV1.KenneyFire':'Engine.Texture'])
 int replacement=up.importTable.find{it.objectFullName=='AmberFireTexturesV1.KenneyFire'}.objectReference
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'&&(it.objectInnerFullName.startsWith('FireRain')||it.objectInnerFullName.startsWith('FireShot'))}.each{entry->
  def o=f.getOrCreateObject(entry);int old=o.@properties.find{it.name=='Texture'}.getAt(0)
  byte[] oldBytes=AmberCatalog.compact(old),newBytes=AmberCatalog.compact(replacement),prefix=AmberCatalog.compact(up.nameReference('Texture'))
  assert oldBytes.length==1&&newBytes.length==1
  byte[] raw=entry.objectRawData
  def matches=[]
  for(int i=0;i<raw.length-prefix.length-1;i++)if((0..<prefix.length).every{raw[i+it]==prefix[it]}&&(raw[i+prefix.length]&255)==5&&raw[i+prefix.length+1]==oldBytes[0])matches<<i+prefix.length+1
  assert matches.size()==1:entry.objectInnerFullName
  raw[matches[0]]=newBytes[0];entry.setObjectRawData(raw)
 }
}
for(File file:[particles,glyphs]){
 def proc=new ProcessBuilder(new File(project,'tools/jdk-25.0.4.1+1/bin/java.exe').path,'-cp',new File(project,'tools/XDAT_NEW/xdat_editor/dist/*').path+';'+new File(root,'scripts').path,'groovy.ui.GroovyMain',new File(root,'scripts/force_client_particles.groovy').path,file.path).redirectErrorStream(true).start()
 def out=proc.inputStream.text;assert proc.waitFor()==0:out;println out.trim()
}
println 'PASS: V5 particles cloned without changing V4, external fire texture linked, all effect and glyph particle counts forced.'
