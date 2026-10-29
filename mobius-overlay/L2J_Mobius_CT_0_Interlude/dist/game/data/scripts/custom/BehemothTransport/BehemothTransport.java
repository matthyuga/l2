package custom.BehemothTransport;

import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.templates.NpcTemplate;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.*;
import org.l2jmobius.gameserver.mechanics.events.listeners.*;
import org.l2jmobius.gameserver.mechanics.events.returns.TerminateReturn;
import org.l2jmobius.gameserver.network.serverpackets.*;
import org.l2jmobius.gameserver.util.StatSet;
import static custom.BehemothTransport.SeatRules.Role.*;

/** Experimental two-player transport, opt-in via .behemoth; never auto-spawns. */
public final class BehemothTransport implements IVoicedCommandHandler
{
    static final int NPC_ID=902791, DISPLAY_ID=59091;
    private static final Logger LOG=Logger.getLogger(BehemothTransport.class.getName());
    private static final TerminateReturn BLOCK=new TerminateReturn(true,true,true);
    private static final Path RETURNS=Path.of("config/BehemothTransport-return.properties");
    private static BehemothTransport instance;
    static final class Trip
    {
        final Player owner;final Npc npc;final SeatRules.Seats seats=new SeatRules.Seats();
        final Set<Integer> invited=ConcurrentHashMap.newKeySet();
        Player driver,gunner;boolean closing;long lastSync,lastGuard;
        Trip(Player owner,Npc npc){this.owner=owner;this.npc=npc;}
    }
    private record Member(Trip trip,SeatRules.Role role,Player player) { }
    private final Map<Integer,Trip> owned=new ConcurrentHashMap<>(),byNpc=new ConcurrentHashMap<>();
    private final Map<Integer,Member> members=new ConcurrentHashMap<>();
    private final Properties returns=new Properties();
    private final ScheduledFuture<?> timer;

