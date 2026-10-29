import java.lang.instrument.Instrumentation;
import java.net.*;
import java.nio.file.*;
import java.lang.reflect.*;
public class VerifyRoomUi {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  URL[] paths={Path.of(dir,"compiled").toUri().toURL(),Path.of("E:/l2-local/research/pvp-room-bots/compiled").toUri().toURL(),Path.of("E:/l2-local/research/pvp-room-bots/startup-script-check").toUri().toURL()};
  try(URLClassLoader loader=new URLClassLoader(paths,ClassLoader.getSystemClassLoader()){
   @Override protected Class<?> loadClass(String name,boolean resolve)throws ClassNotFoundException{
    synchronized(getClassLoadingLock(name)){
     Class<?> type=findLoadedClass(name);if(type==null){if(name.startsWith("custom.ElvenPvpRoom."))type=findClass(name);else type=super.loadClass(name,false);}if(resolve)resolveClass(type);return type;
    }
   }
  }){
   try{
    loader.loadClass("custom.ElvenPvpRoom.UiIntegrationCheck").getMethod("run",String.class).invoke(null,dir);
    loader.loadClass("custom.ElvenPvpRoom.BotIntegrationCheck").getMethod("run",String.class).invoke(null,dir);
   }catch(InvocationTargetException e){throw new RuntimeException(e.getCause());}
  }
 }
}
