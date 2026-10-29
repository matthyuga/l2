package custom.ExplorationWalking;
import java.nio.file.*;
import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.TownManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.ExShowScreenMessage;

/** GM-only walking lab, server-authoritative personal exploration and global knowledge. */
public final class ExplorationWalking extends Script implements IVoicedCommandHandler {
    private static final Logger LOG=Logger.getLogger(ExplorationWalking.class.getName());
    private static final String PERSONAL="FOG4_PERSONAL",PAUSED="FOG4_PAUSED";
    private final Map<Integer,Session> sessions=new HashMap<>();
    private final Path file=Path.of("data","exploration-walking-v4","global.base64");
    private final BitSet global;
    private final ExplorationPlaces places;
    private long globalVersion=0;
    private static final class Session {
        Player player;BitSet personal;long seenGlobal=-1,sequence=0,lastSent=0;boolean dirty=true;
        final ExplorationPlaces.Tracker location=new ExplorationPlaces.Tracker();
        Session(Player p){player=p;personal=FogGrid.decode(p.getVariables().getString(PERSONAL,""));}
    }
    public ExplorationWalking() throws Exception {
        global=Files.exists(file)?FogGrid.decode(Files.readString(file).trim()):new BitSet();
        places=new ExplorationPlaces(Path.of("data/scripts/custom/ExplorationWalking/places.xml"));
        VoicedCommandHandler.getInstance().registerHandler(this);
        ThreadPool.scheduleAtFixedRate(this::tick,1500,1000);
        LOG.info("ExplorationWalking V4.2 ready: "+places.size()+" named exploration places plus TownZones; .exploracion estado | pausa | continuar.");
    }
    @Override public String[] getCommandList(){return new String[]{"exploracion"};}
    @Override public synchronized boolean onCommand(String command,Player p,String params) {
        if(p==null)return false;if(!p.isGM()){p.sendMessage("Exploracion V4: ensayo GM.");return true;}
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        if(action.equals("pausa")||action.equals("continuar")) {
            p.getVariables().set(PAUSED,action.equals("pausa"));p.getVariables().storeMe();
            p.sendMessage(action.equals("pausa")?"Exploracion automatica pausada.":"Exploracion automatica activada.");
        }
        Session s=sessions.get(p.getObjectId());
        p.sendMessage("Mapa V4: "+(s==null?0:s.personal.cardinality())+" celdas personales, "+global.cardinality()+" globales. Giran siempre despejada.");
        if(s!=null){s.dirty=true;s.lastSent=0;}
        return true;
    }
    private synchronized void tick() {
        Set<Integer> live=new HashSet<>();
        for(Player p:World.getPlayers()) {
            if(!p.isOnline()||!p.isGM()||p.isLabControlled())continue;live.add(p.getObjectId());
            try {update(p);}catch(Exception e){LOG.log(Level.WARNING,"Walking fog update failed objectId="+p.getObjectId(),e);}
        }
        sessions.keySet().retainAll(live);
    }
    private void update(Player p) throws Exception {
        Session s=sessions.get(p.getObjectId());
        if(s==null||s.player!=p){s=new Session(p);sessions.put(p.getObjectId(),s);}
        boolean canExplore=!p.getVariables().getBoolean(PAUSED,false)&&!p.isDead()&&!p.isTeleporting()&&p.getInstanceId()==0;
        if(canExplore) {
            BitSet next=(BitSet)s.personal.clone();
            if(FogGrid.reveal(next,p.getX(),p.getY())) {
                BitSet merged=(BitSet)global.clone();merged.or(next);
                if(!merged.equals(global)) {persist(merged);global.clear();global.or(merged);globalVersion++;}
                p.getVariables().set(PERSONAL,FogGrid.encode(next));p.getVariables().storeMe();s.personal=next;s.dirty=true;
            }
            var town=TownManager.getTown(p.getX(),p.getY(),p.getZ());
            var place=town==null?places.find(p.getX(),p.getY(),p.getZ()):null;
            String key=town!=null?"FOG4_TOWN_"+town.getTownId():place!=null?"FOG4_PLACE_"+place.id:"";
            if(s.location.enter(key,System.currentTimeMillis())) {
                String name=town!=null?town.getName():place.name;
                if(name==null||name.isBlank())name="Ciudad "+town.getTownId();
                boolean first=!p.getVariables().getBoolean(key,false);
                if(first){p.getVariables().set(key,true);p.getVariables().storeMe();}
                p.sendPacket(new ExShowScreenMessage(first?"Lugar descubierto: "+name:name,first?5000:3000));
                if(first){p.sendMessage("Lugar descubierto: "+name+". Registrado en tu exploracion.");LOG.info("Walking fog place discovered objectId="+p.getObjectId()+" key="+key+" name="+name);}
            }
        }
        long now=System.currentTimeMillis();
        if(s.dirty||s.seenGlobal!=globalVersion||now-s.lastSent>=10000) {
            for(String part:FogGrid.packets(p.getObjectId(),++s.sequence,global,s.personal))p.sendPacket(new ExShowScreenMessage(part,1));
            s.seenGlobal=globalVersion;s.lastSent=now;s.dirty=false;
        }
    }
    private void persist(BitSet bits) throws Exception {
        Files.createDirectories(file.getParent());Path temp=Files.createTempFile(file.getParent(),"fog-",".tmp");
        try {Files.writeString(temp,FogGrid.encode(bits));Files.move(temp,file,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
        finally {Files.deleteIfExists(temp);}
    }
    public static void main(String[] args) throws Exception{new ExplorationWalking();}
}
