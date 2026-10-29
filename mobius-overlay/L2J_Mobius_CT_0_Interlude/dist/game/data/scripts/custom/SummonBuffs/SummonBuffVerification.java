package custom.SummonBuffs;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.config.custom.SchemeBufferConfig;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.entity.actor.instance.SchemeBuffer;
import org.l2jmobius.gameserver.entity.actor.instance.Servitor;
import org.l2jmobius.gameserver.mechanics.script.Script;
import custom.AmberContract.AmberServitor;

/** Opt-in, offline reserved owner; real NPC bypass, real effects/stat changes, no grants or saves. */
public class SummonBuffVerification extends Script
{
    private static final Logger LOG=Logger.getLogger(SummonBuffVerification.class.getName());
    private int checks;
    public SummonBuffVerification(){if(Boolean.getBoolean("lab.summonbuff.verify"))ThreadPool.schedule(this::verify,30000);}
    private void check(boolean value,String message){if(!value)throw new IllegalStateException(message);checks++;}
    private void verify()
    {
        Player p=null;SchemeBuffer buffer=null;Servitor summon=null;PlayerClass original=null;
        try{
            int id;
            try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("SELECT charId,online FROM characters WHERE char_name='AmberOwnerProbe' AND account_name='ambercontracttest'"))
            {try(var r=q.executeQuery()){if(!r.next()||r.getInt(2)!=0||World.getPlayer(r.getInt(1))!=null)throw new IllegalStateException("Offline probe unavailable");id=r.getInt(1);}}
            p=Player.load(id);check(p!=null&&!p.hasSummon(),"Offline probe has no existing summon");original=p.getPlayerClass();p.fullRestore();
            var skills=p.getAllSkills().stream().collect(java.util.stream.Collectors.toMap(s->s.getId(),s->s.getLevel()));int shortcutCount=p.getAllShortcuts().size();
            buffer=new SchemeBuffer(NpcData.getInstance().getTemplate(50008));
            String menu=Files.readString(Path.of(buffer.getHtmlPath(50008,0)));
            for(String action:new String[]{"autobuff;pet;auto","autobuff;pet;fighter","autobuff;pet;mage","autobuff;me"})check(menu.contains(action),"Menu exposes registered NPC action "+action);
            for(int ownerClass:new int[]{103,90}){
                p.setTemplate(PlayerClass.getPlayerClass(ownerClass));
                check(SchemeBuffer.autoBuffCategory(p).equals(ownerClass==103?"MAGE_GROUP":"FIGHTER_GROUP"),"Player preset retains original class detection");
                for(int npcId:new int[]{902501,14111,14207,14251,14391,14435,14575,14619,14799,14836,14837,14838}){
                    var template=NpcData.getInstance().getTemplate(npcId);check(template!=null,"Native summon template available "+npcId);
                    summon=npcId==902501?new AmberServitor(template,p):new Servitor(template,p);p.setPet(summon);summon.fullRestore();
                    boolean mage=java.util.Set.of(14251,14391,14435,14619,14837).contains(npcId);
                    check(SchemeBuffer.autoBuffCategory(summon).equals(mage?"MAGE_GROUP":"FIGHTER_GROUP"),"Summon chooses own profile, independent of owner "+ownerClass+" npc="+npcId);
                    double attack=summon.getPAtk(null),speed=summon.getPAtkSpd(),magic=summon.getMAtk(null,null),cast=summon.getMAtkSpd();
                    var ownerEffects=p.getEffectList().getEffects().stream().map(b->b.getSkill().getId()).collect(java.util.stream.Collectors.toSet());
                    buffer.onBypassFeedback(p,"autobuff;pet;auto");
                    int offense=mage?1059:1068,tempo=mage?1085:1086;
                    check(summon.isAffectedBySkill(offense)&&summon.isAffectedBySkill(tempo),"Actual NPC bypass applies offense and speed buffs");
                    check(!summon.isAffectedBySkill(mage?1068:1059)&&!summon.isAffectedBySkill(mage?1086:1085),"Automatic preset avoids the opposite offensive profile");
                    check(mage?summon.getMAtk(null,null)>magic&&summon.getMAtkSpd()>cast:summon.getPAtk(null)>attack&&summon.getPAtkSpd()>speed,"Real summon combat stats increase");
                    var buff=summon.getEffectList().getBuffInfoBySkillId(tempo);
                    check(buff!=null&&buff.getTime()>SchemeBufferConfig.BUFFER_DURATION_SECONDS-5&&buff.getTime()<=SchemeBufferConfig.BUFFER_DURATION_SECONDS,"Summon uses configured NPC buff duration");
                    check(ownerEffects.equals(p.getEffectList().getEffects().stream().map(b->b.getSkill().getId()).collect(java.util.stream.Collectors.toSet())),"Summon buff does not change owner's effects");
                    check(SchemeBuffer.autoBuffCategory(summon).equals(mage?"MAGE_GROUP":"FIGHTER_GROUP"),"Buffed stats cannot change automatic classification");
                    summon.stopAllEffects();buffer.onBypassFeedback(p,"autobuff;pet;invalid");check(summon.getEffectList().getEffects().isEmpty(),"Invalid profile grants no effects");
                    if(npcId==902501){
                        buffer.onBypassFeedback(p,"autobuff;pet;mage");check(summon.isAffectedBySkill(1059)&&summon.isAffectedBySkill(1085),"Explicit mage override available for custom/mixed summons");
                        check(SchemeBuffer.autoBuffCategory(summon).equals("FIGHTER_GROUP"),"Override does not alter Amber's underlying classification");
                        summon.stopAllEffects();buffer.onBypassFeedback(p,"autobuff;pet;fighter");check(summon.isAffectedBySkill(1068)&&summon.isAffectedBySkill(1086),"Explicit fighter override applies real effects");
                    }
                    summon.stopAllEffects();summon.deleteMe(p);summon=null;
                }
            }
            var before=p.getEffectList().getEffects().size();buffer.onBypassFeedback(p,"autobuff;pet;auto");check(!p.hasSummon()&&p.getEffectList().getEffects().size()==before,"Missing summon never buffs owner by mistake");
            p.setTemplate(original);check(skills.equals(p.getAllSkills().stream().collect(java.util.stream.Collectors.toMap(s->s.getId(),s->s.getLevel())))&&shortcutCount==p.getAllShortcuts().size(),"No learned skills, levels or shortcuts changed");
            LOG.info("SummonBuffVerification SUCCESS: "+checks+" checks; 12 summon templates x mage/fighter owner, actual NPC bypass/effects/stats/duration, Amber and overrides, no owner mutations.");
        }catch(Exception e){LOG.log(java.util.logging.Level.SEVERE,"SummonBuffVerification FAILED after "+checks+" checks",e);}
        finally{
            if(summon!=null){summon.stopAllEffects();summon.deleteMe(p);}
            if(buffer!=null)buffer.deleteMe();
            if(p!=null){if(original!=null)p.setTemplate(original);p.setOnlineStatus(true,false);p.deleteMe();}
        }
    }
    public static void main(String[] args){new SummonBuffVerification();}
}
