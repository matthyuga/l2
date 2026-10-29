import acmi.l2.clientmod.io.UnrealPackage
new UnrealPackage(new File('E:/l2/system-hud/NWindow.u'),true).withCloseable{up->up.exportTable.findAll{it.objectInnerFullName.contains('RequestBypassToServer')||it.objectInnerFullName=='UIScript.OnClickButton'}.each{println it.objectInnerFullName+' '+it.fullClassName}}
