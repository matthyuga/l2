package custom.WorldDamageNumbers;

import java.util.Locale;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.MagicSkillUse;

/** Cosmetic numbers on the actual attacker, shared by every nearby observer. */
public class WorldDamageNumbers extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(WorldDamageNumbers.class.getName());
    public WorldDamageNumbers()
    {
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,
            (OnCreatureDamageDealt e)->damage(e),this));
        VoicedCommandHandler.getInstance().registerHandler(this);
        LOG.info("WorldDamageNumbers: general attacker-anchored glyphs enabled; .vfx prueba for client diagnostics.");
    }
    private static void damage(OnCreatureDamageDealt e)
    {
        Creature attacker=e.getAttacker();
        if(attacker==null||!attacker.isSpawned()||!Double.isFinite(e.getDamage())||e.getDamage()<=0)return;
        boolean magic=e.getSkill()!=null&&e.getSkill().isMagic();
        show(attacker,damageValue(e.getDamage()),(magic?2:0)+(e.isCritical()?1:0));
    }
    static int damageValue(double amount){return (int)Math.max(1,Math.min(Integer.MAX_VALUE,Math.round(amount)));}
    static int glyphSkill(int color,int slot,int digit){return 19200+color*100+slot*10+digit;}
    static void show(Creature attacker,int amount,int color)
    {
        String digits=Integer.toString(amount);
        for(int slot=0;slot<digits.length();slot++){
            int digit=digits.charAt(digits.length()-slot-1)-'0';
            // Native item casting path has no animation and does not alter server combat state.
            attacker.broadcastPacket(new MagicSkillUse(attacker,attacker,glyphSkill(color,slot,digit),1,0,0));
        }
    }
    @Override public String[] getCommandList(){return new String[]{"vfx"};}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        if(!p.isGM())return true;
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        if(!action.equals("prueba")){p.sendMessage(".vfx prueba: nativo, numero 1234, flechas al cielo y circulo. Quedate quieto 10 segundos.");return true;}
        p.sendMessage("VFX 1/5: fuego nativo sobre tu personaje.");emit(p,19600);
        ThreadPool.schedule(()->{if(p.isSpawned()){p.sendMessage("VFX 2/5: numero 1234 sobre tu personaje.");show(p,1234,0);}},2000);
        ThreadPool.schedule(()->{if(p.isSpawned()){p.sendMessage("VFX 3/5: 50 flechas al cielo.");emit(p,19012);}},4000);
        ThreadPool.schedule(()->{if(p.isSpawned()){p.sendMessage("VFX 4/5: circulo de area.");emit(p,19010);}},6000);
        ThreadPool.schedule(()->{if(p.isSpawned()){p.sendMessage("VFX 5/5: 50 flechas de fuego caen dentro del circulo, sin dano.");emit(p,19008,1);}},8000);
        ThreadPool.schedule(()->{if(p.isSpawned())emit(p,19008,2);},8500);
        ThreadPool.schedule(()->{if(p.isSpawned())emit(p,19008,3);},9000);
        return true;
    }
    private static void emit(Creature c,int skill,int level){c.broadcastPacket(new MagicSkillUse(c,c,skill,level,0,0));}
    private static void emit(Creature c,int skill){c.broadcastPacket(new MagicSkillUse(c,c,skill,1,0,0));}
    public static void main(String[] args){new WorldDamageNumbers();}
}
