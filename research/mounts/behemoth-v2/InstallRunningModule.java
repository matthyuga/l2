import java.lang.instrument.Instrumentation;
import java.net.URLClassLoader;
import java.nio.file.*;
import java.io.PrintWriter;
import java.io.StringWriter;
/** Loads only this newly built module; does not redefine existing core classes. */
public final class InstallRunningModule
{
    private static URLClassLoader loader;
    public static void agentmain(String directory,Instrumentation instrumentation) throws Exception
    {
        Path root=Path.of(directory);Path result=root.resolve("module-load.txt");
        try
        {
            if(loader!=null)throw new IllegalStateException("Module already installed by this agent");
            ClassLoader parent=Class.forName("org.l2jmobius.gameserver.GameServer").getClassLoader();
            loader=new URLClassLoader(new java.net.URL[]{root.resolve("behemoth-runtime.jar").toUri().toURL()},parent);
            Class.forName("custom.BehemothTransport.BehemothTransport",true,loader).getMethod("main",String[].class).invoke(null,(Object)new String[0]);
            Files.writeString(result,"READY: Behemoth module registered. No core classes redefined.\n");
        }
        catch(Throwable e){StringWriter text=new StringWriter();e.printStackTrace(new PrintWriter(text));Files.writeString(result,"FAIL: "+text);throw new RuntimeException(e);}
    }
}
