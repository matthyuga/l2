package custom.VeilmarPvp;

import java.util.Locale;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.spawns.Spawn;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.instancezone.Instance;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;

/** Opt-in shared Veilmar PvP test room. No changes to builds, equipment or AI. */
public final class VeilmarPvp implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(VeilmarPvp.class.getName());
    private static final int TEMPLATE=3052;
    private static final int[][] POINTS={{-78552,212264,-2592},{-86840,201512,-7664},{-93640,211000,-7952}};
    private static final Map<Integer,Location> RETURNS=new ConcurrentHashMap<>();
    private int roomId;
    private final List<Spawn> fighters=new ArrayList<>();

    private VeilmarPvp()
    {
        VoicedCommandHandler.getInstance().registerHandler(this);
        org.l2jmobius.commons.threads.ThreadPool.scheduleAtFixedRate(this::tick,1000,1000);
        LOG.info("Veilmar PvP instalada: .veilmar | agite | calma | interior | interior2 | volver | revivir | estado. Sala y combatientes bajo demanda.");
    }
    @Override public String[] getCommandList(){return new String[]{"veilmar"};}
    @Override public synchronized boolean onCommand(String command,Player p,String params)
    {
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        try
        {
            switch(action)
            {
                case "", "entrar", "superficie" -> enter(p,0);
                case "interior", "santuario" -> enter(p,1);
                case "interior2" -> enter(p,2);
                case "salir", "volver" -> leave(p);
                case "revivir" -> revive(p);
                case "agite" -> {
                    if(!p.isGM() || !inside(p) || p.getZ()<=-5000)p.sendMessage("GM: entra a la superficie de Veilmar para iniciar el agite.");
                    else if(!fighters.isEmpty())p.sendMessage("El agite ya esta activo; .veilmar calma para detenerlo.");
                    else {spawnFighters(room(),fighters);p.sendMessage("Agite Veilmar: 9 combatientes, FFA y respawn de 20 segundos. .veilmar calma para detenerlo.");}
                }
                case "calma" -> {if(p.isGM() && inside(p)){clearFighters(fighters);p.sendMessage("Agite detenido.");}}
                case "estado" -> p.sendMessage("Veilmar PvP: "+(inside(p)?"dentro de sala "+roomId:"fuera")+", agite="+fighters.size()+". .veilmar volver | revivir | agite | calma. Duelo GM: .ia mago / .ia fisico.");
                default -> p.sendMessage(".veilmar entrar | superficie | interior | interior2 | volver | revivir | agite | calma | estado");
            }
        }
        catch(Exception ex)
        {
            LOG.log(java.util.logging.Level.SEVERE,"Veilmar command failed",ex);
            p.sendMessage("Veilmar no disponible: revisa geodata y plantilla 3052.");
        }
        return true;
    }
    private boolean inside(Player p)
    {
        return roomId>0 && InstanceManager.getInstance().getInstance(roomId)!=null && p.getInstanceId()==roomId;
    }
    private Instance room()
    {
        InstanceManager manager=InstanceManager.getInstance();
        Instance room=manager.getInstance(roomId);
        if(roomId==0 || room==null)
        {
            if(manager.getInstanceTemplateFileName(TEMPLATE)==null)throw new IllegalStateException("Missing Veilmar template");
            room=manager.createDynamicInstance(TEMPLATE);
            clearFighters(fighters);
            room.setEmptyDestroyTime(300000);
            roomId=room.getId();
            room.getDoors().forEach(d->d.openMe());
        }
        return room;
    }
    private static int floor(int[] point)
    {
        GeoEngine geo=GeoEngine.getInstance();
        if(!geo.hasGeo(point[0],point[1]))throw new IllegalStateException("Missing Veilmar geodata");
        int z=geo.getHeight(point[0],point[1],point[2]);
        if(Math.abs(z-point[2])>100)throw new IllegalStateException("Entry floor differs from original map");
        return z;
    }
    private void enter(Player p,int index)
    {
        if(p.isDead() || p.isInCombat() || p.isTeleporting())
        {p.sendMessage("Sal de combate; debes estar vivo y sin teleport pendiente para viajar a Veilmar.");return;}
        if(!inside(p) && p.getInstanceId()!=0)
        {p.sendMessage("Primero sal de tu instancia actual.");return;}
        int[] point=POINTS[index];int z=floor(point);
        Instance room=room();
        if(!inside(p))RETURNS.put(p.getObjectId(),new Location(p));
        p.teleToLocation(point[0],point[1],z,0,room.getId(),false);
        restore(p);
        p.sendMessage("Veilmar PvP: combate libre. .veilmar volver para regresar. GM: .veilmar agite para 9 rivales o .ia mago / .ia fisico para duelo.");
    }
    private void leave(Player p)
    {
        if(!inside(p)){p.sendMessage("No estas en Veilmar PvP.");return;}
        if(p.isInCombat() && !p.isDead()){p.sendMessage("Sal de combate antes de volver.");return;}
        if(p.isTeleporting()){p.sendMessage("Espera a terminar el teleport.");return;}
        if(p.isDead())p.doRevive();
        Location loc=RETURNS.remove(p.getObjectId());
        if(loc==null)loc=new Location(83425,148585,-3406);
        p.teleToLocation(loc.getX(),loc.getY(),loc.getZ(),loc.getHeading(),0,false);
        restore(p);
        p.sendMessage("Regresaste de Veilmar.");
    }
    private void revive(Player p)
    {
        if(!inside(p) || !p.isDead()){p.sendMessage("Revivir solo funciona si moriste dentro de Veilmar.");return;}
        if(p.isTeleporting())return;
        int z=floor(POINTS[0]);p.doRevive();
        p.teleToLocation(POINTS[0][0],POINTS[0][1],z,0,roomId,false);restore(p);
        p.sendMessage("Reapareciste en Veilmar con HP, CP y MP completos.");
    }
    private static void restore(Player p)
    {
        p.fullRestore();
        var skill=SkillData.getInstance().getSkill(1323,1);
        if(skill!=null)skill.applyEffects(p,p,true,7200);
    }
    private static void spawnFighters(Instance room,List<Spawn> list)throws Exception
    {
        GeoEngine geo=GeoEngine.getInstance();List<Spawn> prepared=new ArrayList<>();
        for(int i=0;i<9;i++)
        {
            double angle=i*Math.PI*2/9;int x=POINTS[0][0]+(int)(650*Math.cos(angle)),y=POINTS[0][1]+(int)(650*Math.sin(angle));
            int z=geo.getHeight(x,y,floor(POINTS[0]));
            if(Math.abs(z-floor(POINTS[0]))>100 || !geo.canMoveToTarget(POINTS[0][0],POINTS[0][1],floor(POINTS[0]),x,y,z,room.getId()))throw new IllegalStateException("Blocked agite spawn "+i);
            Spawn spawn=new Spawn(901100+i);spawn.setXYZ(x,y,z);spawn.setInstanceId(room.getId());spawn.setRespawnDelay(20);prepared.add(spawn);
        }
        try
        {
            for(Spawn spawn:prepared)
            {
                list.add(spawn);spawn.startRespawn();Npc npc=spawn.doSpawn();
                if(npc==null || !npc.isAttackable())throw new IllegalStateException("Missing attackable Veilmar fighter");
                npc.setTitle("Veilmar agite");npc.setInvul(false);npc.setRunning();
            }
        }
        catch(Exception ex){clearFighters(list);throw ex;}
    }
    private static void clearFighters(List<Spawn> list)
    {
        for(Spawn spawn:list)
        {
            spawn.stopRespawn();Npc npc=spawn.getLastSpawn();
            if(npc!=null){npc.abortCast();npc.abortAttack();npc.getAI().setIntentionIdle();npc.deleteMe();npc.setInstanceId(0);}
        }
        list.clear();
    }
    private synchronized void tick()
    {
        if(fighters.isEmpty())return;
        Instance room=InstanceManager.getInstance().getInstance(roomId);
        if(room==null || room.getPlayers().stream().map(World::getPlayer).noneMatch(p->p!=null && p.isOnline()))
        {clearFighters(fighters);return;}
        List<Creature> targets=new ArrayList<>();
        for(Spawn spawn:fighters){Npc npc=spawn.getLastSpawn();if(npc!=null && !npc.isAlikeDead())targets.add(npc);}
        for(int id:room.getPlayers()){Player p=World.getPlayer(id);if(p!=null && p.isOnline() && !p.isAlikeDead() && !p.isInvul())targets.add(p);}
        for(Spawn spawn:fighters)
        {
            Npc npc=spawn.getLastSpawn();if(npc==null || npc.isAlikeDead())continue;
            Creature old=npc.getAI().getAttackTarget();
            if(old!=null && targets.contains(old) && old.getInstanceId()==roomId)continue;
            List<Creature> choices=targets.stream().filter(t->t!=npc && t.getInstanceId()==roomId).toList();
            if(choices.isEmpty())continue;
            Creature target=choices.get(ThreadLocalRandom.current().nextInt(choices.size()));
            npc.asAttackable().clearAggroList();npc.asAttackable().addDamageHate(target,0,50000);
            npc.setTarget(target);npc.getAI().setIntentionAttack(target);
        }
    }
    /** Server-side smoke check; no persistent player or character changes. */
    public static void verify()
    {
        try
        {
            for(int[] point:POINTS)floor(point);
            if(InstanceManager.getInstance().getInstanceTemplateFileName(TEMPLATE)==null)throw new IllegalStateException("Missing template");
            Instance room=InstanceManager.getInstance().createDynamicInstance(TEMPLATE);
            try
            {
                if(!room.isPvP() || !room.isSummonAllowed() || room.getDoors().size()!=26)throw new IllegalStateException("Instance/doors mismatch: "+room.getDoors().size());
                room.getDoors().forEach(d->d.openMe());
                GeoEngine geo=GeoEngine.getInstance();int[] point=POINTS[0];int z=floor(point);
                if(!geo.canMoveToTarget(point[0],point[1],z,point[0],point[1]-300,z,room.getId()))throw new IllegalStateException("IA spawn path blocked at entry");
                int wx=-86240,wy=201512,wz=geo.getHeight(wx,wy,-7656);
                if(geo.checkNearestNswe(GeoEngine.getGeoX(wx),GeoEngine.getGeoY(wy),wz,org.l2jmobius.gameserver.geoengine.geodata.Cell.NSWE_EAST))throw new IllegalStateException("Expected interior wall edge is not blocked");
                verifyCombat(room);
                List<Spawn> probe=new ArrayList<>();
                try{spawnFighters(room,probe);if(probe.size()!=9)throw new IllegalStateException("Agite count mismatch");}
                finally{clearFighters(probe);}
                if(!room.getNpcs().isEmpty())throw new IllegalStateException("Agite cleanup left NPCs");
                LOG.info("VEILMAR_SMOKE PASS: 3 floors, PvP room, summons, "+room.getDoors().size()+" open doors, IA spawn path, interior wall, native PvP damage and 9 agite spawns/cleanup. No persistent characters changed.");
            }
            finally{InstanceManager.getInstance().destroyInstance(room.getId());}
        }
        catch(Exception ex){LOG.log(java.util.logging.Level.SEVERE,"VEILMAR_SMOKE FAIL",ex);}
    }
    private static void verifyCombat(Instance room)throws Exception
    {
        // Invoke the normal constructor, avoiding Player.create(), which inserts a DB row.
        var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
        var constructor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);
        constructor.setAccessible(true);
        Player a=null,b=null;
        try
        {
            a=constructor.newInstance(template,"veilmar-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
            b=constructor.newInstance(template,"veilmar-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
            int slot=0;
            for(Player p:new Player[]{a,b})
            {
                p.setName("VeilmarProbe"+(slot++));p.setAccessLevel(0);p.setLabControlled(true);
                p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.setInstanceId(room.getId());
                p.spawnMe(POINTS[0][0]+slot*32,POINTS[0][1],floor(POINTS[0]));
                p.setInvul(false);p.setSpawnProtection(false);p.revalidateZone(true);p.fullRestore();
                if(!p.isInsideZone(ZoneId.PVP) || p.isInsideZone(ZoneId.PEACE))throw new IllegalStateException("Native PvP zone state mismatch");
            }
            if(!b.isAutoAttackable(a))throw new IllegalStateException("Native PvP target rejected");
            double before=b.getCurrentHp()+b.getCurrentCp();
            for(int attempt=0;attempt<4 && b.getCurrentHp()+b.getCurrentCp()>=before;attempt++)
            {a.doAttack(b);Thread.sleep(1200);}
            if(b.getCurrentHp()+b.getCurrentCp()>=before)throw new IllegalStateException("No damage from native melee attack");
        }
        finally
        {
            for(Player p:new Player[]{a,b})if(p!=null)
            {p.abortAttack();p.abortCast();p.stopAllEffects();p.deleteMe();p.setOnlineStatus(false,false);}
        }
    }
    public static void main(String[] args)
    {
        new VeilmarPvp();
        if(Boolean.getBoolean("lab.veilmar.verify"))org.l2jmobius.commons.threads.ThreadPool.schedule(VeilmarPvp::verify,30000);
    }
}
