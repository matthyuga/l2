import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.core.Function
import acmi.l2.clientmod.unreal.bytecode.token.*
import java.nio.charset.Charset
import java.nio.ByteBuffer
import java.nio.ByteOrder
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext

def client=new File(args[0]);def output=new File(args[1]);output.bytes=new File(client,'Interface.u').bytes
def serializer=new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx']))
def encode={obj,entry->
 def out=new ByteArrayOutputStream()
 def stream=new ObjectOutputStream(out,entry.unrealPackage.file.charset,0,serializer,new UnrealRuntimeContext(entry,serializer))
 serializer.forClass(obj.class).writeObject(obj,stream)
 if(obj.unreadBytes?.length)out.write(obj.unreadBytes)
 byte[] bytes=out.toByteArray()
 if(obj instanceof Function){
  assert obj.@properties.empty
  // The bundled serializer writes token count; UE2 requires bytecode VM size.
  int at=0
  for(int field=0;field<7;field++){
   int first=bytes[at++]&255
   if((first&64)!=0){int b;do{b=bytes[at++]&255}while((b&128)!=0)}
  }
  at+=8
  int size=obj.bytecode.sum{it.getSize(new BytecodeContext(new UnrealRuntimeContext(entry,serializer)))}?:0
  ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).putInt(at,size)
 }
 bytes
}
new UnrealPackage(output,false).withCloseable{up->
 def byName={name->up.exportTable.find{it.objectInnerFullName==name}}
 assert byName('MagicSkillWnd.OnClickButton')==null:'Already patched; inspect current package.'
 def clazz=serializer.getOrCreateObject(byName('MagicSkillWnd'))
 assert Arrays.equals(clazz.entry.objectRawDataExternally,byName('MagicSkillWnd').objectRawData):'Wrong Interface package resolved.'
 assert Arrays.equals(encode(clazz,byName('MagicSkillWnd')),byName('MagicSkillWnd').objectRawData):'Class roundtrip mismatch'
 def originalExports=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 def template=serializer.getOrCreateObject(byName('MagicSkillWnd.OnClickItem'))
 new File(output.parentFile,'function-original.bin').bytes=byName('MagicSkillWnd.OnClickItem').objectRawData
 new File(output.parentFile,'function-roundtrip.bin').bytes=encode(template,byName('MagicSkillWnd.OnClickItem'))
 assert Arrays.equals(encode(template,byName('MagicSkillWnd.OnClickItem')),byName('MagicSkillWnd.OnClickItem').objectRawData):'Function roundtrip mismatch'
 up.addNameEntries(['RequestBypassToServer','OnClickButton'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 // A new button callback, with the same string argument signature as other UI buttons.
 up.addExportEntry('MagicSkillWnd.OnClickButton','Core.Function',null,byName('MagicSkillWnd.OnClickItem').objectRawData,UnrealPackage.DEFAULT_OBJECT_FLAGS)
 up.addExportEntry('MagicSkillWnd.OnClickButton.strID','Core.StrProperty',null,byName('MagicSkillWnd.OnClickItem.strID').objectRawData,UnrealPackage.DEFAULT_OBJECT_FLAGS)
 def functionEntry=byName('MagicSkillWnd.OnClickButton');def paramEntry=byName('MagicSkillWnd.OnClickButton.strID')
 def param=serializer.getOrCreateObject(byName('MagicSkillWnd.OnClickItem.strID'))
 param.next=null;param.superField=null;param.entry=paramEntry;paramEntry.setObjectRawData(encode(param,paramEntry))
 template.entry=functionEntry;template.superField=null;template.next=clazz.child;template.child=param
 template.scriptText=null;template.cppText=null;template.friendlyName='OnClickButton';template.line=0;template.textPos=0
 template.bytecode=[new VirtualFunction(up.nameReference('RequestBypassToServer'),new StringConst('voice .habilidades')),new Return(new Nothing())] as Token[]
 functionEntry.setObjectRawData(encode(template,functionEntry))
 clazz.child=template;byName('MagicSkillWnd').setObjectRawData(encode(clazz,byName('MagicSkillWnd')))
 originalExports.each{name,raw->if(name!='MagicSkillWnd')assert Arrays.equals(raw,byName(name).objectRawData):'Unexpected changed export '+name}
 println 'PASS: button callback added; all previous function exports byte identical; class child chain updated.'
 println 'Callback: RequestBypassToServer("voice .habilidades")'
}
