package custom.GludioSky;

import java.util.Locale;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.entity.zone.type.RespawnZone;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.ZoneManager;
import org.l2jmobius.gameserver.data.xml.MapRegionData;

/** Public access to the floating arrival dock. No account/build/inventory changes. */
public final class GludioSky implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(GludioSky.class.getName());
    private static final int X=149000,Y=46700,Z=12040;
    private GludioSky()
    {
        VoicedCommandHandler.getInstance().registerHandler(this);
        LOG.info("GludioSky: .muelle / .muelle coliseo. New characters arrive at the floating dock; .muelle nave reaches the docked airship.");
    }
    @Override public String[] getCommandList(){return new String[]{"muelle"};}
    @Override public boolean onCommand(String command,Player player,String params)
    {
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        if(action.equals("estado"))
        {
            boolean here=player.getX()>145000&&player.getX()<154000&&player.getY()>44000&&player.getY()<50000&&player.getZ()>9500;
            player.sendMessage("Muelle: "+(here?"estas en la llegada aerea":"estas fuera del muelle")+". Posicion "+player.getX()+","+player.getY()+","+player.getZ()+"; instancia "+player.getInstanceId()+"; carga pendiente="+player.isTeleporting()+".");
            player.sendMessage("Muelle: 149000,46700,12021. Aeronave: .muelle nave. Resort: .muelle aurelia. .muelle para regresar; .muelle coliseo para bajar.");
            LOG.info("GLUDIO_TRAVEL status object="+player.getObjectId()+" server="+player.getX()+","+player.getY()+","+player.getZ()+" client="+player.getClientX()+","+player.getClientY()+","+player.getClientZ()+" instance="+player.getInstanceId()+" teleporting="+player.isTeleporting());
            return true;
        }
        if(player.isDead()||player.isInCombat()||player.isTeleporting()||player.isFlying()||player.isInOlympiadMode()||player.getInstanceId()!=0)
        {player.sendMessage("Para viajar debes estar vivo, en tierra, fuera de combate, eventos e instancias.");return true;}
        if(player.getPvpFlag()>0||player.getKarma()>0)
        {player.sendMessage("Espera a que termine tu estado PvP o karma antes de viajar al muelle.");return true;}
        if(action.equals("nave")||action.equals("barco"))
        {
            int floor=GeoEngine.getInstance().getHeight(152000,46700,12040);
            if(Math.abs(floor-12040)>100){player.sendMessage("La cubierta de la aeronave no esta disponible.");return true;}
            player.teleToLocation(152000,46700,floor+24,0,0,false);
            player.sendMessage("Aeronave en pruebas, estacionada. .muelle para volver al muelle; .muelle coliseo para bajar.");
            return true;
        }
        if(action.equals("aurelia")||action.startsWith("aurelia ")||action.equals("resort"))
        {
            int ax=153400,ay=55800,az=12040;
            if(action.equals("aurelia a")){ax=156000;ay=55000;az=11296;}
            else if(action.equals("aurelia b")){ax=156000;ay=55000;az=10792;}
            else if(action.equals("aurelia puente")){ax=151700;ay=55000;az=11664;}
            else if(!action.equals("aurelia")&&!action.equals("aurelia cubierta")&&!action.equals("resort"))
            {player.sendMessage(".muelle aurelia | .muelle aurelia a | .muelle aurelia b | .muelle aurelia puente");return true;}
            int floor=GeoEngine.getInstance().getHeight(ax,ay,az);
            if(Math.abs(floor-az)>80){player.sendMessage("El suelo de Aurelia no esta disponible. Avisa al administrador.");return true;}
            player.teleToLocation(ax,ay,floor+24,0,0,false);
            player.sendMessage("Aurelia: nave resort estacionada. .muelle para regresar. Interiores: .muelle aurelia a / b / puente.");
            return true;
        }
        if(action.equals("coliseo")||action.equals("bajar"))
        {
            if((player.getX()<145000||player.getX()>154000||player.getY()<44000||player.getY()>50000||player.getZ()<9500) && (player.getX()<149800||player.getX()>163200||player.getY()<51000||player.getY()>59000||player.getZ()<9500))
            {player.sendMessage("Ese acceso parte del muelle. Usa .muelle para llegar.");return true;}
            player.teleToLocation(148900,46100,-3400,0,0,false);
        }
        else if(action.isEmpty()||action.equals("entrar"))
        {
            int floor=GeoEngine.getInstance().getHeight(X,Y,Z);
            if(Math.abs(floor-Z)>100){player.sendMessage("El suelo del muelle no esta disponible. Avisa al administrador.");return true;}
            LOG.info("GLUDIO_TRAVEL request object="+player.getObjectId()+" from="+player.getX()+","+player.getY()+","+player.getZ()+" instance="+player.getInstanceId()+" floor="+floor);
            player.teleToLocation(X,Y,floor+24,0,0,false);
            LOG.info("GLUDIO_TRAVEL sent object="+player.getObjectId()+" server="+player.getX()+","+player.getY()+","+player.getZ()+" instance="+player.getInstanceId()+" teleporting="+player.isTeleporting());
            player.sendMessage("Viaje al muelle aereo solicitado. .muelle estado para comprobar llegada; .muelle coliseo para bajar.");
        }
        else player.sendMessage(".muelle | .muelle nave | .muelle aurelia | .muelle estado | .muelle coliseo");
        return true;
    }
    private static void verify()
    {
        Player probe=null;
        try
        {
            GeoEngine geo=GeoEngine.getInstance();
            if(!geo.hasGeo(X,Y)||Math.abs(geo.getHeight(X,Y,Z)-12016)>8)throw new IllegalStateException("Dock floor missing");
            if(Math.abs(geo.getHeight(148900,46100,-3400)+3400)>100)throw new IllegalStateException("Original Coliseum floor changed");
            var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
            var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);
            ctor.setAccessible(true);
            probe=ctor.newInstance(template,"gludio-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
            probe.setName("GludioSkyProbe");probe.setAccessLevel(0);probe.setLabControlled(true);
            probe.setDead(false);probe.setOnlineStatus(true,false);probe.setEnteredWorld();probe.spawnMe(X,Y,Z);probe.revalidateZone(true);
            if(!probe.isInsideZone(ZoneId.PEACE))throw new IllegalStateException("Arrival is not a peace zone");
            RespawnZone zone=ZoneManager.getInstance().getZone(probe,RespawnZone.class);
            if(zone==null||!"gludio_sky".equals(zone.getRespawnPoint(probe)))throw new IllegalStateException("Respawn zone missing");
            Location loc=MapRegionData.getInstance().getSpawnLocByRegionName("gludio_sky");
            if(loc==null||loc.getZ()!=Z)throw new IllegalStateException("Respawn coordinates mismatch");
            if(!geo.canMoveToTarget(X,Y,Z,X+64,Y,Z,0))throw new IllegalStateException("Spawn movement blocked");
            LOG.info("GLUDIO_SKY_SMOKE PASS: dock floor, spawn movement, peace/respawn zone and original Coliseum lower floor; transient character only.");
        }
        catch(Exception e){LOG.log(java.util.logging.Level.SEVERE,"GLUDIO_SKY_SMOKE FAIL",e);}
        finally{if(probe!=null){probe.deleteMe();probe.setOnlineStatus(false,false);}}
    }
    public static void main(String[] args)
    {
        new GludioSky();
        if(Boolean.getBoolean("lab.gludio.verify"))org.l2jmobius.commons.threads.ThreadPool.schedule(GludioSky::verify,30000);
    }
}
