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
 assert obj instanceof Function && obj.@properties.empty
 int at=0;7.times{int first=b[at++]&255;if(first&64){int n;do{n=b[at++]&255}while(n&128)}}
 at+=8;int size=obj.bytecode.sum{it.getSize(new BytecodeContext(context))}?:0
 ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).putInt(at,size);b
}
new UnrealPackage(output,false).withCloseable{up->
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 def original=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 def nativeBypass=up.importTable.find{it.objectFullName=='NWindow.UIScript.RequestBypassToServer'}
 assert nativeBypass!=null
 def decl=serializer.getOrCreateObject(nativeBypass);assert (decl.functionFlags&1)!=0 && (decl.functionFlags&1024)!=0
 def make={clazz,choices->
  def entry=byName(clazz+'.OnClickButton'),fn=serializer.getOrCreateObject(entry)
  def ctx=new BytecodeContext(new UnrealRuntimeContext(entry,serializer)),tokens=[]
  choices.each{key,command->
   def jump=new JumpIfNot(condition:new NativeFunctionCall(122,new LocalVariable(fn.child.entry.objectReference),new StringConst(key)),targetOffset:0)
   tokens<<jump;tokens<<new FinalFunction(nativeBypass.objectReference,new StringConst(command));tokens<<new Return(new Nothing())
   jump.targetOffset=tokens.sum{it.getSize(ctx)}
  }
  tokens<<new Return(new Nothing());fn.bytecode=tokens as Token[];entry.setObjectRawData(encode(fn,entry))
 }
 make('MagicSkillWnd',['ClassMain':'voice .habilidades quick 0','ClassSub1':'voice .habilidades quick 1','ClassSub2':'voice .habilidades quick 2','ClassSub3':'voice .habilidades quick 3','ClassCommon':'voice .habilidades quick 4','ClassAmber':'voice .habilidades quick 5','ClassAll':'voice .habilidades quick -1','ClassNext':'voice .habilidades next','ClassesButton':'voice .habilidades','AmberAssistButton':'voice .amber toggle'])
 make('SummonedWnd',['AmberAssistButton':'voice .amber toggle'])

 // Insert decoration guards while relocating every existing VM branch.
 def patch={name,choose,insert->
  def entry=byName(name),fn=serializer.getOrCreateObject(entry),ctx=new BytecodeContext(new UnrealRuntimeContext(entry,serializer))
  def old=fn.bytecode.toList(),offsets=[:];int position=0
  old.each{t->offsets[t]=position;position+=t.getSize(ctx)}
  int oldEnd=position;def tokens=[],relocation=[:],newBranches=[]
  old.each{t->
   relocation[offsets[t]]=tokens.sum{it.getSize(ctx)}?:0
   if(choose(t)){def extras=insert(t,fn);tokens.addAll(extras);newBranches.addAll(extras.findAll{it instanceof JumpIfNot})}
   tokens<<t
  }
  relocation[oldEnd]=tokens.sum{it.getSize(ctx)}
  old.each{t->if(t instanceof JumpIfNot||t instanceof Jump){assert relocation.containsKey(t.targetOffset);t.targetOffset=relocation[t.targetOffset]}}
  // New guards skip only their own inserted instructions (they all end at the original selected token).
  int at=0;tokens.eachWithIndex{t,i->
   if(t in newBranches){int j=i+1;while(j<tokens.size() && !old.contains(tokens[j]))j++;t.targetOffset=at+(i..j-1).sum{tokens[it].getSize(ctx)}}
   at+=t.getSize(ctx)
  }
  fn.bytecode=tokens as Token[];entry.setObjectRawData(encode(fn,entry))
 }
 def handle=serializer.getOrCreateObject(byName('MagicSkillWnd.HandleSkillList'))
 def greater=handle.bytecode.find{it instanceof JumpIfNot&&it.condition.toString(new UnrealRuntimeContext(byName('MagicSkillWnd.HandleSkillList'),serializer)).contains('Lock > 0')}.condition.nativeIndex
 def field={name->handle.bytecode.find{it instanceof Let && it.left instanceof StructMember && up.objectReference(it.left.objRef).objectName.name==name}.left}
 def skillId=handle.bytecode.find{it instanceof Let&&it.left instanceof StructMember&&up.objectReference(it.left.objRef).objectName.name=='ClassID'}.right
 patch('MagicSkillWnd.HandleSkillList',{it.toString(new UnrealRuntimeContext(byName('MagicSkillWnd.HandleSkillList'),serializer)).contains('.static.AddItem(')}, {token,fn->
  [new JumpIfNot(condition:new NativeFunctionCall(greater,skillId,new IntConst(19099)),targetOffset:0),
   new JumpIfNot(condition:new NativeFunctionCall(greater,new IntConst(19200),skillId),targetOffset:0),
   new Let(field('ClassID'),new IntZero()),new Let(field('Level'),new IntZero()),
   new Let(field('ItemSubType'),new IntZero()),new Let(field('MacroCommand'),new StringConst(''))]
 })
 // Never send UseSkill(0) for a header or an empty padding cell.
 def clickEntry=byName('MagicSkillWnd.OnClickItem'),click=serializer.getOrCreateObject(clickEntry)
 def use=click.bytecode.find{it.toString(new UnrealRuntimeContext(clickEntry,serializer)).startsWith('UseSkill(')}
 def guard=new JumpIfNot(condition:new NativeFunctionCall(greater,use.params[0],new IntZero()),targetOffset:0)
 // Generic insertion helper points to UseSkill; this guard must point after UseSkill instead.
 patch('MagicSkillWnd.OnClickItem',{it.is(use)},{t,fn->[guard]})
 click=serializer.getOrCreateObject(clickEntry)
 def ctx=new BytecodeContext(new UnrealRuntimeContext(clickEntry,serializer));int end=0
 click.bytecode.each{t->if(t instanceof Return && guard.targetOffset<end)guard.targetOffset=end;end+=t.getSize(ctx)}
 clickEntry.setObjectRawData(encode(click,clickEntry))
 def changed=['MagicSkillWnd.OnClickButton','SummonedWnd.OnClickButton','MagicSkillWnd.HandleSkillList','MagicSkillWnd.OnClickItem']
 original.each{name,b->if(!(name in changed))assert Arrays.equals(b,byName(name).objectRawData):'Unrelated export changed '+name}
 println 'PASS: final native bypass dispatch, Next class, decoration guards; every unrelated export byte identical.'
}
