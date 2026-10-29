import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.core.Function
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
import java.nio.ByteBuffer
import java.nio.ByteOrder

def stage=new File(args[0]),client=new File('E:/l2/system-hud')
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
 assert !byName('AmberButtonStylesUI'):'Already installed'
 def original=up.exportTable.collectEntries{[(it.objectInnerFullName):it.objectRawData]}
 def names=['AmberButtonStylesUI','m_Held','OnLoad','OnEvent','OnTimer','OnClickButton','ToggleWheel','strID','Event_ID','TimerID','ShowWindow','HideWindow','SetFocus','IsShowWindow','SetUITimer','KillUITimer','RegisterEvent']
 names.addAll(['CloseAll','ShowWelcome','ShowPlace','ShowGreeting','ShowEnd','UseOriginal','UseCompensation','UseOpaque','UseSemi','UseClear','UseStyleA','UseStyleB','UseStyleC','UseStyleD','SetTexture']);up.addNameEntries(names.collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['NWindow.UIAPI_WINDOW':'Core.Class','NWindow.UIAPI_TEXTURECTRL':'Core.Class','NWindow.ButtonHandle':'Core.Class','NWindow.ButtonHandle.SetTexture':'Core.Function','NWindow.UIScript.GetHandle':'Core.Function','NWindow.UIScript.IsKeyDown':'Core.Function','NWindow.UIScript.RequestBypassToServer':'Core.Function'])
 def nativeRef={n->def e=up.importTable.find{it.objectFullName==n};assert e; e.objectReference}
 def clazzTemplate=byName('TutorialViewerWnd')
 assert Arrays.equals(encode(ser.getOrCreateObject(clazzTemplate),clazzTemplate),clazzTemplate.objectRawData):'Class roundtrip failed'
 up.addExportEntry('AmberButtonStylesUI','Core.Class',clazzTemplate.objectSuperClass.objectFullName,clazzTemplate.objectRawData,clazzTemplate.objectFlags)
 // Allocate the complete export graph BEFORE retaining entry references: addExportEntry
 // rebuilds the table, invalidating references retained across further allocations.
 def fieldTemplate=byName('MagicSkillWnd.m_bShow');assert fieldTemplate
 up.addExportEntry('AmberButtonStylesUI.m_Held','Core.BoolProperty',null,fieldTemplate.objectRawData,fieldTemplate.objectFlags)
 def signatures=['OnLoad':null,'CloseAll':null,'ShowWelcome':null,'ShowPlace':null,'ShowGreeting':null,'ShowEnd':null,'UseOriginal':null,'UseCompensation':null,'UseOpaque':null,'UseSemi':null,'UseClear':null,'UseStyleA':null,'UseStyleB':null,'UseStyleC':null,'UseStyleD':null,'OnEvent':'Event_ID','OnClickButton':'strID']
 signatures.each{name,paramType->
  def template=byName('MagicSkillWnd.OnLoad')
  up.addExportEntry('AmberButtonStylesUI.'+name,'Core.Function',null,template.objectRawData,template.objectFlags)
  if(paramType){
   def old=byName(paramType=='strID'?'MagicSkillWnd.OnClickButton.strID':'MagicSkillWnd.OnEvent.Event_ID')
   up.addExportEntry('AmberButtonStylesUI.'+name+'.'+paramType,old.fullClassName,null,old.objectRawData,old.objectFlags)
  }
  if(name=='OnEvent'){
   def old=byName('MagicSkillWnd.OnEvent.param')
   up.addExportEntry('AmberButtonStylesUI.OnEvent.param',old.fullClassName,null,old.objectRawData,old.objectFlags)
  }
 }
 clazzTemplate=byName('TutorialViewerWnd');fieldTemplate=byName('MagicSkillWnd.m_bShow')
 def classEntry=byName('AmberButtonStylesUI'),clazz=fresh(clazzTemplate)
 clazz.entry=classEntry;clazz.friendlyName='AmberButtonStylesUI';clazz.child=null;clazz.scriptText=null;clazz.cppText=null
 clazz.dependencies=[];clazz.@properties.clear()
 // Keep an explicit class super reference and no borrowed fields or defaults.
 clazz.superField=ser.getOrCreateObject(byName('UICommonAPI'))
 def fieldEntry=byName('AmberButtonStylesUI.m_Held'),field=fresh(fieldTemplate)
 field.entry=fieldEntry;field.next=null;field.superField=null
 fieldEntry.setObjectRawData(encode(field,fieldEntry));clazz.child=field
 def held={->new BoolVariable(new InstanceVariable(fieldEntry.objectReference))}
 // EInputKey is a byte enum. IntConstByte emits a 32-bit integer result despite
 // its name; using it for a native byte parameter can overwrite native stack data.
 def key={int code->new FinalFunction(nativeRef('NWindow.UIScript.IsKeyDown'),new ByteConst(code))}
 def vcall={String n,List params=[]->new VirtualFunction(up.nameReference(n),params as Token[])}
 def make={String name,String paramType,Closure body->
  def template=byName('MagicSkillWnd.OnLoad')
  def entry=byName('AmberButtonStylesUI.'+name),fn=fresh(template)
  fn.entry=entry;fn.friendlyName=name;fn.superField=null;fn.next=clazz.child;fn.child=null
  fn.scriptText=null;fn.cppText=null;fn.line=0;fn.textPos=0;fn.nativeIndex=0;fn.functionFlags=131074
  def param=null
  if(paramType){
   def old=byName(paramType=='strID'?'MagicSkillWnd.OnClickButton.strID':'MagicSkillWnd.OnEvent.Event_ID')
   def pe=byName('AmberButtonStylesUI.'+name+'.'+paramType);param=fresh(old)
   param.entry=pe;param.next=null;param.superField=null
   if(name=='OnEvent'){
    def extraEntry=byName('AmberButtonStylesUI.OnEvent.param'),extra=fresh(byName('MagicSkillWnd.OnEvent.param'))
    extra.entry=extraEntry;extra.next=null;extra.superField=null;extraEntry.setObjectRawData(encode(extra,extraEntry));param.next=extra
   }
   pe.setObjectRawData(encode(param,pe));fn.child=param
  }
  def context=new BytecodeContext(new UnrealRuntimeContext(entry,ser))
  def tokens=[]
  def api={String n,List params=[],int resultType=0,String apiClass='NWindow.UIAPI_WINDOW'->
   def call=vcall(n,params)
   new ClassContext(new ObjectConst(nativeRef(apiClass)),call.getSize(context),resultType,call)
  }
  def emit={Token t->tokens<<t}
  def guard={Token condition,Closure block->
   def jump=new JumpIfNot(condition:condition,targetOffset:0);tokens<<jump;block();jump.targetOffset=tokens.sum{it.getSize(context)}?:0
  }

  def buttonApi={String path,List tex->
   def handle=new DynamicCast(nativeRef('NWindow.ButtonHandle'),new FinalFunction(nativeRef('NWindow.UIScript.GetHandle'),new StringConst(path)))
   def call=new FinalFunction(nativeRef('NWindow.ButtonHandle.SetTexture'),tex.collect{new StringConst(it)} as Token[])
   new acmi.l2.clientmod.unreal.bytecode.token.Context(handle,call.getSize(context),0,call)
  }
  body(emit,guard,api,param==null?null:new LocalVariable(param.entry.objectReference),buttonApi)

  tokens<<new Return(new Nothing());fn.bytecode=tokens as Token[]
  entry.setObjectRawData(encode(fn,entry));clazz.child=fn
 }

 def pages=['AmberStoryWelcomeWnd','AmberStoryPlaceWnd','AmberStoryGreetingWnd','AmberStoryEndWnd']
 make('CloseAll',null){emit,guard,api,p,buttonApi->pages.each{emit(api('HideWindow',[new StringConst(it)]))}}
 make('OnLoad',null){emit,guard,api,p,buttonApi->emit(vcall('RegisterEvent',[new IntConst(150)]));emit(vcall('RegisterEvent',[new IntConst(160)]));emit(vcall('CloseAll'));emit(api('HideWindow',[new StringConst('AmberStoryLauncherWnd')]))}
 ['ShowWelcome':pages[0],'ShowPlace':pages[1],'ShowGreeting':pages[2],'ShowEnd':pages[3]].each{fn,win->
  make(fn,null){emit,guard,api,p,buttonApi->emit(vcall('CloseAll'));emit(api('ShowWindow',[new StringConst(win)]));emit(api('SetFocus',[new StringConst(win)]))}
 }
 make('OnEvent','Event_ID'){emit,guard,api,p,buttonApi->
  guard(new NativeFunctionCall(154,p,new IntConst(150))){emit(vcall('CloseAll'));emit(api('ShowWindow',[new StringConst('AmberStoryLauncherWnd')]))}
  guard(new NativeFunctionCall(154,p,new IntConst(160))){emit(vcall('CloseAll'));emit(api('HideWindow',[new StringConst('AmberStoryLauncherWnd')]))}
 }

 ['UseOriginal':'NexusAmberStoryV1.Portrait','UseCompensation':'NexusAmberGammaV2.PortraitComp'].each{fn,tex->
  make(fn,null){emit,guard,api,p,buttonApi->pages.each{win->emit(api('SetTexture',[new StringConst(win+'.Portrait'),new StringConst(tex)],0,'NWindow.UIAPI_TEXTURECTRL'))}}
 }
 ['UseOpaque':'BackgroundOpaque','UseSemi':'BackgroundSemi','UseClear':'BackgroundClear'].each{fn,tex->
  make(fn,null){emit,guard,api,p,buttonApi->pages.each{win->emit(api('SetTexture',[new StringConst(win+'.Background'),new StringConst('NexusAmberAngularV3.'+tex)],0,'NWindow.UIAPI_TEXTURECTRL'))}}
 }

 ['A','B','C','D'].each{style->
  make('UseStyle'+style,null){emit,guard,api,p,buttonApi->
   pages.eachWithIndex{win,i->
    def controls=['Close','Original','Compensate','Opaque','Semi','Clear']
    if(i==0){controls.addAll(['Explore','Greet'])}else{controls.add(i==3 ? 'Restart' : 'Next')}
    controls.each{n->emit(buttonApi(win+'.'+n,['Up','Down','Over'].collect{'NexusAmberButtonsV5.'+style+n+it}))}
    emit(api('SetTexture',[new StringConst(win+'.StyleBadge'),new StringConst('NexusAmberButtonsV5.Current'+style)],0,'NWindow.UIAPI_TEXTURECTRL'))
   }
  }
 }
 make('OnClickButton','strID'){emit,guard,api,p,buttonApi->
  ['Open':'ShowWelcome','Explore':'ShowPlace','Greet':'ShowGreeting','Next':'ShowEnd','Restart':'ShowWelcome','Close':'CloseAll','Original':'UseOriginal','Compensate':'UseCompensation','Opaque':'UseOpaque','Semi':'UseSemi','Clear':'UseClear','StyleA':'UseStyleA','StyleB':'UseStyleB','StyleC':'UseStyleC','StyleD':'UseStyleD'].each{button,fn->
   guard(new NativeFunctionCall(122,p,new StringConst(button))){emit(vcall(fn));emit(new Return(new Nothing()))}
  }
 }
 classEntry.setObjectRawData(encode(clazz,classEntry))
 original.each{n,b->assert Arrays.equals(b,byName(n).objectRawData):'Previous export changed: '+n}
 println 'PASS: isolated AmberButtonStylesUI, 17 functions, 15 button routes, no timers/network calls; all previous exports byte identical.'
}
