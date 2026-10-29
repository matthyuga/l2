import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import ct0.*
import acmi.l2.clientmod.util.IOUtil

def root=new File('E:/l2/system-hud')
def out=new File(args[0]);out.mkdirs()
def ser=new UnrealSerializerFactory(new Environment(root,['./*.u','../system/*.u']))
new UnrealPackage(new File(root,'Interface.u'),true).withCloseable{up->
 new File(out,'map-bytecode.txt').withPrintWriter('UTF-8'){p->
  up.exportTable.findAll{it.objectInnerFullName.toLowerCase().contains('minimap')}.each{e->
   p.println('\nEXPORT '+e.objectInnerFullName+' '+e.fullClassName)
   if(e.fullClassName=='Core.Function'){
    try{def fn=ser.getOrCreateObject(e);def ctx=new UnrealRuntimeContext(e,ser);fn.bytecode.each{p.println(it.toString(ctx))}}catch(Exception ex){p.println('PARSE_ERROR '+ex)}
   }
  }
 }
}
new UnrealPackage(new File(root,'NWindow.u'),true).withCloseable{up->
 new File(out,'map-api.txt').withPrintWriter('UTF-8'){p->
  up.exportTable.findAll{it.objectInnerFullName.toLowerCase().contains('minimap') || (it.objectInnerFullName.toLowerCase().contains('texture')&&it.fullClassName=='Core.Function')}.each{e->
   p.println(e.objectInnerFullName+' '+e.fullClassName)
   if(e.fullClassName=='Core.Function'){try{def fn=ser.getOrCreateObject(e);def f=fn.child;while(f){p.println(' PARAM '+f.entry.objectInnerFullName+' '+f.entry.fullClassName);f=f.next}}catch(Exception ex){p.println('PARSE_ERROR '+ex)}}
  }
 }
}
ExpandoMetaClass.enableGlobally()
InputStream.metaClass.readInt={->IOUtil.readInt(delegate)}
InputStream.metaClass.readString={->IOUtil.readString(delegate)}
InputStream.metaClass.readFloat={->IOUtil.readFloat(delegate)}
InputStream.metaClass.readBoolean={->IOUtil.readBoolean(delegate)}
def x=new XDAT();new File(root,'Interface.xdat').withInputStream{x.read(it)}
new File(out,'map-layout.txt').withPrintWriter('UTF-8'){p->
 Closure walk
 walk={o,int depth->p.println((' '*depth)+o.properties.findAll{k,v->k!='children'&&k!='class'});if(o.properties.containsKey('children'))o.children?.each{walk(it,depth+1)}}
 x.windows.findAll{it.name.toLowerCase().contains('minimap')}.each{walk(it,0)}
}
println 'Read-only map inspection complete: '+out
