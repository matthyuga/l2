package custom.ElvenPvpRoom;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.instancezone.Instance;
import org.l2jmobius.gameserver.entity.instancezone.InstanceWorld;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.ExShowScreenMessage;
import org.l2jmobius.gameserver.network.serverpackets.TeleportToLocation;

/** Elven room lobby and authoritative boundary countdown. No build/resource edits. */
public class PvpRooms extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG = Logger.getLogger(PvpRooms.class.getName());
    public static final int NPC = 902600, TEMPLATE = 3051;
    public static final long EXIT_NANOS = 4_000_000_000L;
    // First playable perimeter: all nine existing fighters and the entry are inside.
    public static final int MIN_X=42000, MAX_X=49200, MIN_Y=46600, MAX_Y=54000;
    private final Map<Integer,Visit> visits = new ConcurrentHashMap<>();
    private final Map<Integer,Location> returns = new ConcurrentHashMap<>();
    private final Npc[] hosts = new Npc[2];

    private static final class Visit
    {
        Location lastInside;
        long exitStarted;
        boolean commandExit;
        int shownSegments=-1;
        Visit(Location location) { lastInside=location; }
    }

    public PvpRooms()
    {
        addStartNpc(NPC); addTalkId(NPC); addFirstTalkId(NPC);
        hosts[0]=host(83480,148120,-3406,32768);
        hosts[1]=host(149160,46700,12016,32768);
        VoicedCommandHandler.getInstance().registerHandler(this);
        ThreadPool.scheduleAtFixedRate(this::tick,100,100);
        LOG.info("PvpRooms: Elven lobby active in Giran/Gludio sky; 4 second vulnerable exit to Giran.");
    }

    private Npc host(int x,int y,int z,int heading)
    {
        int floor=GeoEngine.getInstance().getHeight(x,y,z);
        if(Math.abs(floor-z)>100) throw new IllegalStateException("Lobby floor missing: "+x+","+y+","+floor);
        return addSpawn(NPC,x,y,floor,heading,false,0,false,0);
    }

    @Override public String[] getCommandList() { return new String[]{"salas"}; }
    @Override public boolean onCommand(String command,Player p,String params)
    {
        String action=params==null?"":params.trim().toLowerCase(java.util.Locale.ROOT);
        switch(action)
        {
            case "elven", "entrar" -> enter(p);
            case "salir" -> requestExit(p);
            case "cancelar" -> cancelCommandExit(p);
            default -> { p.sendMessage("Salas PvP: habla con Salas PvP en Giran o en el muelle. .salas salir inicia 4 s; .salas cancelar cancela la salida por comando."); }
        }
        return true;
    }

    @Override public String onFirstTalk(Npc npc,Player p) { return menu(); }
    @Override public String onTalk(Npc npc,Player p) { return menu(); }
    @Override public String onEvent(String event,Npc npc,Player p)
    {
        if(npc==null || npc.getId()!=NPC || p.getInstanceId()!=npc.getInstanceId()
            || Math.abs(p.getZ()-npc.getZ())>200 || !p.isInsideRadius2D(npc,250)) return null;
        if("elven".equals(event)) { enter(p); return null; }
        return menu();
    }

    private String menu()
    {
        Instance room=room(false);
        int count=room==null?0:room.getPlayers().size();
        return "<html><body><center><font color=LEVEL>HELLGAMES - Salas PvP</font><br>"
            +"Elven Village - Todos contra todos<br>Jugadores: "+count+"<br>"
            +"<button value=\"Entrar a Elven\" action=\"bypass -h Quest PvpRooms elven\" width=200 height=28 back=\"L2UI_CT1.Button_DF_Down\" fore=\"L2UI_CT1.Button_DF\"><br>"
            +"Al cruzar el limite tenes 4 segundos para volver.<br>"
            +"Durante la salida seguis siendo vulnerable.<br>"
            +"Si volves, retornas a tu ultima posicion interior.<br>"
            +"Si llega a cero, regresas a Giran.<br>"
            +"Entrar no cura ni modifica tus efectos.<br>"
            +"Salida manual: .salas salir<br>Cancelar salida manual: .salas cancelar"
            +"</center></body></html>";
    }

    private Instance room(boolean create)
    {
        synchronized(InstanceManager.getInstance())
        {
            for(Instance instance:InstanceManager.getInstance().getInstances().values())
                if(instance!=null && instance.getTemplateId()==TEMPLATE) return instance;
            if(!create) return null;
            InstanceManager manager=InstanceManager.getInstance();
            if(manager.getInstanceTemplateFileName(TEMPLATE)==null) throw new IllegalStateException("Missing Elven template");
            Instance instance=manager.createDynamicInstance(TEMPLATE);
            InstanceWorld world=new InstanceWorld(); world.setInstance(instance); manager.addWorld(world);
            return instance;
        }
    }

    private synchronized void enter(Player p)
    {
        if(p.isDead() || p.isInCombat() || p.isTeleporting() || p.isMounted() || p.isFlying() || p.isInVehicle()
            || p.isInOlympiadMode() || p.isInDuel())
        { p.sendMessage("Para entrar debes estar vivo, desmontado y fuera de combate, duelo y Olympiad."); return; }
        Instance room=room(true);
        if(p.getInstanceId()==room.getId()) { p.sendMessage("Ya estas en Elven PvP."); return; }
        if(p.getInstanceId()!=0) { p.sendMessage("Primero sal de tu instancia actual."); return; }
        Location destination=safe(returns.getOrDefault(p.getObjectId(),new Location(45150,52100,-2792,49152)));
        visits.put(p.getObjectId(),new Visit(destination));
        InstanceWorld world=InstanceManager.getInstance().getWorld(room.getId());
        if(world!=null) world.addAllowed(p);
        travel(p,destination,room.getId());
        p.sendMessage("Elven PvP: cruzar el limite inicia 4 s de salida a Giran. No se restauraron recursos ni efectos.");
    }

    public static boolean inside(Location loc)
    {
        return loc.getX()>MIN_X && loc.getX()<MAX_X && loc.getY()>MIN_Y && loc.getY()<MAX_Y
            && loc.getZ()>-3800 && loc.getZ()<-2000;
    }

    private Location safe(Location desired)
    {
        if(desired!=null && inside(desired))
        {
            int floor=GeoEngine.getInstance().getHeight(desired.getX(),desired.getY(),desired.getZ());
            if(Math.abs(floor-desired.getZ())<100)
                return new Location(desired.getX(),desired.getY(),floor,desired.getHeading());
        }
        return new Location(45150,52100,-2792,49152);
    }

    /** Finish the server teleport immediately, so loading/Appearing cannot grant immunity. */
    private void travel(Player p,Location destination,int instance)
    {
        p.teleToLocation(destination.getX(),destination.getY(),destination.getZ(),destination.getHeading(),instance,false);
        p.onTeleported();
        p.setTeleportProtection(false);
    }

    /** Same-room displacement stays spawned and targetable, including during the client transition. */
    private void returnInside(Player p,Visit visit)
    {
        Location destination=safe(visit.lastInside);
        p.stopMove(null); p.abortAttack(); p.abortCast(); p.setTarget(null);
        p.getAI().setIntentionActive();
        p.setXYZ(destination.getX(),destination.getY(),destination.getZ()); p.setHeading(destination.getHeading());
        p.setClientX(p.getX()); p.setClientY(p.getY()); p.setClientZ(p.getZ());
        p.setCursorKeyMovement(false);
        p.setBlinkActive(true);
        p.setLastServerPosition(p.getX(),p.getY(),p.getZ());
        p.revalidateZone(true);
        p.broadcastPacket(new TeleportToLocation(p,p.getX(),p.getY(),p.getZ(),p.getHeading()));
        p.broadcastInfo();
        if(p.getSummon()!=null) p.getSummon().teleToLocation(p.getLocation(),false);
        visit.exitStarted=0; visit.commandExit=false; visit.shownSegments=-1;
        screen(p,"Salida cancelada. Regresaste a tu posicion anterior.",1500);
    }

    private synchronized void requestExit(Player p)
    {
        Instance room=room(false);
        if(room==null || p.getInstanceId()!=room.getId()) { p.sendMessage("No estas en Elven PvP."); return; }
        if(p.isDead() || p.isTeleporting()) { p.sendMessage("No puedes iniciar la salida mientras estas muerto o viajando."); return; }
        Visit visit=visits.computeIfAbsent(p.getObjectId(),id->new Visit(safe(new Location(p))));
        if(visit.exitStarted==0) { visit.commandExit=true; begin(p,visit,System.nanoTime()); }
    }

    private synchronized void cancelCommandExit(Player p)
    {
        Visit visit=visits.get(p.getObjectId());
        if(visit==null || !visit.commandExit || p.isDead() || p.isTeleporting()) return;
        if(System.nanoTime()-visit.exitStarted>=EXIT_NANOS) { leave(p,visit); return; }
        if(!inside(new Location(p))) { p.sendMessage("Para cancelar, volve al interior de la arena."); return; }
        returnInside(p,visit);
    }

    private void begin(Player p,Visit visit,long now)
    {
        visit.exitStarted=now; visit.shownSegments=-1;
        p.sendMessage("Saliendo de Elven: 4 segundos. Seguis siendo vulnerable.");
        progress(p,visit,EXIT_NANOS);
    }

    private void progress(Player p,Visit visit,long remaining)
    {
        int segments=(int)Math.max(0,Math.min(16,(remaining*16+EXIT_NANOS-1)/EXIT_NANOS));
        if(segments==visit.shownSegments) return;
        visit.shownSegments=segments;
        screen(p,"Saliendo de Elven ["+"|".repeat(segments)+".".repeat(16-segments)+"] "
            +String.format(java.util.Locale.ROOT,"%.1f",remaining/1_000_000_000.0)+" s - Volve para cancelar",600);
    }

    private static void screen(Player p,String text,int milliseconds)
    {
        p.sendPacket(new ExShowScreenMessage(text,ExShowScreenMessage.TOP_CENTER,milliseconds,1,false,false));
    }

    private void leave(Player p,Visit visit)
    {
        returns.put(p.getObjectId(),safe(visit.lastInside));
        InstanceWorld world=InstanceManager.getInstance().getWorld(p.getInstanceId());
        if(world!=null) world.removeAllowed(p);
        visits.remove(p.getObjectId());
        travel(p,new Location(83425,148585,-3406),0);
        screen(p,"Saliendo de Elven [................] 0.0 s - Regresaste a Giran.",1500);
    }

    private synchronized void tick()
    {
        try
        {
            Instance room=room(false);
            if(room==null) { visits.clear(); return; }
            visits.keySet().removeIf(id->{Player p=World.getPlayer(id);return p==null || !p.isOnline() || p.getInstanceId()!=room.getId();});
            for(int id:room.getPlayers())
            {
                Player p=World.getPlayer(id);
                if(p==null || !p.isOnline() || p.getInstanceId()!=room.getId() || p.isTeleporting()) continue;
                Visit visit=visits.computeIfAbsent(id,key->new Visit(safe(new Location(p))));
                // Death cancels escape. Normal death/revival rules still apply; no healing here.
                if(p.isDead())
                {
                    if(visit.exitStarted!=0) screen(p,"Salida cancelada: moriste en la arena.",1500);
                    visit.exitStarted=0; visit.commandExit=false; visit.shownSegments=-1; continue;
                }
                long now=System.nanoTime();
                if(visit.exitStarted!=0)
                {
                    long remaining=EXIT_NANOS-(now-visit.exitStarted);
                    if(remaining<=0) { leave(p,visit); continue; }
                    if(inside(new Location(p)) && !visit.commandExit) { returnInside(p,visit); continue; }
                    progress(p,visit,remaining);
                }
                else if(inside(new Location(p)))
                {
                    p.setBlinkActive(false);
                    visit.lastInside=new Location(p);
                }
                else begin(p,visit,now);
            }
        }
        catch(Exception ex) { LOG.log(java.util.logging.Level.SEVERE,"Elven boundary tick failed",ex); }
    }

    public static void main(String[] args) { new PvpRooms(); }
}
