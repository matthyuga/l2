import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),stage=new File(root,'research/visual-effects/npc-labels/native-v1/compact-v3')
def f=new UnrealSerializerFactory(new Environment(root,['research/visual-effects/npc-labels/native-v1/compact-v3/*.u','../l2/system-hud/*.u']))
new UnrealPackage(new File(stage,'HellgamesLabelsV1.u'),true).withCloseable{up->
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  def props=f.getOrCreateObject(e).@properties.collectEntries{[(it.name):it.getAt(0)]}
  if(e.objectInnerFullName.endsWith('.Label')){
   assert props.UniformSize==false&&props.UseRegularSizeScale==false
   assert up.objectReference(props.Texture).objectFullName=='HGLabelArtV3.EventLabel'
   def range={String name,String axis->props[name].find{it.name==axis}.getAt(0).find{it.name=='Min'}.getAt(0)}
   assert range('StartSizeRange','X')==20f&&range('StartSizeRange','Y')==10f&&range('StartLocationRange','Z')==18f
  }else{assert props.Disabled==true}
  println 'PASS: '+e.objectInnerFullName+' compact properties, texture, and particle state.'
 }
}
