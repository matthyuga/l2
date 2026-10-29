package custom.AmberContract;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.logging.Level;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.item.enums.ShotType;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Opt-in, reserved headless GM in a private instance; no human character is used. */
public class AmberModelVariantsVerification extends Script
{
    private int checks;
    public AmberModelVariantsVerification(){if(Boolean.getBoolean("lab.amber.models.verify"))ThreadPool.schedule(this::verify,45000);}
    private void check(boolean condition,String label){if(!condition)throw new IllegalStateException(label);checks++;}
    private Player probe(int instanceId)throws Exception{
        int id=0;
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("SELECT charId,account_name,online FROM characters WHERE char_name=?")){
            q.setString(1,"AmberModelsProbe");try(var r=q.executeQuery()){if(r.next()){
                if(!"ambermodeltest".equals(r.getString(2))||r.getInt(3)!=0||World.getPlayer(r.getInt(1))!=null)throw new IllegalStateException("Reserved model probe unavailable");id=r.getInt(1);
            }}
        }
        Player p=id==0?Player.create(PlayerTemplateData.getInstance().getTemplate(103),"ambermodeltest","AmberModelsProbe",new PlayerAppearance((byte)0,(byte)0,(byte)0,false)):Player.load(id);
        if(p==null)throw new IllegalStateException("Probe creation failed");
        p.setLabControlled(true);p.setOnlineStatus(true,true);p.setDead(false);p.stopAllEffects();p.setAccessLevel(100);
        p.getStat().setExp(ExperienceData.getInstance().getExpForLevel(80));p.getStat().setLevel((byte)80);p.rewardSkills();p.setInstanceId(instanceId);p.setEnteredWorld();p.spawnMe(148900,46100,-3408);p.fullRestore();
        return p;
    }
    private void verify(){
        Player p=null;int instanceId=0;
        try{
            instanceId=InstanceManager.getInstance().createDynamicInstance(0).getId();p=probe(instanceId);
            p.getVariables().set(AmberContract.CONTRACT,true);p.getVariables().set(AmberModelVariants.VARIABLE,1);p.getVariables().set("AMBER_REUSE_19001",0L);
            AmberContract.grant(p);var invoke=SkillData.getInstance().getSkill(AmberContract.INVOKE,1);p.enableSkill(invoke);p.removeTimeStamp(invoke);
            AmberContract.order(p,AmberContract.INVOKE);check(p.getSummon() instanceof AmberServitor,"normal native invocation creates Amber");
            AmberServitor a=(AmberServitor)p.getSummon();a.setFollowStatus(false);a.stopMove(null);a.assist.enable(false);
            check(a.getId()==AmberContract.SUMMON&&a.getTemplate().getDisplayId()==59002,"default remains original Amber");
            var handler=VoicedCommandHandler.getInstance().getHandler("ambers");check(handler!=null,"selector voice handler registered");
            SkillData.getInstance().getSkill(AmberContract.FIRE_BUFF,1).applyEffects(a,a);check(a.getEffectList().getBuffInfoBySkillId(AmberContract.FIRE_BUFF)!=null,"probe fire buff active");
            a.setCurrentHp(a.getMaxHp()*0.6);a.setCurrentMp(a.getMaxMp()*0.4);a.setChargedShot(ShotType.SOULSHOTS,true);
            int objectId=a.getObjectId();long reuse=p.getVariables().getLong("AMBER_REUSE_19001",0);double hp=a.getCurrentHp(),mp=a.getCurrentMp(),patk=a.getPAtk(p),pdef=a.getPDef(p),maxHp=a.getMaxHp(),maxMp=a.getMaxMp();
            for(int choice:new int[]{2,3,1}){
                check(handler.onCommand("ambers",p,Integer.toString(choice)),"voice selector accepts variant"+choice);
                check(p.getSummon()==a&&a.getObjectId()==objectId,"same live summon identity"+choice);
                check(a.getId()==AmberModelVariants.TEMPLATES[choice-1],"selected template"+choice);
                check(a.getTemplate().getDisplayId()==(choice==1?59002:59018+choice),"selected client display"+choice);
                check(Math.abs(a.getCurrentHp()-hp)<0.001&&Math.abs(a.getCurrentMp()-mp)<0.001,"HP and MP unchanged"+choice);
                check(a.getMaxHp()==maxHp&&a.getMaxMp()==maxMp&&a.getPAtk(p)==patk&&a.getPDef(p)==pdef,"combat stats unchanged"+choice);
                check(a.getEffectList().getBuffInfoBySkillId(AmberContract.FIRE_BUFF)!=null&&a.isChargedShot(ShotType.SOULSHOTS),"fire effect and charged soulshot unchanged"+choice);
                check(p.getVariables().getLong("AMBER_REUSE_19001",0)==reuse,"invocation reuse unchanged"+choice);
                check(a.getKnownSkill(AmberContract.FIRE)!=null&&a.getKnownSkill(AmberContract.RAIN)!=null&&a.getWeapon()==6619,"same native skills and bow"+choice);
                check(AmberModelVariants.selection(p)==choice&&AmberModelVariants.templateId(p)==a.getId(),"future invocations remember model"+choice);
            }
            String html=AmberModelVariants.html(p);check(html.length()<8192&&html.contains("voice .ambers 1")&&html.contains("voice .ambers 2")&&html.contains("voice .ambers 3"),"all three menu buttons route correctly");
            a.charging=true;handler.onCommand("ambers",p,"2");check(a.getId()==AmberContract.SUMMON&&AmberModelVariants.selection(p)==1,"reject model change during rain charge");a.charging=false;
            handler.onCommand("ambers",p,"99");check(AmberModelVariants.selection(p)==1,"invalid selection cannot change model");
            p.setAccessLevel(0);handler.onCommand("ambers",p,"2");check(a.getId()==AmberContract.SUMMON,"non-GM cannot switch");p.setAccessLevel(100);
            a.stopAllEffects();a.unSummon(p);p.getVariables().set(AmberModelVariants.VARIABLE,3);p.getVariables().set("AMBER_REUSE_19001",0L);p.enableSkill(invoke);p.removeTimeStamp(invoke);
            AmberContract.order(p,AmberContract.INVOKE);check(p.getSummon() instanceof AmberServitor&&p.getSummon().getId()==902521,"fresh native invocation uses selected MMD model");
            AmberContract.LOG.info("AmberModelVariantsVerification SUCCESS: "+checks+" checks; three models, real summon identity, stats/resources/effects/shots/reuse preserved, native summon selection and action guards.");
        }catch(Exception e){AmberContract.LOG.log(Level.SEVERE,"AmberModelVariantsVerification FAILED after "+checks+" checks",e);}
        finally{
            if(p!=null){p.getVariables().set(AmberContract.CONTRACT,false);p.getVariables().set(AmberModelVariants.VARIABLE,1);AmberContract.cleanup(p);AmberContract.revokeSavedEffects(p);p.storeMe();p.deleteMe();p.setLabControlled(false);p.setOnlineStatus(false,true);}
            if(instanceId!=0)InstanceManager.getInstance().destroyInstance(instanceId);
        }
    }
    public static void main(String[] args){new AmberModelVariantsVerification();}
}