    private BehemothTransport() throws Exception
    {
        if(instance!=null)throw new IllegalStateException("Behemoth service already installed");
        if(NpcData.getInstance().getTemplate(NPC_ID)!=null)throw new IllegalStateException("Reserved Behemoth NPC ID already used");
        if(Files.exists(RETURNS))try(var in=Files.newInputStream(RETURNS)){returns.load(in);}
        instance=this;VoicedCommandHandler.getInstance().registerHandler(this);
        var players=Containers.Players();
        players.addListener(new FunctionEventListener(players,EventType.ON_CREATURE_ATTACK,(OnCreatureAttack e)->combat(e.getAttacker(),e.getTarget()),this));
        players.addListener(new FunctionEventListener(players,EventType.ON_CREATURE_SKILL_USE,(OnCreatureSkillUse e)->combat(e.getCaster(),e.getTarget()),this));
        players.addListener(new ConsumerEventListener(players,EventType.ON_PLAYER_LOGOUT,(OnPlayerLogout e)->logout(e.getPlayer()),this));
        players.addListener(new ConsumerEventListener(players,EventType.ON_PLAYER_LOGIN,(OnPlayerLogin e)->recover(e.getPlayer()),this));
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DEATH,(OnCreatureDeath e)->death(e.getTarget()),this));
        timer=ThreadPool.scheduleAtFixedRate(this::tick,100,100);
        Runtime.getRuntime().addShutdownHook(new Thread(()->{for(Trip t:List.copyOf(owned.values()))close(t,"Servidor detenido");},"BehemothSafeShutdown"));
        LOG.info("BEHEMOTH_TRANSPORT READY: opt-in .behemoth, GM-only summon, fixed driver/gunner seats; client adapter required");
        if(Boolean.getBoolean("lab.behemoth.verify")||Files.exists(Path.of("config/BehemothTransport-smoke.request")))ThreadPool.schedule(()->BehemothSmoke.run(this),20_000);
    }
    @Override public String[] getCommandList(){return new String[]{"behemoth"};}
    @Override public synchronized boolean onCommand(String command,Player p,String params)
    {
        if(p==null)return false;
        String[] a=(params==null?"":params.trim()).split("\\s+",2);
        String action=a[0].toLowerCase(Locale.ROOT);
        try
        {
            switch(action)
            {
                case "invocar" -> {if(!p.isGM())throw new IllegalStateException("La invocacion experimental esta reservada a GM en L2 Lab.");summon(p);}
                case "conducir" -> board(p,find(p),DRIVER);
                case "subir" -> board(p,find(p),GUNNER);
                case "bajar" -> leave(p,"Bajaste del Behemoth",true);
                case "parar" -> {Trip t=controlled(p);t.npc.stopMove(null);}
                case "guardar" -> {Trip t=owned.get(p.getObjectId());if(t==null)throw new IllegalStateException("No tenes un Behemoth invocado.");if(t.driver!=null||t.gunner!=null)throw new IllegalStateException("Primero deben bajar ambos ocupantes.");close(t,"Behemoth guardado");}
                case "permitir" -> {Trip t=owned.get(p.getObjectId());Player guest=a.length>1?World.getPlayer(a[1]):null;if(t==null||guest==null)throw new IllegalStateException("Usa .behemoth permitir Nombre con tu Behemoth invocado.");t.invited.add(guest.getObjectId());p.sendMessage("Pasajero autorizado: "+guest.getName());}
                case "recuperar" -> recover(p);
                case "estado" -> {Trip t=find(p);p.sendMessage("Behemoth: "+(t.npc.isMoving()?"en marcha":"detenido")+" | conductor: "+(t.driver==null?"libre":t.driver.getName())+" | atacante: "+(t.gunner==null?"libre":t.gunner.getName())+" | HP: "+(int)t.npc.getCurrentHp());}
                default -> p.sendMessage(".behemoth invocar | conducir | subir | bajar | parar | guardar | permitir Nombre | estado | recuperar");
            }
        }
        catch(Exception e){p.sendMessage(e.getMessage()==null?"No se pudo realizar la accion.":e.getMessage());}
        return true;
    }
    synchronized Trip summon(Player owner)
    {
        available(owner);if(owned.containsKey(owner.getObjectId()))throw new IllegalStateException("Ya tenes un Behemoth. Usa .behemoth estado.");
        if(owner.getInstanceId()!=0)throw new IllegalStateException("Esta prueba funciona en el mundo abierto de L2 Lab.");
        double angle=owner.getHeading()*Math.PI/32768.;int x=owner.getX()+(int)(100*Math.cos(angle)),y=owner.getY()+(int)(100*Math.sin(angle));
        GeoEngine geo=GeoEngine.getInstance();int z=geo.getHeight(x,y,owner.getZ());
        if(Math.abs(z-owner.getZ())>80 || !geo.canMoveToTarget(owner,x,y,z))throw new IllegalStateException("No hay espacio transitable delante del personaje.");
        StatSet s=new StatSet();s.set("id",NPC_ID);s.set("displayId",DISPLAY_ID);s.set("name","Behemoth");s.set("title","Transporte de dos ocupantes");
        s.set("level",80);s.set("type","Folk");s.set("usingServerSideName",true);s.set("usingServerSideTitle",true);s.set("randomWalk",false);s.set("randomAnimation",false);
        s.set("talkable",false);s.set("attackable",true);s.set("isAggressive",false);s.set("baseHpMax",20000);s.set("baseMpMax",1000);s.set("basePDef",500);s.set("baseMDef",500);s.set("baseRunSpd",110);s.set("baseWalkSpd",80);s.set("collisionRadius",63);s.set("collisionHeight",54);
        NpcTemplate template=new NpcTemplate(s);template.setSkills(Map.of());
        Npc npc=new Npc(template);npc.setAutoAttackable(true);npc.setInstanceId(owner.getInstanceId());npc.setHeading(owner.getHeading());npc.setName("BHM:0:0");npc.setTitle("Transporte de dos ocupantes");npc.spawnMe(x,y,z);npc.setCurrentHp(npc.getMaxHp());
        Trip t=new Trip(owner,npc);owned.put(owner.getObjectId(),t);byNpc.put(npc.getObjectId(),t);metadata(t);owner.sendMessage("Behemoth invocado. Usa .behemoth conducir y autoriza al pasajero con .behemoth permitir Nombre.");return t;
    }
    private void available(Player p)
    {
        if(!p.isOnline()||p.isAlikeDead()||p.isTeleporting()||p.isMounted()||p.isInVehicle()||p.inObserverMode()||p.isInStoreMode()||p.isProcessingTransaction()||p.isSitting()||p.isInCombat()||p.isCastingNow()||p.isAttackingNow()||p.hasSummon()||p.isOutOfControl()||p.isRooted()||p.isStunned()||p.isImmobilized())
            throw new IllegalStateException("Primero termina combate, movimientos especiales, tienda o invocaciones y queda de pie.");
        if(members.containsKey(p.getObjectId())||BehemothSeatSync.isSeated(p))throw new IllegalStateException("Ya ocupas un asiento.");
    }
    private Trip find(Player p)
    {
        Member m=members.get(p.getObjectId());if(m!=null)return m.trip();
        if(p.getTarget()!=null){Trip t=byNpc.get(p.getTarget().getObjectId());if(t!=null)return t;}
        Trip t=owned.get(p.getObjectId());if(t!=null)return t;
        throw new IllegalStateException("Selecciona el Behemoth al que queres subir.");
    }
    private Trip controlled(Player p)
    {
        Member m=members.get(p.getObjectId());if(m==null||m.role()!=DRIVER)throw new IllegalStateException("Solo el conductor puede pilotar.");return m.trip();
    }
    synchronized void board(Player p,Trip t,SeatRules.Role role)
    {
        if(!p.isLabControlled())throw new IllegalStateException("Montaje en revision: falta validar los asientos visuales. Tu personaje permanece libre.");
        available(p);if(t.closing||t.npc.isAlikeDead())throw new IllegalStateException("Montura no disponible.");
        if(!SeatRules.boardingRange(p.getX()-t.npc.getX(),p.getY()-t.npc.getY(),p.getZ()-t.npc.getZ(),p.getInstanceId()==t.npc.getInstanceId()))throw new IllegalStateException("Acercate al Behemoth.");
        if(t.npc.isMoving())throw new IllegalStateException("La montura debe detenerse para subir.");
        if(role==DRIVER&&p!=t.owner)throw new IllegalStateException("Solo el propietario puede conducir.");
        if(role==GUNNER&&p!=t.owner&&!t.invited.contains(p.getObjectId())&&(t.owner.getParty()==null||!t.owner.getParty().getMembers().contains(p)))throw new IllegalStateException("El propietario debe autorizarte o invitarte a su grupo.");
        if(role==GUNNER&&t.driver==null)throw new IllegalStateException("Primero debe subir el conductor.");
        if(!t.seats.board(role,p.getObjectId()))throw new IllegalStateException("Ese puesto esta ocupado.");
        Member member=new Member(t,role,p);
        if(!BehemothSeatSync.bind(p,destination->control(member,destination))){t.seats.leave(p.getObjectId());throw new IllegalStateException("El personaje ya tiene un asiento protegido.");}
        members.put(p.getObjectId(),member);if(role==DRIVER)t.driver=p;else t.gunner=p;
        try{saveGuard(p,t);p.stopMove(null);p.abortAttack();p.abortCast();sync(member);metadata(t);p.sendMessage(role==DRIVER?"Conductor: clic en el suelo para mover. .behemoth parar / bajar":"Atacante: podes seleccionar objetivos y combatir desde tu puesto. .behemoth bajar");}
        catch(RuntimeException e){leave(p,"No se pudo asegurar el puesto.",true);throw e;}
    }
    private synchronized void control(Member m,Location target)
    {
        Trip t=m.trip();Player p=m.player();if(members.get(p.getObjectId())!=m || t.closing)return;
        if(m.role()!=DRIVER)return;
        if(p.isAlikeDead()||p.isStunned()||p.isRooted()||p.isSleeping()||p.isOutOfControl()){t.npc.stopMove(null);return;}
        long dx=(long)target.getX()-t.npc.getX(),dy=(long)target.getY()-t.npc.getY();if(dx*dx+dy*dy>1600L*1600)return;
        GeoEngine geo=GeoEngine.getInstance();int z=geo.getHeight(target.getX(),target.getY(),t.npc.getZ());
        if(Math.abs(z-t.npc.getZ())>64 || !geo.canMoveToTarget(t.npc,target.getX(),target.getY(),z)){p.sendMessage("Ese recorrido no es transitable para la montura.");return;}
        t.npc.setRunning();t.npc.getAI().setIntentionMoveTo(new Location(target.getX(),target.getY(),z));
    }
    private void sync(Member m)
    {
        Trip t=m.trip();Player p=m.player();SeatRules.Point v=SeatRules.world(t.npc.getX(),t.npc.getY(),t.npc.getZ(),t.npc.getHeading(),m.role());
        p.setXYZ(v.x(),v.y(),v.z());if(m.role()==DRIVER)p.setHeading(t.npc.getHeading());
        p.revalidateZone(false);
        p.broadcastPacket(new ValidateLocation(p));
    }
    private void metadata(Trip t){t.npc.setName("BHM:"+t.seats.driver()+":"+t.seats.gunner());t.npc.broadcastInfo();}
    private synchronized void tick()
    {
        for(Trip t:List.copyOf(owned.values()))try
        {
            if(t.closing)continue;
            if(t.npc.isAlikeDead()||!t.owner.isOnline()||t.owner.getInstanceId()!=t.npc.getInstanceId()){close(t,"Montura retirada");continue;}
            for(Player p:new Player[]{t.driver,t.gunner})if(p!=null)
            {
                if(!p.isOnline()||p.isAlikeDead()||p.isTeleporting()||p.getInstanceId()!=t.npc.getInstanceId()||Math.abs((long)p.getX()-t.npc.getX())>400||Math.abs((long)p.getY()-t.npc.getY())>400)
                    leave(p,"Saliste del transporte",!p.isTeleporting()&&p.getInstanceId()==t.npc.getInstanceId());
            }
            if(t.driver==null)t.npc.stopMove(null);
            long now=System.nanoTime();if(now-t.lastSync>=200_000_000L){t.lastSync=now;for(Player p:new Player[]{t.driver,t.gunner})if(p!=null){Member m=members.get(p.getObjectId());if(m!=null)sync(m);}}
            if(now-t.lastGuard>=1_000_000_000L){t.lastGuard=now;for(Player p:new Player[]{t.driver,t.gunner})if(p!=null)saveGuard(p,t);}
        }
        catch(Throwable e){LOG.log(Level.SEVERE,"Behemoth tick failed; releasing its occupants",e);close(t,"Fallo de transporte");}
    }
    TerminateReturn combat(Creature actor,Creature target)
    {
        if(!(actor instanceof Player p))return null;Member m=members.get(p.getObjectId());if(m==null)return null;
        if(m.role()==DRIVER||target==m.trip().npc||target==m.trip().driver||target==m.trip().gunner)return BLOCK;
        return null; // Ordinary range, line of sight, PvP, cooldown and damage rules remain authoritative.
    }
    private SeatRules.Point landing(Player p,Trip t)
    {
        int side=p==t.gunner?-1:1;double a=t.npc.getHeading()*Math.PI/32768.+Math.PI/2;
        int x=t.npc.getX()+(int)(side*90*Math.cos(a)),y=t.npc.getY()+(int)(side*90*Math.sin(a));GeoEngine geo=GeoEngine.getInstance();int z=geo.getHeight(x,y,t.npc.getZ());
        if(Math.abs(z-t.npc.getZ())>64||!geo.canMoveToTarget(t.npc,x,y,z)){x=t.npc.getX();y=t.npc.getY();z=t.npc.getZ();}
        return new SeatRules.Point(x,y,z);
    }
    synchronized void leave(Player p,String reason,boolean reposition)
    {
        Member m=members.get(p.getObjectId());if(m==null)return;Trip t=m.trip();
        // Stopping is mandatory before releasing either fixed seat.
        t.npc.stopMove(null);SeatRules.Point ground=landing(p,t);members.remove(p.getObjectId(),m);BehemothSeatSync.unbind(p);t.seats.leave(p.getObjectId());
        if(m.role()==DRIVER)t.driver=null;else t.gunner=null;metadata(t);
        p.abortAttack();p.abortCast();p.stopMove(null);
        if(reposition){p.setXYZ(ground.x(),ground.y(),ground.z());p.broadcastPacket(new ValidateLocation(p));}
        if(!p.isLabControlled())
        {
            // Persist ground, never the elevated seat, including orderly logout.
            try{if(reposition)p.storeMe();returns.remove(Integer.toString(p.getObjectId()));writeReturns();}
            catch(Exception e){LOG.log(Level.WARNING,"Behemoth return guard retained for login recovery",e);}
        }
        p.sendMessage(reason);
        if(m.role()==DRIVER&&t.gunner!=null)leave(t.gunner,"El conductor bajo: transporte detenido",true);
    }
    synchronized void close(Trip t,String reason)
    {
        if(t==null||t.closing)return;t.closing=true;
        if(t.driver!=null)leave(t.driver,reason,true);if(t.gunner!=null)leave(t.gunner,reason,true);
        t.seats.close();owned.remove(t.owner.getObjectId(),t);byNpc.remove(t.npc.getObjectId(),t);t.npc.stopMove(null);t.npc.deleteMe();
    }
    synchronized void logout(Player p){Trip t=owned.get(p.getObjectId());if(t!=null)close(t,"Propietario desconectado");else leave(p,"Pasajero desconectado",true);}
    synchronized void death(Creature actor)
    {
        if(actor instanceof Npc npc){Trip t=byNpc.get(npc.getObjectId());if(t!=null)close(t,"La montura fue derrotada");}
        else if(actor instanceof Player p)leave(p,"Ocupante derrotado",true);
    }
    private synchronized void saveGuard(Player p,Trip t)
    {
        if(p.isLabControlled())return;SeatRules.Point v=landing(p,t);returns.setProperty(Integer.toString(p.getObjectId()),v.x()+","+v.y()+","+v.z()+","+t.npc.getInstanceId());writeReturns();
    }
    private void writeReturns()
    {
        try{Path tmp=RETURNS.resolveSibling(RETURNS.getFileName()+".tmp");try(var out=Files.newOutputStream(tmp)){returns.store(out,"Behemoth safe ground recovery - L2 Lab");}Files.move(tmp,RETURNS,StandardCopyOption.REPLACE_EXISTING);}
        catch(Exception e){throw new IllegalStateException("No se pudo guardar la recuperacion segura del transporte.",e);}
    }
    private synchronized void recover(Player p)
    {
        String value=returns.getProperty(Integer.toString(p.getObjectId()));if(value==null)return;
        try{String[] v=value.split(",");int x=Integer.parseInt(v[0]),y=Integer.parseInt(v[1]),z=Integer.parseInt(v[2]);if(Math.abs((long)x)>1_000_000||Math.abs((long)y)>1_000_000||Math.abs((long)z)>100_000)throw new IllegalStateException("Invalid recovery coordinate");
            if(members.containsKey(p.getObjectId()))return;p.setInstanceId(0);p.teleToLocation(x,y,z);p.storeMe();returns.remove(Integer.toString(p.getObjectId()));writeReturns();p.sendMessage("Posicion segura recuperada tras salir del Behemoth.");}
        catch(Exception e){LOG.log(Level.SEVERE,"Behemoth login recovery retained for retry",e);}
    }
    public static void main(String[] args) throws Exception {new BehemothTransport();}
}
