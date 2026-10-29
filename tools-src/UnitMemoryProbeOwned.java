import java.lang.instrument.*;
import java.lang.reflect.*;
import java.lang.management.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.entity.item.instance.Item;

/** Bounded observer. No class redefinition, GC request, spawn, combat, or human loading. */
public class UnitMemoryProbeOwned {
 static Instrumentation instrument;
 static final Map<Class<?>,List<Field>> fields=new HashMap<>();
 static final String HEADER="category,name,template,state,shallow_bytes,local_graph_bytes,objects,omitted_edges,inaccessible_fields,capped,milliseconds\n";
 static Class<?> find(String n){return Arrays.stream(instrument.getAllLoadedClasses()).filter(c->c.getName().equals(n)).findFirst().orElseThrow();}
 static String category(WorldObject o){
  if(o instanceof Player p)return p.getName().startsWith("Arena")?"bot_player":"human_player";
  if(o instanceof Summon)return "summon";
  if(o.getClass().getName().contains("GiranGuardians$Guardian"))return "custom_guardian";
  if(o instanceof Defender)return "native_defender";
  if(o instanceof Monster m)return m.getId()>=900000?"custom_monster":"monster";
  if(o instanceof Npc n){String type=n.getClass().getSimpleName();return type.contains("Merchant")||type.contains("Teleporter")||type.equals("Folk")?"simple_npc":"other_npc";}
  return "other";
 }
 static boolean boundary(Object value,Object root){
  if(value==root)return false;Class<?> c=value.getClass();String n=c.getName();
  if(value instanceof WorldObject&&!(value instanceof Item))return true;
  if(value instanceof Class<?>||value instanceof ClassLoader||value instanceof Thread||value instanceof Enum<?>||value instanceof Executor)return true;
  if(n.equals("java.lang.Integer")||n.equals("java.lang.Long")||n.equals("java.lang.Double")||n.equals("java.lang.Float")||n.equals("java.lang.Boolean")||n.equals("java.lang.Byte")||n.equals("java.lang.Short")||n.equals("java.lang.Character"))return true;
  return n.startsWith("org.l2jmobius.gameserver.entity.actor.templates.")||n.startsWith("org.l2jmobius.gameserver.entity.item.templates.")||n.startsWith("org.l2jmobius.gameserver.data.")||n.startsWith("org.l2jmobius.gameserver.managers.")||n.startsWith("org.l2jmobius.gameserver.taskmanagers.")||value instanceof org.l2jmobius.gameserver.mechanics.script.Script||n.equals("org.l2jmobius.gameserver.mechanics.skill.Skill")||n.contains(".entity.clan.")||n.contains(".entity.groups.")||n.contains(".entity.spawns.")||n.contains(".mechanics.siege.")||n.contains(".mechanics.zone.")||n.endsWith("WorldRegion")||n.endsWith("GameClient")||n.startsWith("java.util.logging.")||n.startsWith("java.lang.invoke.")||n.startsWith("java.lang.reflect.")||n.startsWith("sun.")||n.startsWith("jdk.");
 }
 static List<Field> refs(Class<?> cls){return fields.computeIfAbsent(cls,c->{List<Field> result=new ArrayList<>();for(Class<?> cur=c;cur!=null;cur=cur.getSuperclass())for(Field f:cur.getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())&&!f.getType().isPrimitive())result.add(f);return result;});}
 static String csv(String s){return '"'+s.replace("\"","\"\"")+'"';}
 static String measure(WorldObject root,String state){
  long start=System.nanoTime(),size=0;int omitted=0,inaccessible=0;boolean capped=false;
  Set<Object> seen=Collections.newSetFromMap(new IdentityHashMap<>());ArrayDeque<Object> queue=new ArrayDeque<>();queue.add(root);
  while(!queue.isEmpty()){
   if(seen.size()>=50000||System.nanoTime()-start>200_000_000L){capped=true;break;}
   Object o=queue.removeFirst();if(!seen.add(o))continue;size+=instrument.getObjectSize(o);Class<?> cls=o.getClass();
   if(cls.isArray()){if(!cls.getComponentType().isPrimitive())for(int j=0;j<Array.getLength(o);j++){Object v=Array.get(o,j);if(v!=null){if(boundary(v,root))omitted++;else if(!seen.contains(v))queue.add(v);}}}
   else for(Field f:refs(cls)){try{if(!f.trySetAccessible()){inaccessible++;continue;}Object v=f.get(o);if(v!=null){if(boundary(v,root))omitted++;else if(!seen.contains(v))queue.add(v);}}catch(Throwable e){inaccessible++;}}
  }
  int id=root instanceof Npc n?n.getId():0;return category(root)+","+csv(root.getName())+","+id+","+state+","+instrument.getObjectSize(root)+","+size+","+seen.size()+","+omitted+","+inaccessible+","+capped+","+(System.nanoTime()-start)/1e6+"\n";
 }
 public static void agentmain(String dir,Instrumentation i){instrument=i;
  Module target=UnitMemoryProbeOwned.class.getModule();Map<String,Set<Module>> opens=new HashMap<>();for(String p:new String[]{"java.lang","java.lang.ref","java.util","java.util.concurrent","java.util.concurrent.atomic","java.util.concurrent.locks","java.time","java.math"})opens.put(p,Set.of(target));i.redefineModule(Object.class.getModule(),Set.of(),Map.of(),opens,Set.of(),Map.of());
  Thread t=new Thread(()->run(Path.of(dir)),"UnitMemoryProbeOwned-observer");t.setDaemon(true);t.start();
 }
 static void run(Path dir){try{
  Files.createDirectories(dir);StringBuilder csv=new StringBuilder(HEADER);Map<String,Integer> counts=new TreeMap<>(),sampled=new HashMap<>();Set<Integer> templates=new HashSet<>();List<WorldObject> snapshot=new ArrayList<>();for(WorldObject o:World.getVisibleObjects())snapshot.add(o);
  for(WorldObject o:snapshot){String c=category(o);counts.merge(c,1,Integer::sum);if(c.equals("other")||sampled.getOrDefault(c,0)>=(c.equals("monster")?30:5))continue;if(c.equals("monster")&&o instanceof Npc n&&!templates.add(n.getId()))continue;if(o instanceof Creature creature&&creature.isDead())continue;csv.append(measure(o,o instanceof Creature cr&&cr.isInCombat()?"combat":"idle"));sampled.merge(c,1,Integer::sum);}
  // Only when no reserved pilot is in use: inspect saved technical profiles, never enter/spawn them.
  boolean claimed=false;Class<?> arena=find("custom.SoloArenaGauntlet.SoloArenaGauntlet");List<Player> loaded=new ArrayList<>();
  try{if(sampled.getOrDefault("bot_player",0)==0){claimed=(boolean)arena.getMethod("tryClaimPilot").invoke(null);if(claimed){Class<?> gr=find("custom.GiranSiegeLab.GiranRoster");var load=gr.getDeclaredMethod("load",String.class);load.setAccessible(true);for(String name:new String[]{"Darius","Nerys","Darion","Zareth","Arden"}){Player p=(Player)load.invoke(null,name);loaded.add(p);csv.append(measure(p,"offline_profile_not_spawned"));}}}}
  finally{if(!loaded.isEmpty()){var dispose=find("custom.GiranSiegeLab.GiranRoster").getDeclaredMethod("dispose",Player.class);dispose.setAccessible(true);for(Player p:loaded)dispose.invoke(null,p);}if(claimed)arena.getMethod("releasePilot").invoke(null);}
  Files.writeString(dir.resolve("units.csv"),csv);Files.writeString(dir.resolve("census.txt"),"utc="+java.time.Instant.now()+"\nworld_counts="+counts+"\nsamples="+sampled+"\nTechnical samples="+loaded.size()+";unspawned and unloaded\n");
  var memory=ManagementFactory.getMemoryMXBean().getHeapMemoryUsage();Files.writeString(dir.resolve("heap.txt"),"used="+memory.getUsed()+"\ncommitted="+memory.getCommitted()+"\nmax="+memory.getMax()+"\n");
  System.err.println("UNIT_MEMORY_PROBE PASS report="+dir+";bounded local graphs;no spawn/combat/GC/human changes;temporary profiles cleaned");
 }catch(Throwable e){System.err.println("UNIT_MEMORY_PROBE FAILED");e.printStackTrace();}}
}
