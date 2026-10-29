import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
import java.nio.ByteBuffer
import java.nio.ByteOrder

def stage=new File(args[0]),client=new File(stage.parentFile.parentFile.parentFile,'l2/system-hud')
def input=new File(client,'Interface.u'),output=new File(stage,'Interface.u')
def saved=new File(stage,'timer-crash-v2/Interface.u');saved.parentFile.mkdirs()
assert !saved.exists():'Previous attempt exists; inspect before reapplying'
saved.bytes=input.bytes;output.bytes=input.bytes
def ser=new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx']))
def encode={fn,entry->
 def context=new UnrealRuntimeContext(entry,ser),ctx=new BytecodeContext(context)
 def out=new ByteArrayOutputStream(),stream=new ObjectOutputStream(out,entry.unrealPackage.file.charset,0,ser,context)
 ser.forClass(fn.class).writeObject(fn,stream);if(fn.unreadBytes?.length)out.write(fn.unreadBytes)
 byte[] raw=out.toByteArray();int at=0
 7.times{int first=raw[at++]&255;if(first&64){int n;do{n=raw[at++]&255}while(n&128)}}
 at+=8;ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN).putInt(at,(fn.bytecode.sum{it.getSize(ctx)}?:0) as int);raw
}
new UnrealPackage(output,false).withCloseable{up->
 def original=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 def timerEntry=byName('StickerRadialUI.OnTimer'),timer=ser.getOrCreateObject(timerEntry)
 timer.bytecode=[new Return(new Nothing())] as Token[]
 timerEntry.setObjectRawData(encode(timer,timerEntry))
 def entry=byName('StickerRadialUI.OnEvent'),fn=ser.getOrCreateObject(entry),context=new UnrealRuntimeContext(entry,ser),ctx=new BytecodeContext(context)
 def old=fn.bytecode.toList(),oldOffsets=[:];int before=0
 old.each{oldOffsets[it]=before;before+=it.getSize(ctx)}
 int oldEnd=before,now=0;def relocation=[:],tokens=[];int removed=0
 old.each{t->
  relocation[oldOffsets[t]]=now
  String text=t.toString(context)
  if(text.contains('.static.SetUITimer(')||text.contains('.static.KillUITimer(')){removed++}
  else{tokens<<t;now+=t.getSize(ctx)}
 }
 assert removed==2
 relocation[oldEnd]=now
 tokens.each{if(it instanceof JumpIfNot||it instanceof Jump){assert relocation.containsKey(it.targetOffset);it.targetOffset=relocation[it.targetOffset]}}
 fn.bytecode=tokens as Token[];entry.setObjectRawData(encode(fn,entry))
 original.each{n,b->if(!(n in ['StickerRadialUI.OnTimer','StickerRadialUI.OnEvent']))assert Arrays.equals(b,byName(n).objectRawData):n}
 println 'PASS: timer registration and cancellation removed, OnTimer is return-only, branches relocated; ALL other exports byte identical.'
}
