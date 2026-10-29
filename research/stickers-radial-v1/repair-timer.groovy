import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
import java.nio.ByteBuffer
import java.nio.ByteOrder

def stage=new File(args[0]),client=new File(stage.parentFile.parentFile.parentFile,'l2/system-hud')
def input=new File(client,'Interface.u'),out=new File(stage,'Interface.u')
def saved=new File(stage,'timer-crash-v1/Interface.u');saved.parentFile.mkdirs()
assert !saved.exists():'Crash snapshot already exists; inspect before reapplying'
saved.bytes=input.bytes;out.bytes=input.bytes
def ser=new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx']))
new UnrealPackage(out,false).withCloseable{up->
 def original=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 def e=up.exportTable.find{it.objectInnerFullName=='StickerRadialUI.OnTimer'}
 def fn=ser.getOrCreateObject(e),context=new UnrealRuntimeContext(e,ser),ctx=new BytecodeContext(context)
 def ref=up.importTable.find{it.objectFullName=='NWindow.UIScript.IsKeyDown'}
 def nativeFn=ser.getOrCreateObject(ref)
 assert nativeFn.child.entry.fullClassName=='Core.ByteProperty'
 int changed=0
 fn.bytecode.findAll{it instanceof JumpIfNot && it.condition instanceof FinalFunction}.each{t->
  def call=t.condition
  if(call.funcRef==ref.objectReference){
   assert call.params.size()==1 && call.params[0] instanceof IntConstByte
   int value=call.params[0].value;assert value in [27,18,69]
   call.params[0]=new ByteConst(value);changed++
  }
 }
 assert changed==3
 // EX_ByteConst and EX_IntConstByte have equal VM/serialized sizes. All jump
 // targets and other instructions must therefore remain at their original offsets.
 def b=new ByteArrayOutputStream(),stream=new ObjectOutputStream(b,up.file.charset,0,ser,context)
 ser.forClass(fn.class).writeObject(fn,stream);if(fn.unreadBytes?.length)b.write(fn.unreadBytes)
 byte[] raw=b.toByteArray();int at=0
 7.times{int first=raw[at++]&255;if(first&64){int n;do{n=raw[at++]&255}while(n&128)}}
 at+=8;ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN).putInt(at,fn.bytecode.sum{it.getSize(ctx)} as int)
 byte[] before=e.objectRawData
 assert raw.length==before.length
 def differences=(0..<raw.length).findAll{raw[it]!=before[it]}
 assert differences.size()==3: differences
 assert differences.every{(before[it]&255)==0x2c && (raw[it]&255)==0x24}
 e.setObjectRawData(raw)
 original.each{n,bytes->if(n!=e.objectInnerFullName)assert Arrays.equals(bytes,up.exportTable.find{it.objectInnerFullName==n}.objectRawData)}
 println 'PASS: IsKeyDown native enum signature verified as byte; exactly 3 opcode bytes changed, 0x2c IntConstByte -> 0x24 ByteConst; all VM offsets and all other exports identical.'
}
