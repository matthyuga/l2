package custom.ExplorationLab;

import java.nio.file.Path;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.ExShowScreenMessage;

/** Opt-in GM discovery prototype. No map patches, combat changes, rewards or teleports. */
public final class ExplorationLab extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(ExplorationLab.class.getName());
    private final Set<Integer> observers=ConcurrentHashMap.newKeySet();
    private final ExplorationState state;
    public ExplorationLab() throws Exception
    {
        state=new ExplorationState(Path.of("data","exploration-lab-v1","region.properties"));
        VoicedCommandHandler.getInstance().registerHandler(this);
        ThreadPool.scheduleAtFixedRate(this::tick,1000,1000);
        LOG.info("ExplorationLab V1: .explora, GM opt-in; no participants on startup.");
    }
    @Override public String[] getCommandList(){return new String[]{"explora"};}
    @Override public synchronized boolean onCommand(String command,Player p,String params)
    {
        if(p==null)return false;
        if(!p.isGM()){p.sendMessage("Exploracion: ensayo privado para GM.");return true;}
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        try
        {
            switch(action)
            {
                case "anclar":
                    if(state.current()!=null){p.sendMessage("Ya hay una region de prueba. Usa anclar-nueva para reemplazarla expresamente.");break;}
                    anchor(p);break;
                case "anclar-nueva":anchor(p);break;
                case "iniciar":
                    if(state.current()==null){p.sendMessage("Primero usa .explora anclar en el centro del ensayo.");break;}
                    observers.add(p.getObjectId());p.sendMessage("Ensayo activo. Radio 600; baliza virtual en el centro (radio 120).");discover(p);break;
                case "salir":observers.remove(p.getObjectId());p.sendMessage("Ensayo detenido para tu personaje.");break;
                case "activar":activate(p);break;
                case "recuperar":
                    if(!eligible(p)){p.sendMessage("Inicia el ensayo y acercate a la baliza central.");break;}
                    if(state.reveal())
                    {
                        LOG.info("ExplorationLab global reveal by objectId="+p.getObjectId());
                        for(int id:observers){Player other=World.getPlayer(id);if(other!=null&&other.isGM())other.sendMessage("Region de ensayo recuperada globalmente. Usa .explora estado.");}
                    }
                    else p.sendMessage("La region ya estaba recuperada.");
                    break;
                case "estado":status(p);break;
                default:p.sendMessage(".explora anclar | iniciar | activar | recuperar | estado | salir. Region alternativa: anclar-nueva.");
            }
        }
        catch(Exception e){LOG.log(Level.WARNING,"ExplorationLab command failed",e);p.sendMessage("No se pudo guardar el ensayo. Revisa el log; no se confirma el cambio.");}
        return true;
    }
    private void anchor(Player p) throws Exception
    {
        if(p.isDead()||p.isInCombat()||p.getInstanceId()!=0){p.sendMessage("Ancla fuera de combate, vivo y en el mundo compartido.");return;}
        state.anchor(p.getX(),p.getY(),p.getZ(),p.getInstanceId());
        p.sendMessage("Nueva region de ensayo anclada en "+p.getX()+", "+p.getY()+", "+p.getZ()+". Niebla TOTAL. Usa .explora iniciar.");
    }
    private synchronized void tick()
    {
        for(int id:observers)
        {
            Player p=World.getPlayer(id);
            if(p==null||!p.isOnline()||!p.isGM()){observers.remove(id);continue;}
            try{discover(p);}catch(Exception e){observers.remove(id);LOG.log(Level.WARNING,"ExplorationLab paused for objectId="+id,e);}
        }
    }
    private void discover(Player p)
    {
        ExplorationState.Region r=state.current();
        if(r==null||p.isDead()||p.isTeleporting()||!r.contains(p.getX(),p.getY(),p.getZ(),p.getInstanceId(),600))return;
        if(!p.getVariables().getBoolean(r.visitKey(),false))
        {
            p.getVariables().set(r.visitKey(),true);p.getVariables().storeMe();
            p.sendPacket(new ExShowScreenMessage("Lugar descubierto: Region de ensayo",ExShowScreenMessage.TOP_CENTER,5000));
            p.sendMessage("Visita registrada. La baliza virtual se activa con .explora activar a menos de 120 del centro.");
            LOG.info("ExplorationLab discovery region="+r.id()+" objectId="+p.getObjectId());
        }
    }
    private boolean eligible(Player p)
    {
        ExplorationState.Region r=state.current();
        return observers.contains(p.getObjectId())&&r!=null&&!p.isDead()&&!p.isTeleporting()&&!p.isInCombat()
            &&r.contains(p.getX(),p.getY(),p.getZ(),p.getInstanceId(),120);
    }
    private void activate(Player p)
    {
        if(!eligible(p)){p.sendMessage("Inicia el ensayo y acercate a menos de 120 de la baliza central, fuera de combate.");return;}
        discover(p);ExplorationState.Region r=state.current();
        if(p.getVariables().getBoolean(r.surveyKey(),false)){p.sendMessage("Ya activaste esta baliza.");return;}
        p.getVariables().set(r.surveyKey(),true);p.getVariables().storeMe();
        p.sendPacket(new ExShowScreenMessage("Baliza de exploracion activada",ExShowScreenMessage.TOP_CENTER,4000));
        status(p);
    }
    private void status(Player p)
    {
        ExplorationState.Region r=state.current();
        if(r==null){p.sendMessage("Sin region anclada.");return;}
        boolean visited=p.getVariables().getBoolean(r.visitKey(),false),surveyed=p.getVariables().getBoolean(r.surveyKey(),false);
        p.sendMessage("Ensayo "+r.id()+" centro="+r.x()+","+r.y()+","+r.z()+" global="+r.revealed()+" visita="+visited+" baliza="+surveyed);
        p.sendMessage("Cobertura calculada: "+ExplorationState.fog(r,surveyed)+". La niebla grafica aun no esta conectada al mapa.");
    }
    public static void main(String[] args) throws Exception{new ExplorationLab();}
}
