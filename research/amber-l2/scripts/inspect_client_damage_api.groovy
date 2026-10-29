import acmi.l2.clientmod.io.UnrealPackage
def client=new File(args[0])
for(String file:['NWindow.u'])new UnrealPackage(new File(client,'system-hud/'+file),true).withCloseable{up->
 println file
 up.exportTable.findAll{it.objectInnerFullName==~/(?i).*(damage|floating|drawtext|screenpos|project|worldtoscreen|effectspawn|showeffect).*/}.each{println it.objectInnerFullName+' '+it.fullClassName}
 up.nameTable.findAll{it.name==~/(?i).*(damage|floating|worldtoscreen).*/}.each{println 'NAME '+it.name}
}
