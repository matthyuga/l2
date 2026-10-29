import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,stage=new File(root,'exports/contract/combat-vfx-v4')
def particles=new File(stage,'AmberParticlesV4.u')
particles.bytes=new File(root,'tools/l2editor/L2Editor/AmberParticlesV4.u').bytes
// Preserve the texture native payload and its lazy-array offsets verbatim.
// A separate palette package lets mesh material references remain one-byte imports.
def palette=new File(stage,'AmberVfxMaterialsV4.utx');palette.bytes=particles.bytes
new UnrealPackage(palette,false).withCloseable{it.setUUID(UUID.randomUUID())}
def factory=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v4/*.u','research/amber-l2/exports/contract/combat-vfx-v4/*.utx','../l2/system-hud/*.u','../l2/system/*.u']))
new UnrealPackage(particles,false).withCloseable{up->
 def materials=[AreaRing:'AreaGold',AreaDisk:'AreaFill',ArrowWhite:'AmberWhite',ArrowFire:'AmberFire',ArrowSky:'AmberWhite',ArrowShot:'AmberFire']
 up.addImportEntries(materials.values().toList().unique().collectEntries{[('AmberVfxMaterialsV4.'+it):'Engine.Texture']})
 materials.each{name,texture->
  def entry=up.exportTable.find{it.objectInnerFullName==name}
  def object=factory.getOrCreateObject(entry)
  int old=object.@properties.find{it.name=='Materials'}.getAt(0)[0].find{it.name=='Material'}.getAt(0)
  int replacement=up.importTable.find{it.objectFullName=='AmberVfxMaterialsV4.'+texture}.objectReference
  byte[] before=AmberCatalog.compact(old),after=AmberCatalog.compact(replacement)
  assert before.length==1&&after.length==1:'Do not shift native mesh payload'
  byte[] raw=entry.objectRawData
  // Materials array is the first tagged property; locate the Material object property within it.
  byte[] prefix=AmberCatalog.compact(up.nameReference('Material'))
  def matches=[]
  for(int i=0;i<20-prefix.length-1;i++)if((0..<prefix.length).every{raw[i+it]==prefix[it]}&&(raw[i+prefix.length]&255)==5&&raw[i+prefix.length+1]==before[0])matches<<i+prefix.length+1
  assert matches.size()==1:'Ambiguous material position for '+name
  raw[matches[0]]=after[0];entry.setObjectRawData(raw)
 }
}
println 'PASS: six mesh materials explicitly linked; native mesh byte counts and offsets preserved.'
def encoder=new ProcessBuilder('powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',new File(root,'Build-AmberVfxMaterialsV4.ps1').path).redirectErrorStream(true).start()
def output=encoder.inputStream.text;assert encoder.waitFor()==0:output;println output.trim()
