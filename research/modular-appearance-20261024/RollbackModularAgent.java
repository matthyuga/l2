import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.custom.ModularAppearance;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RollbackModularAgent {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Path root=Path.of(directory);for(var p:World.getPlayers())if(p.getClient()!=null)throw new IllegalStateException("Player client connected; rollback refused");
  List<Integer> ids=new ArrayList<>();
  try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT DISTINCT charId FROM character_variables WHERE var='MODULAR_BEFORE_V1' OR (var='MODULAR_APPEARANCE_V1' AND val='true')");var rs=ps.executeQuery()){while(rs.next())ids.add(rs.getInt(1));}
  for(int id:ids){
   Player p=World.getPlayer(id);boolean detached=p==null;if(detached)p=Player.load(id);if(p==null)throw new IllegalStateException("Cannot restore affected character "+id);
   if(ModularAppearance.canRestore(p))ModularAppearance.restore(p);
   p.getVariables().remove(ModularAppearance.ENABLED);p.getVariables().remove(ModularAppearance.BODY);p.getVariables().saveNow();p.storeMe();if(detached)p.stopVitalityTask();
  }
  Map<String,Class<?>> loaded=new HashMap<>();for(var c:inst.getAllLoadedClasses())loaded.put(c.getName(),c);
  List<ClassDefinition> definitions=new ArrayList<>();
  try(var files=Files.walk(root.resolve("rollback-classes"))){for(Path file:files.filter(p->p.toString().endsWith(".class")).toList()){
   String name=root.resolve("rollback-classes").relativize(file).toString().replace('\\','.').replace('/','.').replaceAll("\\.class$","");Class<?> type=loaded.get(name);if(type==null)throw new IllegalStateException("Missing live rollback class "+name);definitions.add(new ClassDefinition(type,Files.readAllBytes(file)));
  }}
  if(definitions.size()!=6)throw new IllegalStateException("Incomplete live rollback");
  var voices=VoicedCommandHandler.getInstance();var body=voices.getHandler("cuerpo");if(body!=null)voices.removeHandler(body);
  inst.redefineClasses(definitions.toArray(ClassDefinition[]::new));Files.writeString(root.resolve("live-rollback-proof.txt"),"PASS: original six live classes restored; .cuerpo removed; "+ids.size()+" modular profiles returned to legacy mode.\n");
 }
}
