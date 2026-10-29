import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.core.Function
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
import java.nio.ByteBuffer
import java.nio.ByteOrder

def stage=new File(args[0]),client=new File(stage.parentFile.parentFile.parentFile,'l2/system-hud')
def buttonOnly=new File(stage,'input-mode.json').exists() && new File(stage,'input-mode.json').text.contains('"button-only"')
def output=new File(stage,'Interface.u');output.bytes=new File(stage,'current/Interface.u').bytes
def ser=new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx']))
def fresh={entry->new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx'])).getOrCreateObject(entry)}
def encode={obj,entry->
 def out=new ByteArrayOutputStream(),context=new UnrealRuntimeContext(entry,ser)
 def stream=new ObjectOutputStream(out,entry.unrealPackage.file.charset,0,ser,context)
 ser.forClass(obj.class).writeObject(obj,stream);if(obj.unreadBytes?.length)out.write(obj.unreadBytes)
 byte[] b=out.toByteArray()
 if(obj instanceof Function){
  assert obj.@properties.empty
  int at=0;7.times{int first=b[at++]&255;if(first&64){int n;do{n=b[at++]&255}while(n&128)}}
  at+=8;int size=obj.bytecode.sum{it.getSize(new BytecodeContext(context))}?:0
  ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).putInt(at,size)
 }
 b
}
new UnrealPackage(output,false).withCloseable { up ->
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 assert !byName('StickerRadialUI'):'Already installed'
 def original=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 def names=['StickerRadialUI','m_Held','OnLoad','OnEvent','OnTimer','OnClickButton','ToggleWheel','strID','Event_ID','TimerID','ShowWindow','HideWindow','SetFocus','IsShowWindow','SetUITimer','KillUITimer','RegisterEvent']
 up.addNameEntries(names.collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['NWindow.UIAPI_WINDOW':'Core.Class','NWindow.UIScript.IsKeyDown':'Core.Function','NWindow.UIScript.RequestBypassToServer':'Core.Function'])
 def nativeRef={n->def e=up.importTable.find{it.objectFullName==n};assert e; e.objectReference}
 def clazzTemplate=byName('TutorialViewerWnd')
 assert Arrays.equals(encode(ser.getOrCreateObject(clazzTemplate),clazzTemplate),clazzTemplate.objectRawData):'Class roundtrip failed'
 up.addExportEntry('StickerRadialUI','Core.Class',clazzTemplate.objectSuperClass.objectFullName,clazzTemplate.objectRawData,clazzTemplate.objectFlags)
 // Allocate the complete export graph BEFORE retaining entry references: addExportEntry
 // rebuilds the table, invalidating references retained across further allocations.
 def fieldTemplate=byName('MagicSkillWnd.m_bShow');assert fieldTemplate
 up.addExportEntry('StickerRadialUI.m_Held','Core.BoolProperty',null,fieldTemplate.objectRawData,fieldTemplate.objectFlags)
 def signatures=['OnLoad':null,'ToggleWheel':null,'OnEvent':'Event_ID','OnTimer':'TimerID','OnClickButton':'strID']
 signatures.each{name,paramType->
  def template=byName('MagicSkillWnd.OnLoad')
  up.addExportEntry('StickerRadialUI.'+name,'Core.Function',null,template.objectRawData,template.objectFlags)
  if(paramType){
   def old=byName(paramType=='strID'?'MagicSkillWnd.OnClickButton.strID':'MagicSkillWnd.OnEvent.Event_ID')
   up.addExportEntry('StickerRadialUI.'+name+'.'+paramType,old.fullClassName,null,old.objectRawData,old.objectFlags)
  }
  if(name=='OnEvent'){
   def old=byName('MagicSkillWnd.OnEvent.param')
   up.addExportEntry('StickerRadialUI.OnEvent.param',old.fullClassName,null,old.objectRawData,old.objectFlags)
  }
 }
 clazzTemplate=byName('TutorialViewerWnd');fieldTemplate=byName('MagicSkillWnd.m_bShow')
 def classEntry=byName('StickerRadialUI'),clazz=fresh(clazzTemplate)
 clazz.entry=classEntry;clazz.friendlyName='StickerRadialUI';clazz.child=null;clazz.scriptText=null;clazz.cppText=null
 clazz.dependencies=[];clazz.@properties.clear()
 // Keep an explicit class super reference and no borrowed fields or defaults.
 clazz.superField=ser.getOrCreateObject(byName('UICommonAPI'))
 def fieldEntry=byName('StickerRadialUI.m_Held'),field=fresh(fieldTemplate)
 field.entry=fieldEntry;field.next=null;field.superField=null
 fieldEntry.setObjectRawData(encode(field,fieldEntry));clazz.child=field
 def held={->new BoolVariable(new InstanceVariable(fieldEntry.objectReference))}
 // EInputKey is a byte enum. IntConstByte emits a 32-bit integer result despite
 // its name; using it for a native byte parameter can overwrite native stack data.
 def key={int code->new FinalFunction(nativeRef('NWindow.UIScript.IsKeyDown'),new ByteConst(code))}
 def vcall={String n,List params=[]->new VirtualFunction(up.nameReference(n),params as Token[])}
 def make={String name,String paramType,Closure body->
  def template=byName('MagicSkillWnd.OnLoad')
  def entry=byName('StickerRadialUI.'+name),fn=fresh(template)
  fn.entry=entry;fn.friendlyName=name;fn.superField=null;fn.next=clazz.child;fn.child=null
  fn.scriptText=null;fn.cppText=null;fn.line=0;fn.textPos=0;fn.nativeIndex=0;fn.functionFlags=131074
  def param=null
  if(paramType){
   def old=byName(paramType=='strID'?'MagicSkillWnd.OnClickButton.strID':'MagicSkillWnd.OnEvent.Event_ID')
   def pe=byName('StickerRadialUI.'+name+'.'+paramType);param=fresh(old)
   param.entry=pe;param.next=null;param.superField=null
   if(name=='OnEvent'){
    def extraEntry=byName('StickerRadialUI.OnEvent.param'),extra=fresh(byName('MagicSkillWnd.OnEvent.param'))
    extra.entry=extraEntry;extra.next=null;extra.superField=null;extraEntry.setObjectRawData(encode(extra,extraEntry));param.next=extra
   }
   pe.setObjectRawData(encode(param,pe));fn.child=param
  }
  def context=new BytecodeContext(new UnrealRuntimeContext(entry,ser))
  def tokens=[]
  def api={String n,List params=[],int resultType=0->
   def call=vcall(n,params)
   new ClassContext(new ObjectConst(nativeRef('NWindow.UIAPI_WINDOW')),call.getSize(context),resultType,call)
  }
  def emit={Token t->tokens<<t}
  def guard={Token condition,Closure block->
   def jump=new JumpIfNot(condition:condition,targetOffset:0);tokens<<jump;block();jump.targetOffset=tokens.sum{it.getSize(context)}?:0
  }
  body(emit,guard,api,param==null?null:new LocalVariable(param.entry.objectReference))
  tokens<<new Return(new Nothing());fn.bytecode=tokens as Token[]
  entry.setObjectRawData(encode(fn,entry));clazz.child=fn
 }
 make('OnLoad',null){emit,guard,api,p->
  emit(vcall('RegisterEvent',[new IntConst(150)]));emit(vcall('RegisterEvent',[new IntConst(160)]))
  emit(api('HideWindow',[new StringConst('StickerRadialWnd')]))
 }
 make('ToggleWheel',null){emit,guard,api,p->
  guard(api('IsShowWindow',[new StringConst('StickerRadialWnd')],4)){
   emit(api('HideWindow',[new StringConst('StickerRadialWnd')]));emit(new Return(new Nothing()))
  }
  emit(api('ShowWindow',[new StringConst('StickerRadialWnd')]))
  emit(api('SetFocus',[new StringConst('StickerRadialWnd')]))
 }
 make('OnEvent','Event_ID'){emit,guard,api,p->
  guard(new NativeFunctionCall(154,p,new IntConst(150))){
   emit(new LetBool(held(),new False()));emit(api('HideWindow',[new StringConst('StickerRadialWnd')]))
   emit(api('ShowWindow',[new StringConst('StickerLauncherWnd')]))
   if(!buttonOnly)emit(api('SetUITimer',[new StringConst('StickerLauncherWnd'),new IntConst(7341),new IntConst(60)]))
  }
  guard(new NativeFunctionCall(154,p,new IntConst(160))){
   emit(new LetBool(held(),new False()));if(!buttonOnly)emit(api('KillUITimer',[new StringConst('StickerLauncherWnd'),new IntConst(7341)]))
   emit(api('HideWindow',[new StringConst('StickerRadialWnd')]))
   emit(api('HideWindow',[new StringConst('StickerLauncherWnd')]))
  }
 }
 make('OnTimer','TimerID'){emit,guard,api,p->
  if(buttonOnly)return
  guard(key(27)){emit(api('HideWindow',[new StringConst('StickerRadialWnd')]))}
  guard(key(18)){
   guard(key(69)){
    guard(new NativeFunctionCall(129,held())){emit(vcall('ToggleWheel'))}
    emit(new LetBool(held(),new True()));emit(new Return(new Nothing()))
   }
  }
  emit(new LetBool(held(),new False()))
 }
 make('OnClickButton','strID'){emit,guard,api,p->
  guard(new NativeFunctionCall(122,p,new StringConst('Open'))){emit(vcall('ToggleWheel'));emit(new Return(new Nothing()))}
  guard(new NativeFunctionCall(122,p,new StringConst('Close'))){emit(api('HideWindow',[new StringConst('StickerRadialWnd')]));emit(new Return(new Nothing()))}
  (0..<8).each{i->
   guard(new NativeFunctionCall(122,p,new StringConst('S'+i))){
    emit(api('HideWindow',[new StringConst('StickerRadialWnd')]))
    emit(new FinalFunction(nativeRef('NWindow.UIScript.RequestBypassToServer'),new StringConst('voice .sticker '+(i+1))))
    emit(new Return(new Nothing()))
   }
  }
 }
 classEntry.setObjectRawData(encode(clazz,classEntry))
 original.each{n,b->assert Arrays.equals(b,byName(n).objectRawData):'Previous export changed: '+n}
 println 'PASS: isolated StickerRadialUI class added, input='+ (buttonOnly?'button-only; no timers':'Alt+E edge-trigger and Esc cancel')+', 8 native bypass choices; ALL previous exports byte identical.'
}
