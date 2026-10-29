import java.nio.file.*;
import java.util.*;
import jdk.jfr.consumer.*;
public class ReadAgiteJfr {
 public static void main(String[] args)throws Exception{
  Map<String,Long> counts=new TreeMap<>(),waits=new TreeMap<>();long total=0,driver=0;
  try(var f=new RecordingFile(Path.of(args[0]))){while(f.hasMoreEvents()){
   var e=f.readEvent();total++;String type=e.getEventType().getName();
   if(!Set.of("jdk.ExecutionSample","jdk.ThreadPark","jdk.SocketRead","jdk.SocketWrite","jdk.FileWrite","jdk.FileRead","jdk.JavaMonitorEnter").contains(type))continue;
   var t=e.getThread(type.equals("jdk.ExecutionSample")?"sampledThread":"eventThread");if(t==null||!t.getJavaName().contains("AgiteCapacity"))continue;
   driver++;var stack=e.getStackTrace();if(stack==null)continue;
   List<String> frames=new ArrayList<>();for(var frame:stack.getFrames())frames.add(frame.getMethod().getType().getName()+"."+frame.getMethod().getName());
   if(!type.equals("jdk.ExecutionSample")&&e.getDuration().toMillis()>500&&frames.stream().anyMatch(s->s.endsWith(".phase")))System.out.println("LONG_PHASE_WAIT "+e.getStartTime()+" "+type+" "+e.getDuration().toMillis()+"ms "+frames);
   String key=frames.stream().filter(s->s.contains("restoreExperience")||s.contains("giveAvailableSkills")||s.contains("storeSkills")||s.contains("getConnection")||s.contains("findPath")||s.contains("deleteCharByObjId")||s.contains("Player.store")).findFirst().orElse(frames.isEmpty()?"none":frames.get(0));
   counts.merge(type+" "+key,1L,Long::sum);if(!type.equals("jdk.ExecutionSample"))waits.merge(type+" "+key,e.getDuration().toNanos(),Long::sum);
  }}
  System.out.println("events="+total+" driverEvents="+driver);counts.entrySet().stream().sorted(Map.Entry.<String,Long>comparingByValue().reversed()).limit(25).forEach(e->System.out.println(e.getKey()+" count="+e.getValue()+" waitMs="+waits.getOrDefault(e.getKey(),0L)/1e6));
 }
}
