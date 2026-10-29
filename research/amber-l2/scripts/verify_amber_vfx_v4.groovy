import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,stage=new File(root,'exports/contract/combat-vfx-v4')
def env=new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v4/*.u','research/amber-l2/exports/contract/combat-vfx-v4/*.utx','research/amber-l2/exports/contract/combat-vfx-v4/*.usk','../l2/system-hud/*.u','../l2/system/*.u','../l2/animations/*.ukx','../l2/animations/*.usk','../l2/systextures/*.utx'])
def factory=new UnrealSerializerFactory(env)
def value={obj,String name->obj.@properties.find{it.name==name}?.getAt(0)}
def num={obj,String name,String axis,String bound->value(obj,name).find{it.name==axis}.getAt(0).find{it.name==bound}.getAt(0)}
def range={obj,String name,String bound->value(obj,name).find{it.name==bound}.getAt(0)}
int checks=0
def check={boolean ok,String label->assert ok:label;checks++}
byte[] rawPalette=new File(stage,'AmberVfxMaterialsV4.utx').bytes
byte[] encodedPalette=new File(stage,'AmberVfxMaterialsV4.client.utx').bytes
check(encodedPalette.length==rawPalette.length+48,'client texture wrapper size')
check(new String(encodedPalette,0,28,'UTF-16LE')=='Lineage2Ver121','client texture wrapper version')
int paletteKey='ambervfxmaterialsv4.utx'.chars().sum()&255
check((0..<rawPalette.length).every{((encodedPalette[it+28]&255)^paletteKey)==(rawPalette[it]&255)},'client texture full filename-key roundtrip')
if(args.length>1&&args[1]=='installed'){
 def client=new File(project.parentFile,'l2')
 check(Arrays.equals(encodedPalette,new File(client,'systextures/AmberVfxMaterialsV4.utx').bytes),'installed texture must be encoded')
}
new UnrealPackage(new File(stage,'AmberEffectsV4.usk'),true).withCloseable{up->
 for(String name:['Rain','FireRain','Mark','SkyVolley']+(1..16).collect{'FireShot'+it}){
  def o=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name})
  check(o.@properties.size()==1&&o.@properties[0].name=='ShotActions',name+' launch phase')
 }
 for(String name:['Rain','FireRain','RainImpact','FireRainImpact','Mark']){
  def o=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name+'Action'})
  check(value(o,'bSpawnOnTarget')==true&&value(o,'bSizeScale')==false&&value(o,'bRelativeToCylinder')==false,name+' fixed target position and real radius')
 }
}
new UnrealPackage(new File(stage,'AmberParticlesV4.u'),true).withCloseable{up->
 def object={String name->factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name})}
 for(String name:['AreaRing','AreaDisk','ArrowSky','ArrowWhite','ArrowFire','ArrowShot']){
  int material=value(object(name),'Materials')[0].find{it.name=='Material'}.getAt(0)
  check(up.objectReference(material).objectFullName.startsWith('AmberVfxMaterialsV4.'),name+' explicit material')
 }
 def sky=object('SkyVolley');check(value(sky,'Emitters').size()==120,'60 arrows with 60 luminous tips')
 for(int i=0;i<60;i++){
  def a=object('SkyVolley.P'+i*2)
  check(value(a,'MaxParticles')==1&&value(a,'RespawnDeadParticles')==false,'one sky arrow per emitter')
  // UCC omits an all-zero InitialDelayRange on the first arrow.
  check(i==0||Math.abs(range(a,'InitialDelayRange','Min')-i*0.04)<0.0001,'staggered sky release')
  check(num(a,'StartVelocityRange','Z','Min')==650,'sky goes up')
 }
 for(String name:['Rain','FireRain']){
  check(value(object(name),'Emitters').size()==100,name+' 50 arrows with luminous tips')
  for(int i=0;i<50;i++){
   def a=object(name+'.P'+i*2)
   check(Math.hypot(num(a,'StartLocationRange','X','Min'),num(a,'StartLocationRange','Y','Min'))<=200,name+' within damage circle')
   check(Math.abs(range(a,'LifetimeRange','Min')-0.650)<0.0001&&num(a,'StartVelocityRange','Z','Min')==-600,name+' impact synchronized at 650ms')
  }
 }
 check(value(object('Mark'),'Emitters').size()==2,'area has outline and fill')
 for(int i=0;i<2;i++){
  def o=object('Mark.P'+i)
  check(value(o,'UseMeshBlendMode')==false,'ground area blends translucently')
  check(Math.abs(range(o,'LifetimeRange','Min')-5.8)<0.0001,'area spans charge and impact waves')
 }
 for(int i=1;i<=16;i++){
  check(value(object('FireShot'+i),'Emitters').size()==2,'fire arrow has mesh and bright trail')
  def glow=object('FireShot'+i+'.P1')
  check(num(glow,'StartVelocityRange','X','Min')==1400,'fire glow travels with arrow')
 }
}
println 'PASS: '+checks+' staged V4 package checks. This verifies structure and timing, not in-game visibility.'
