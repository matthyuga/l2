import java.lang.instrument.Instrumentation;
import java.net.*;
import java.nio.file.*;
import java.lang.reflect.*;
public class VerifySiegeBots {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  URL[] urls={Path.of(dir,"compiled").toUri().toURL(),Path.of("E:/l2-local/research/pvp-room-ui/startup-script-check").toUri().toURL()};
  try(URLClassLoader loader=new URLClassLoader(urls,ClassLoader.getSystemClassLoader()){
   protected Class<?> loadClass(String name,boolean resolve)throws ClassNotFoundException{synchronized(getClassLoadingLock(name)){Class<?> type=findLoadedClass(name);if(type==null)type=name.startsWith("custom.ElvenPvpRoom.")?findClass(name):super.loadClass(name,false);if(resolve)resolveClass(type);return type;}}
  }){try{loader.loadClass("custom.ElvenPvpRoom.SiegeBotCheck").getMethod("run",String.class).invoke(null,dir);}catch(InvocationTargetException e){throw new RuntimeException(e.getCause());}}
 }
}
