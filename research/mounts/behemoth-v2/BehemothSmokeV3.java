package custom.BehemothTransport;

import java.nio.file.*;
import java.util.*;
import java.util.logging.*;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
import static custom.BehemothTransport.SeatRules.Role.*;

/** Real server actors, never accounts/DB rows; NOT evidence of two-client rendering. */
public final class BehemothSmokeV3
{
    private static final Logger LOG=Logger.getLogger(BehemothSmokeV3.class.getName());
    private static void check(boolean condition,String message){if(!condition)throw new AssertionError(message);}
    private static Player probe(String name,int x,int y,int z) throws Exception
    {
        var template=PlayerTemplateData.getInstance().getTemplate(0);
        var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,PlayerAppearance.class);ctor.setAccessible(true);
        Player p=ctor.newInstance(template,"behemoth-transient-probe",new PlayerAppearance((byte)0,(byte)0,(byte)0,false));
        p.setName(name);p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(x,y,z);p.revalidateZone(true);p.setCurrentHp(p.getMaxHp());return p;
    }
    static void run(BehemothTransport service)
    {
        var checks=new ArrayList<String>();var actors=new ArrayList<Player>();BehemothTransport.Trip trip=null;Throwable failure=null;
        try
        {
            int x=83525,y=148585,z=GeoEngine.getInstance().getHeight(x,y,-3401);
            Player driver=probe("BehemothDriverQA",x,y,z),gunner=probe("BehemothGunnerQA",x+20,y+20,z),other=probe("BehemothBystanderQA",x-20,y,z);actors.addAll(List.of(driver,gunner,other));
            check(!driver.isMovementDisabled(),"ordinary player initially mobile");
            trip=service.summon(driver);check(trip.npc.getTemplate().getFCollisionHeight()==54 && trip.npc.getTemplate().getFCollisionRadius()==63,"initial spawn uses native collision dimensions");checks.add("native collision dimensions configured before first spawn");check(trip.npc.getMaxHp()>1000,"mount HP configured");checks.add("transient native NPC summon");
            service.board(driver,trip,DRIVER);check(BehemothSeatSync.isSeated(driver)&&driver.isMovementDisabled(),"driver seat guard");checks.add("driver assigned and guarded");
            try{service.board(gunner,trip,GUNNER);throw new AssertionError("unauthorized passenger boarded");}catch(IllegalStateException expected){checks.add("uninvited passenger rejected");}
            trip.invited.add(gunner.getObjectId());service.board(gunner,trip,GUNNER);check(BehemothSeatSync.isSeated(gunner),"gunner assigned");checks.add("authorized independent second player");
            check(driver.getZ()>trip.npc.getZ()+80 && gunner.getZ()>trip.npc.getZ()+80,"elevated seat coordinates");checks.add("seat coordinates synchronized");
            check(service.combat(driver,other)!=null,"driver cannot attack");check(service.combat(gunner,other)==null,"gunner retains normal attacks");check(service.combat(gunner,trip.npc)!=null,"own mount protected");check(service.combat(other,driver)==null,"ordinary outsider combat unchanged");checks.add("driver/gunner combat roles");
            check(BehemothSeatSync.onMove(gunner,x+300,y,z),"gunner movement consumed");check(!trip.npc.isMoving(),"gunner cannot drive");checks.add("passenger movement cannot steer");
            check(BehemothSeatSync.onMove(driver,trip.npc.getX()+80,trip.npc.getY(),trip.npc.getZ()),"driver request consumed");check(trip.npc.isMoving(),"mount receives move intention");checks.add("driver controls native movement");trip.npc.stopMove(null);
            check(BehemothSeatSync.onValidate(gunner),"passenger client coordinates ignored");checks.add("client position spoof cannot release seat");
            service.leave(gunner,"QA leave",true);check(!BehemothSeatSync.isSeated(gunner)&&!gunner.isMovementDisabled(),"gunner restored");check(Math.abs(gunner.getZ()-trip.npc.getZ())<70,"gunner ground placement");checks.add("dismount restores ground and movement");
            service.board(gunner,trip,GUNNER);service.logout(gunner);check(!BehemothSeatSync.isSeated(gunner)&&BehemothSeatSync.isSeated(driver),"gunner logout preserves driver");checks.add("passenger disconnect cleanup");
            service.board(gunner,trip,GUNNER);gunner.setDead(true);service.death(gunner);check(!BehemothSeatSync.isSeated(gunner)&&BehemothSeatSync.isSeated(driver),"gunner death preserves driver");gunner.setDead(false);gunner.setCurrentHp(gunner.getMaxHp());checks.add("passenger death cleanup");
            service.board(gunner,trip,GUNNER);service.logout(driver);check(!BehemothSeatSync.isSeated(driver)&&!BehemothSeatSync.isSeated(gunner)&&trip.seats.closed(),"owner logout closes both");checks.add("owner disconnect releases both seats");trip=null;
            trip=service.summon(driver);gunner.setXYZ(trip.npc.getX()-20,trip.npc.getY(),trip.npc.getZ());service.board(driver,trip,DRIVER);trip.invited.add(gunner.getObjectId());service.board(gunner,trip,GUNNER);service.death(trip.npc);check(!BehemothSeatSync.isSeated(driver)&&!BehemothSeatSync.isSeated(gunner)&&trip.seats.closed(),"mount death releases both");checks.add("mount death releases both players");trip=null;
            check(!other.isMovementDisabled()&&!BehemothSeatSync.onMove(other,x,y,z),"unrelated player untouched");checks.add("unrelated players unchanged");
        }
        catch(Throwable e){failure=e;LOG.log(Level.SEVERE,"BEHEMOTH_SERVER_SMOKE FAIL",e);}
        finally
        {
            if(trip!=null)service.close(trip,"QA cleanup");
            for(Player p:actors)try{service.logout(p);BehemothSeatSync.unbind(p);p.deleteMe();p.setOnlineStatus(false,false);}catch(Exception ignored){}
            try{String rows=checks.stream().map(s->"\""+s+"\"").reduce((a,b)->a+","+b).orElse("");String error=failure==null?"null":"\""+failure.toString().replace("\\","\\\\").replace("\"","\\\"")+"\"";Files.writeString(Path.of("../../research/mounts/behemoth-v2/server-smoke.json"),"{\"passed\":"+(failure==null)+",\"realNetworkClients\":false,\"persistentCharactersCreated\":false,\"checks\":["+rows+"],\"error\":"+error+"}");}catch(Exception e){LOG.log(Level.SEVERE,"Cannot write Behemoth smoke report",e);}
            try{Files.deleteIfExists(Path.of("config/BehemothTransport-smoke.request"));}catch(Exception ignored){}
        }
        if(failure==null)LOG.info("BEHEMOTH_SERVER_SMOKE PASS: "+checks.size()+" real-actor checks; native client rendering still requires verification");
    }
}
