import ct0.*
import acmi.l2.clientmod.util.IOUtil
ExpandoMetaClass.enableGlobally()
InputStream.metaClass.readInt={->IOUtil.readInt(delegate)}
InputStream.metaClass.readString={->IOUtil.readString(delegate)}
InputStream.metaClass.readFloat={->IOUtil.readFloat(delegate)}
InputStream.metaClass.readBoolean={->IOUtil.readBoolean(delegate)}
def x=new XDAT();new File('E:/l2/system-hud/Interface.xdat').withInputStream{x.read(it)}
for(String name:['TutorialViewerWnd','MagicSkillWnd','StatusWnd','RadarMapWnd','MainMenuWnd','SystemMenuWnd','QuestAlarmWnd','ItemAnnounceWnd']){
 def w=x.windows.find{it.name==name};if(w){println name+' '+w.properties.findAll{k,v->k!='children'&&k!='class'};println 'CHILDREN '+w.children.collect{it.name}}
}
