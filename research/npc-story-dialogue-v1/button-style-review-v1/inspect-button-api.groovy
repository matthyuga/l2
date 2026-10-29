import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def root=new File('E:/l2/system-hud');def ser=new UnrealSerializerFactory(new Environment(root,['./*.u']))
new UnrealPackage(new File(root,'NWindow.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.startsWith('UIAPI_BUTTON.') && (it.fullClassName=='Core.Function'||it.fullClassName=='Core.Class')}.each{e->
 def fn=ser.getOrCreateObject(e);def ps=[];def f=fn.child;while(f){ps<<f.entry.objectInnerFullName+':'+f.entry.fullClassName;f=f.next};println e.objectInnerFullName+' '+ps
 }
}
