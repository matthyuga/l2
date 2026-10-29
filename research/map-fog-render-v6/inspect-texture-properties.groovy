import acmi.l2.clientmod.io.*
new UnrealPackage(new File('E:/l2/system-hud/Engine.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.startsWith('Texture.')&&it.fullClassName.endsWith('Property')}.each{println it.objectInnerFullName+' '+it.fullClassName}
 println 'MAPPING NAMES: '+up.nameTable.collect{it.name}.findAll{it.toLowerCase().contains('mapping')}
}
