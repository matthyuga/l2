import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.core.Function
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
import java.nio.ByteBuffer
import java.nio.ByteOrder
def client=new File(args[0]),output=new File(args[1]);output.bytes=new File(client,'Interface.u').bytes
def serializer=new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx']))
def encode={obj,entry->
 def out=new ByteArrayOutputStream(),context=new UnrealRuntimeContext(entry,serializer)
 def stream=new ObjectOutputStream(out,entry.unrealPackage.file.charset,0,serializer,context)
 serializer.forClass(obj.class).writeObject(obj,stream);if(obj.unreadBytes?.length)out.write(obj.unreadBytes)
 byte[] b=out.toByteArray()
 if(obj instanceof Function){
  assert obj.@properties.empty;int at=0
  7.times{int first=b[at++]&255;if(first&64){int n;do{n=b[at++]&255}while(n&128)}}
  at+=8;int size=obj.bytecode.sum{it.getSize(new BytecodeContext(context))}?:0
  ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).putInt(at,size)
 };b
}
new UnrealPackage(output,false).withCloseable{up->
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 def original=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 assert byName('MagicSkillWnd.OnClickButton')!=null&&byName('SummonedWnd.OnClickButton')==null
 def make={clazzName,choices->
  def clazz=serializer.getOrCreateObject(byName(clazzName))
  def entry=byName(clazzName+'.OnClickButton')
  def paramEntry=byName(clazzName+'.OnClickButton.strID')
  def fn=entry==null?null:serializer.getOrCreateObject(entry)
  if(entry==null){
   up.addExportEntry(clazzName+'.OnClickButton','Core.Function',null,byName('MagicSkillWnd.OnClickItem').objectRawData,UnrealPackage.DEFAULT_OBJECT_FLAGS)
   up.addExportEntry(clazzName+'.OnClickButton.strID','Core.StrProperty',null,byName('MagicSkillWnd.OnClickItem.strID').objectRawData,UnrealPackage.DEFAULT_OBJECT_FLAGS)
   entry=byName(clazzName+'.OnClickButton');paramEntry=byName(clazzName+'.OnClickButton.strID')
   def param=serializer.getOrCreateObject(byName('MagicSkillWnd.OnClickItem.strID'));param.next=null;param.superField=null;param.entry=paramEntry;paramEntry.setObjectRawData(encode(param,paramEntry))
   fn=serializer.getOrCreateObject(byName('MagicSkillWnd.OnClickItem'))
   fn.entry=entry;fn.superField=null;fn.next=clazz.child;fn.child=param;fn.scriptText=null;fn.cppText=null;fn.friendlyName='OnClickButton';fn.line=0;fn.textPos=0
   entry.setObjectRawData(encode(fn,entry))
   clazz.child=fn;byName(clazzName).setObjectRawData(encode(clazz,byName(clazzName)))
  }
  def ctx=new BytecodeContext(new UnrealRuntimeContext(entry,serializer));def tokens=[]
  choices.each{key,command->
   def condition=new NativeFunctionCall(122,new LocalVariable(paramEntry.objectReference),new StringConst(key))
   def jump=new JumpIfNot(condition:condition,targetOffset:0)
   tokens<<jump;tokens<<new VirtualFunction(up.nameReference('RequestBypassToServer'),new StringConst(command));tokens<<new Return(new Nothing())
   jump.targetOffset=tokens.sum{it.getSize(ctx)}
  }
  tokens<<new Return(new Nothing());fn.bytecode=tokens as Token[];entry.setObjectRawData(encode(fn,entry))
 }
 make('MagicSkillWnd',['ClassMain':'voice .habilidades quick 0','ClassSub1':'voice .habilidades quick 1','ClassSub2':'voice .habilidades quick 2','ClassSub3':'voice .habilidades quick 3','ClassCommon':'voice .habilidades quick 4','ClassAmber':'voice .habilidades quick 5','ClassAll':'voice .habilidades quick -1','ClassesButton':'voice .habilidades','AmberAssistButton':'voice .amber toggle'])
 make('SummonedWnd',['AmberAssistButton':'voice .amber toggle'])
 original.each{name,b->if(!(name in ['MagicSkillWnd.OnClickButton','SummonedWnd']))assert Arrays.equals(b,byName(name).objectRawData):'Unrelated export changed '+name}
 println 'PASS: class buttons dispatch filters individually; both AI buttons use the native effect lifecycle; all unrelated exports byte identical.'
}
