package custom.BehemothNativeRide;

import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.enums.CategoryType;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.templates.NpcTemplate;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
import org.l2jmobius.gameserver.network.serverpackets.*;
import org.l2jmobius.gameserver.util.StatSet;

/** First native driver test. Ride owns locomotion; there is NO remote NPC steering. */
public final class BehemothNativeRide implements IVoicedCommandHandler {
 static final int ID=59091;
 private static final Logger LOG=Logger.getLogger(BehemothNativeRide.class.getName());
 private static BehemothNativeRide instance;
 private final Map<Integer,Npc> offers=new ConcurrentHashMap<>();
 private final Map<Integer,Player> riders=new ConcurrentHashMap<>();
 private final Map<Integer,Player> owners=new ConcurrentHashMap<>();
 private final NpcTemplate template;
 public BehemothNativeRide() throws Exception {
  if(instance!=null)throw new IllegalStateException("Native Behemoth already loaded");
  var s=new StatSet();s.set("id",ID);s.set("displayId",ID);s.set("name","Behemoth");s.set("title","Prueba de conductor nativo");s.set("level",80);s.set("type","Folk");s.set("usingServerSideName",true);s.set("usingServerSideTitle",true);s.set("randomWalk",false);s.set("randomAnimation",false);s.set("talkable",false);s.set("attackable",false);s.set("baseHpMax",20000);s.set("baseMpMax",1000);s.set("basePDef",500);s.set("baseMDef",500);s.set("baseRunSpd",110);s.set("baseWalkSpd",80);s.set("collisionRadius",63);s.set("collisionHeight",54);
  template=new NpcTemplate(s);template.setSkills(Map.of());
  var f=NpcData.class.getDeclaredField("_npcs");f.setAccessible(true);
  @SuppressWarnings("unchecked") var templates=(Map<Integer,NpcTemplate>)f.get(NpcData.getInstance());
  if(templates.putIfAbsent(ID,template)!=null)throw new IllegalStateException("Reserved native mount id already registered");
  CategoryData.getInstance().getCategoryByType(CategoryType.STRIDER).add(ID);
  instance=this;VoicedCommandHandler.getInstance().registerHandler(this);
  ThreadPool.scheduleAtFixedRate(this::tick,500,500);
  Runtime.getRuntime().addShutdownHook(new Thread(()->{for(Player p:List.copyOf(riders.values()))release(p,"Servidor cerrando");for(Npc n:offers.values())n.deleteMe();},"Behemoth-native-release"));
  LOG.info("BEHEMOTH_NATIVE_RIDE READY: native Ride packet, driver only, no seat movement guard");
 }
 public String[] getCommandList(){return new String[]{"behemoth"};}
 public synchronized boolean onCommand(String command,Player p,String params){
  if(p==null)return false;String action=params==null?"":params.trim().split("\\s+",2)[0].toLowerCase(Locale.ROOT);
  try{switch(action){
   case "invocar" -> {if(!p.isGM())throw new IllegalStateException("Prueba reservada a GM en L2 Lab.");summon(p);}
   case "conducir" -> mount(p);
   case "bajar","recuperar" -> release(p,"Bajaste del Behemoth.");
   case "parar" -> {if(riders.get(p.getObjectId())!=p)throw new IllegalStateException("No estas montado en este Behemoth.");p.stopMove(null);}
   case "guardar" -> {release(p,"Behemoth retirado.");Npc n=offers.remove(p.getObjectId());owners.remove(p.getObjectId());if(n!=null)n.deleteMe();}
   case "estado" -> p.sendMessage(riders.get(p.getObjectId())==p?"Conductor nativo activo: clic para moverte, .behemoth bajar para salir.":"Sin montar. .behemoth invocar / conducir. Segundo puesto pendiente.");
   case "subir","permitir" -> p.sendMessage("Esta version prueba al conductor con montaje nativo. Segundo ocupante aun no habilitado.");
   default -> p.sendMessage(".behemoth invocar | conducir | parar | bajar | guardar | estado");
  }}catch(Exception e){p.sendMessage(e.getMessage()==null?"No se pudo completar la accion.":e.getMessage());}
  return true;
 }
 private void available(Player p){if(!p.isOnline()||p.isAlikeDead()||p.isTeleporting()||p.isMounted()||p.isInVehicle()||p.inObserverMode()||p.hasSummon()||p.isInCombat()||p.isAttackingNow()||p.isCastingNow()||p.isInStoreMode()||p.isProcessingTransaction()||p.isSitting()||p.isOutOfControl()||p.isRooted()||p.isStunned()||p.isImmobilized()||BehemothSeatSync.isSeated(p))throw new IllegalStateException("Queda de pie, fuera de combate, sin otra montura ni invocacion.");}
 synchronized Npc summon(Player p){available(p);if(p.getInstanceId()!=0)throw new IllegalStateException("Prueba en el mundo principal.");if(offers.containsKey(p.getObjectId()))throw new IllegalStateException("Ya hay un Behemoth invocado: acercate y usa .behemoth conducir.");
  double a=p.getHeading()*Math.PI/32768.;int x=p.getX()+(int)(100*Math.cos(a)),y=p.getY()+(int)(100*Math.sin(a));int z=GeoEngine.getInstance().getHeight(x,y,p.getZ());if(Math.abs(z-p.getZ())>64||!GeoEngine.getInstance().canMoveToTarget(p,x,y,z))throw new IllegalStateException("Busca suelo plano y despejado.");
  Npc npc=new Npc(template);npc.setName("Behemoth");npc.setTitle("Conductor nativo - L2 Lab");npc.setHeading(p.getHeading());npc.setAutoAttackable(false);npc.spawnMe(x,y,z);offers.put(p.getObjectId(),npc);owners.put(p.getObjectId(),p);p.sendMessage("Behemoth preparado. Acercate y usa .behemoth conducir. Prueba de un conductor.");return npc;
 }
 synchronized void mount(Player p){available(p);Npc npc=offers.get(p.getObjectId());if(npc==null)throw new IllegalStateException("Primero usa .behemoth invocar.");if(p.getInstanceId()!=npc.getInstanceId()||Math.abs(p.getZ()-npc.getZ())>100||Math.hypot(p.getX()-npc.getX(),p.getY()-npc.getY())>200)throw new IllegalStateException("Acercate al Behemoth.");
  p.stopMove(null);riders.put(p.getObjectId(),p);
  try{if(!p.mount(ID,0,false)||!p.isMounted()||p.getMountNpcId()!=ID)throw new IllegalStateException("No se pudo activar la montura nativa.");offers.remove(p.getObjectId());npc.deleteMe();NativeRideMotion.begin(p);p.sendMessage("Conductor nativo activo. Clic en el suelo para moverte; .behemoth bajar para salir.");}
  catch(RuntimeException e){riders.remove(p.getObjectId());if(p.getMountNpcId()==ID)clearMount(p);throw e;}
 }
 private void clearMount(Player p){NativeRideMotion.remove(p);p.stopMove(null);p.abortAttack();p.abortCast();p.setMount(0,0);p.setMountObjectID(0);p.broadcastPacket(new Ride(p));p.broadcastUserInfo();}
 synchronized void release(Player p,String message){boolean registered=riders.remove(p.getObjectId(),p);if(p.getMountNpcId()!=ID){if(registered)owners.remove(p.getObjectId());return;}clearMount(p);owners.remove(p.getObjectId());if(p.isOnline())p.sendMessage(message);}
 private synchronized void tick(){
  for(Player p:List.copyOf(riders.values()))try{if(!p.isOnline()||p.isAlikeDead()||p.getMountNpcId()!=ID||!p.isMounted()||p.getInstanceId()!=0)release(p,"Prueba finalizada: montura retirada.");else NativeRideMotion.tick(p);}catch(Throwable e){LOG.log(Level.WARNING,"Native Behemoth cleanup",e);release(p,"Montura retirada por fallo.");}
  for(var item:List.copyOf(owners.entrySet()))if(!riders.containsKey(item.getKey())&&!item.getValue().isOnline()){Npc npc=offers.remove(item.getKey());owners.remove(item.getKey());if(npc!=null)npc.deleteMe();}
 }
 public static void main(String[] args)throws Exception{new BehemothNativeRide();}
}
