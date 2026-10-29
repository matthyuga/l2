package custom.RaceCustomization;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.Arrays;
import java.util.concurrent.CompletableFuture;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.data.xml.HennaData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Opt-in real-engine verification, never loads or changes a user character. */
public class RaceCustomizationVerification extends Script
{
    private static final Logger LOG=Logger.getLogger(RaceCustomizationVerification.class.getName());
    private int checks;
    public RaceCustomizationVerification(){if(Boolean.getBoolean("lab.race.verify"))ThreadPool.schedule(this::verify,20000);}
    private void check(boolean ok,String step){if(!ok)throw new IllegalStateException(step);checks++;}
    private static void buffs(Player p)
    {
        for(int[] buff:new int[][]{{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},{273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1},{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}})SkillData.getInstance().getSkill(buff[0],buff[1]).applyEffects(p,p);
    }
    private void verify()
    {
        Player p=null;
        try
        {
            int id=0;
            try(Connection con=DatabaseFactory.getConnection();PreparedStatement ps=con.prepareStatement("SELECT charId,account_name,online FROM characters WHERE char_name='RaceMenuProbe'"))
            {
                try(var rs=ps.executeQuery())
                {
                    if(rs.next())
                    {
                        if(!"racialmenutest".equals(rs.getString("account_name"))||rs.getInt("online")!=0||World.getPlayer(rs.getInt("charId"))!=null)throw new IllegalStateException("Reserved probe unavailable");
                        id=rs.getInt("charId");
                    }
                }
            }
            p=id==0?Player.create(PlayerTemplateData.getInstance().getTemplate(103),"racialmenutest","RaceMenuProbe",new PlayerAppearance((byte)0,(byte)0,(byte)0,false)):Player.load(id);
            if(p==null)throw new IllegalStateException("Probe unavailable");
            p.setOnlineStatus(true,false);p.setDead(false);p.setActiveClass(0);p.setRacialOrigin(Race.HUMAN,false);
            p.getStat().setExp(ExperienceData.getInstance().getExpForLevel(80));p.getStat().setLevel((byte)80);p.rewardSkills();
            int[] subs={94,106,113};
            for(int slot=1;slot<=3;slot++)
            {
                if(!p.getSubClasses().containsKey(slot)&&!p.addSubClass(subs[slot-1],slot))throw new IllegalStateException("Probe subclass failed");
                p.setActiveClass(slot);p.getStat().setExp(ExperienceData.getInstance().getExpForLevel(80));p.getStat().setLevel((byte)80);p.rewardSkills();
            }
            p.setActiveClass(0);
            if(id==0)
            {
                for(int itemId:new int[]{6383,6384,6385,6386,6377,6608,858,858,889,889,920})
                {
                    var item=p.getInventory().addItem(ItemProcessType.NONE,itemId,1,p,null);item.setEnchantLevel(4);p.getInventory().equipItem(item);item.updateDatabase(true);
                }
                check(p.addHenna(HennaData.getInstance().getHenna(175)),"INT dye");
                check(p.addHenna(HennaData.getInstance().getHenna(180)),"WIT dye");
            }
            buffs(p);
            p.setCurrentHpMp(p.getMaxHp(),p.getMaxMp());p.setCurrentCp(p.getMaxCp());
            int main=p.getBaseClass(),active=p.getPlayerClass().getId(),skills=p.getAllSkills().size();
            String subRecipe=p.getSubClasses().entrySet().stream().sorted(java.util.Map.Entry.comparingByKey()).map(e->e.getKey()+":"+e.getValue().getId()+":"+e.getValue().getLevel()).toList().toString();
            String initial=RaceCustomization.fingerprint(p);double hp=p.getCurrentHp(),mp=p.getCurrentMp(),cp=p.getCurrentCp();
            Player actor=p;double[] baseline=RaceCustomization.readStats(p);
            for(Race race:new Race[]{Race.HUMAN,Race.ELF,Race.DARK_ELF,Race.ORC,Race.DWARF})
            {
                for(boolean mage:new boolean[]{false,true})
                {
                    if(race==Race.DWARF&&mage)continue;
                    double[] projected=RaceCustomization.project(p,race,mage);
                    check(initial.equals(RaceCustomization.fingerprint(p)),"Projection mutated character "+race+"/"+mage);
                    check(p.getCurrentHp()==hp&&p.getCurrentCp()==cp&&p.getCurrentMp()==mp,"Projection changed resources");
                    double[] concurrent=p.previewRacialStats(race,mage,()->CompletableFuture.supplyAsync(()->RaceCustomization.readStats(actor)).join());
                    check(RaceCustomization.close(baseline,concurrent),"Preview leaked across threads");
                    p.setRacialStatsOrigin(race,mage);
                    check(RaceCustomization.close(projected,RaceCustomization.readStats(p)),"Projection mismatch "+race+"/"+mage);
                    p.setRacialStatsOrigin(Race.HUMAN,false);RaceCustomization.readStats(p);
                    p.setCurrentHpMp(hp,mp);p.setCurrentCp(cp);
                }
            }
            try{p.previewRacialStats(Race.ELF,true,()->{throw new IllegalStateException("expected");});}catch(IllegalStateException expected){}
            check(!p.isRacialStatsPreview()&&RaceCustomization.close(baseline,RaceCustomization.readStats(p)),"Preview exception did not restore context");
            // All owned slots must supply native traits, including inactive subclasses.
            Race[] nativeRaces={Race.ELF,Race.HUMAN,Race.DARK_ELF,Race.ORC};
            boolean[] nativeMage={true,true,false,false};
            for(int slot=0;slot<=3;slot++)
            {
                var selection=new RaceCustomization.Selection(p);selection.selectClass(p,slot);selection.visual=true;selection.stats=true;
                check(RaceCustomization.destinationRace(p,selection)==nativeRaces[slot]&&RaceCustomization.destinationStats(p,selection)==nativeRaces[slot]&&RaceCustomization.destinationMage(p,selection)==nativeMage[slot],"Wrong native origin for owned slot "+slot);
                double[] nativeProjection=RaceCustomization.project(p,nativeRaces[slot],nativeMage[slot]);
                String menu=RaceCustomization.comparisonHtml(p,selection);
                check(menu.length()<7800&&menu.indexOf("value=\"Confirmar\"")<menu.indexOf("STR base")&&menu.contains("value=\"Cancelar\"")&&menu.contains("value=\"Aplicar\"")&&menu.contains(".raza unconfirmed"),"Controls missing/hidden or application lacks confirmation");
                check(p.getPlayerClass().getId()==active&&p.getClassIndex()==0&&RaceCustomization.close(baseline,RaceCustomization.readStats(p)),"Class selection/preview changed active class or attributes");
                RaceCustomization.applyConfiguration(p,Race.HUMAN,RaceCustomization.destinationStats(p,selection),RaceCustomization.destinationMage(p,selection));
                check(RaceCustomization.close(nativeProjection,RaceCustomization.readStats(p)),"Owned slot projection differs from application "+slot);
                p.setRacialStatsOrigin(Race.HUMAN,false);RaceCustomization.readStats(p);
            }
            var selected=new RaceCustomization.Selection(p);selected.selectClass(p,0);
            selected.visual=true;
            check(RaceCustomization.destinationRace(p,selected)==Race.ELF&&RaceCustomization.destinationStats(p,selected)==Race.HUMAN&&!RaceCustomization.destinationMage(p,selected),"Class visual-only did not retain racial attributes");
            selected.visual=false;selected.stats=true;
            check(RaceCustomization.destinationRace(p,selected)==Race.HUMAN&&RaceCustomization.destinationStats(p,selected)==Race.ELF&&RaceCustomization.destinationMage(p,selected),"Class attributes-only did not retain appearance");
            selected=new RaceCustomization.Selection(p);
            check(!selected.visual&&!selected.stats&&RaceCustomization.destinationRace(p,selected)==p.getRace()&&RaceCustomization.destinationStats(p,selected)==p.getRacialStatRace(),"Cancelled/reset selection leaves effective changes");
            check(RaceCustomization.originForClass(PlayerClass.MYSTIC_MUSE)==3&&RaceCustomization.originForClass(PlayerClass.PALADIN)==0&&RaceCustomization.originForClass(PlayerClass.PHANTOM_SUMMONER)==5&&RaceCustomization.originForClass(PlayerClass.OVERLORD)==7&&RaceCustomization.originForClass(PlayerClass.MAESTRO)==8,"User class or dwarf origin mapping wrong");
            try{RaceCustomization.classAtSlot(p,4);throw new IllegalStateException("Invalid slot accepted");}catch(IllegalArgumentException expected){checks++;}
            // All three effective modes and identical selection, with the real application path.
            RaceCustomization.applyConfiguration(p,Race.ORC,Race.HUMAN,false);
            check(p.getRace()==Race.ORC&&p.getRacialStatRace()==Race.HUMAN&&RaceCustomization.close(baseline,RaceCustomization.readStats(p)),"Visual-only changes stats");
            double[] elven=RaceCustomization.project(p,Race.ELF,true);
            hp=p.getCurrentHp();mp=p.getCurrentMp();cp=p.getCurrentCp();
            RaceCustomization.applyConfiguration(p,Race.ORC,Race.ELF,true);
            check(p.getRace()==Race.ORC&&RaceCustomization.close(elven,RaceCustomization.readStats(p)),"Stats-only changes appearance/result");
            check(p.getCurrentHp()<=hp&&p.getCurrentMp()<=mp&&p.getCurrentCp()<=cp,"Apply replenished resources");
            double[] dark=RaceCustomization.project(p,Race.DARK_ELF,true);
            RaceCustomization.applyConfiguration(p,Race.DWARF,Race.DARK_ELF,true);
            check(p.getRace()==Race.DWARF&&RaceCustomization.close(dark,RaceCustomization.readStats(p)),"Independent combined destinations");
            RaceCustomization.applyConfiguration(p,Race.DWARF,Race.DARK_ELF,true);
            check(p.getBaseClass()==main&&p.getPlayerClass().getId()==active&&p.getAllSkills().size()==skills,"Application changed class/skills");
            check(subRecipe.equals(p.getSubClasses().entrySet().stream().sorted(java.util.Map.Entry.comparingByKey()).map(e->e.getKey()+":"+e.getValue().getId()+":"+e.getValue().getLevel()).toList().toString()),"Application changed subclasses");
            check(RaceCustomization.blockedReason(p)!=null,"Non-GM could apply");
            String finalFingerprint=RaceCustomization.fingerprint(p);
            id=p.getObjectId();p.storeMe();p.deleteMe();p.setOnlineStatus(false,true);p=null;
            p=Player.load(id);if(p==null)throw new IllegalStateException("Reload failed");p.setOnlineStatus(true,false);p.stopAllEffects();buffs(p);
            check(p.getRace()==Race.DWARF&&p.getRacialStatRace()==Race.DARK_ELF&&p.isRacialMage(),"Independent origins lost on reload");
            check(RaceCustomization.close(dark,RaceCustomization.readStats(p)),"Stats lost on reload");
            check(finalFingerprint.equals(RaceCustomization.fingerprint(p)),"Equipment/skills/origins changed on reload");
            p.setTitle("Race menu tests OK");p.setXYZ(147450,46350,-3400);
            LOG.info("RaceCustomizationVerification SUCCESS: "+checks+" checks; 9 origins, 4 class slots, menu controls, previews isolated, 3 modes, resources and persistence PASS.");
        }
        catch(Exception e){LOG.log(Level.SEVERE,"RaceCustomizationVerification FAILED",e);}
        finally{if(p!=null){p.storeMe();p.deleteMe();p.setOnlineStatus(false,true);}}
    }
    public static void main(String[] args){new RaceCustomizationVerification();}
}
