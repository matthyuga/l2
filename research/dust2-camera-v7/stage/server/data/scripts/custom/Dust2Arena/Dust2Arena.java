package custom.Dust2Arena;

import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

/** Exploration build. No equipment, character-start or event-rule changes. */
public final class Dust2Arena implements IVoicedCommandHandler
{
    private static final int[] CT={141448,54536,7936},T={140168,57704,8192};
    private static final Map<Integer,Location> RETURNS=new ConcurrentHashMap<>();
    private Dust2Arena(){VoicedCommandHandler.getInstance().registerHandler(this);Logger.getLogger(getClass().getName()).info("Dust2Arena ready: .dust2 | ct | t | escalera | salir | estado. Exploration peace zone.");}
    @Override public String[] getCommandList(){return new String[]{"dust2"};}
    private static boolean inside(Player p){return p.getInstanceId()==0&&p.getX()>138376&&p.getX()<142984&&p.getY()>53160&&p.getY()<58600&&p.getZ()>7644&&p.getZ()<8580;}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        String a=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        if(a.equals("estado")){p.sendMessage("Dust2: "+(inside(p)?"dentro":"fuera")+". Posicion "+p.getX()+","+p.getY()+","+p.getZ()+"; instancia "+p.getInstanceId()+". .dust2 ct | .dust2 t | .dust2 salir");return true;}
        if(!(a.isEmpty()||a.equals("escalera2")||a.equals("escalera")||a.equals("entrar")||a.equals("ct")||a.equals("t")||a.equals("salir")||a.equals("volver"))){p.sendMessage(".dust2 | .dust2 ct | .dust2 t | .dust2 salir | .dust2 estado");return true;}
        if(p.isDead()||p.isInCombat()||p.isTeleporting()||p.isFlying()||p.isInOlympiadMode()||p.getInstanceId()!=0||p.getPvpFlag()>0||p.getKarma()>0){p.sendMessage("Para viajar debes estar vivo, en tierra y fuera de combate, PvP, karma, Olimpiadas e instancias.");return true;}
        if(a.equals("salir")||a.equals("volver"))
        {
            if(!inside(p)&&!RETURNS.containsKey(p.getObjectId())){p.sendMessage("Estas fuera de Dust2. Usa .dust2 para entrar.");return true;}
            Location loc=RETURNS.remove(p.getObjectId());if(loc==null)loc=new Location(149000,46700,12040);
            p.teleToLocation(loc.getX(),loc.getY(),loc.getZ(),loc.getHeading(),0,false);p.sendMessage("Regresaste de Dust2.");return true;
        }
        int[] s=a.equals("escalera2")?new int[]{141320,55440,8064}:a.equals("escalera")?new int[]{139336,56560,8064}:a.equals("t")?T:CT;int floor=GeoEngine.getInstance().getHeight(s[0],s[1],s[2]);
        if(Math.abs(floor-(s[2]-24))>40){p.sendMessage("El suelo de Dust2 no esta disponible. Avisa al administrador.");return true;}
        if(!inside(p))RETURNS.put(p.getObjectId(),new Location(p.getX(),p.getY(),p.getZ(),p.getHeading()));
        p.teleToLocation(s[0],s[1],floor+24,(a.equals("escalera")||a.equals("escalera2"))?49152:0,0,false);
        p.sendMessage("Dust2 en exploracion: zona de paz. .dust2 ct / .dust2 t para cambiar de sector; .dust2 salir para regresar.");return true;
    }
    public static void main(String[] args){new Dust2Arena();}
}
