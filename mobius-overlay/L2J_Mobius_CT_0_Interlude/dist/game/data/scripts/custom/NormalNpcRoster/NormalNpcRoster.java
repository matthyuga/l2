package custom.NormalNpcRoster;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.data.xml.HennaData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.stats.Stat;
import org.l2jmobius.gameserver.mechanics.stats.functions.AbstractFunction;
import org.l2jmobius.gameserver.mechanics.stats.functions.FuncSet;
import custom.LabTelemetry.LabTelemetry;

/** Builds real-player stat sources and applies their calculated combat sheet to the nine NPC rivals. */
public class NormalNpcRoster extends Script
{
    private static final Logger LOGGER = Logger.getLogger(NormalNpcRoster.class.getName());
    private static final String VERSION = "normal-pvp-level80-s4-v1";
    private static final int FIRST_NPC = 901100;
    private static final int LAST_NPC = 901108;
    private static final int[][] COMMON_BUFFS = {{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
    private static final int[][] PHYSICAL_BUFFS = {{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1},
        {271,1},{272,1},{274,1},{275,1},{269,1},{266,1},{264,1},{267,1},{268,1},{304,1}};
    private static final int[][] MAGE_BUFFS = {{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},
        {273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1}};
    private static final int[][] JEWELRY = {{858,2},{858,2},{889,2},{889,2},{920,1}};
    private static final Map<Integer, List<AbstractFunction>> APPLIED = new HashMap<>();
    private static final Profile[] PROFILES =
    {
        new Profile(901100,"ArenaArden","telemetryarena1",89,Race.HUMAN,false,false,6364,new int[]{169,174},"FIGHTER"),
        new Profile(901101,"ArenaSelene","telemetryarena1",97,Race.HUMAN,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901102,"ArenaEryndor","telemetryarena1",102,Race.ELF,false,true,7577,new int[]{169,174},"ARCHER"),
        new Profile(901103,"ArenaLethiel","telemetryarena1",103,Race.ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901104,"ArenaVaelkor","telemetryarena1",108,Race.DARK_ELF,false,true,6367,new int[]{169,174},"FIGHTER"),
        new Profile(901105,"ArenaMyrentha","telemetryarena1",110,Race.DARK_ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901106,"ArenaGorvak","telemetryarena1",113,Race.ORC,false,false,6369,new int[]{169,174},"FIGHTER"),
        new Profile(901107,"ArenaZhurak","telemetryarena2",115,Race.ORC,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901108,"ArenaBrunna","telemetryarena2",118,Race.DWARF,false,false,6365,new int[]{169,174},"FIGHTER")
    };

    private NormalNpcRoster() { ThreadPool.schedule(this::prepareAndApply,45000); }

    private void prepareAndApply()
    {
        try
        {
            try (var con=DatabaseFactory.getConnection();var st=con.createStatement())
            {
                st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_normal_npc_profiles (npc_template_id INT NOT NULL PRIMARY KEY,char_id INT UNSIGNED NOT NULL UNIQUE,char_name VARCHAR(35) NOT NULL UNIQUE,recipe_version VARCHAR(40) NOT NULL,prepared_ms BIGINT UNSIGNED NOT NULL,role_name VARCHAR(20) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            }
            int ready=0;
            for(Profile profile:PROFILES)
            {
                try { prepareAndApplyOne(profile);ready++; }
                catch(Exception e) { LOGGER.log(Level.SEVERE,"No se aplico perfil normal a "+profile.name+"; ese NPC conserva su plantilla",e); }
            }
            if(ready!=PROFILES.length) throw new IllegalStateException("Perfiles listos "+ready+"/"+PROFILES.length);
            LOGGER.info("Roster Coliseo: nueve NPC vinculados a perfiles Player normales nivel 80, +4, con raza, dyes y buffs; la IA y el roster quedan intactos.");
        }
        catch(Exception e) { LOGGER.log(Level.SEVERE,"Roster Coliseo normal: preparacion parcial; los NPC sin perfil permanecen con su plantilla existente.",e); }
    }

    private void prepareAndApplyOne(Profile spec) throws Exception
    {
        int id=0; boolean prepared=false;
        try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT c.charId,c.online,c.account_name,p.recipe_version,p.npc_template_id FROM characters c LEFT JOIN lab_normal_npc_profiles p ON p.char_id=c.charId WHERE c.char_name=?"))
        {
            ps.setString(1,spec.name);
            try(var rs=ps.executeQuery())
            {
                if(rs.next())
                {
                    if(!spec.account.equals(rs.getString("account_name")) || rs.getInt("npc_template_id")!=spec.npcId || !VERSION.equals(rs.getString("recipe_version")))
                        throw new IllegalStateException("Perfil reservado o receta distinta: "+spec.name+"; no se sobrescribe.");
                    if(rs.getInt("online")!=0) throw new IllegalStateException("Perfil conectado; no se modifica: "+spec.name);
                    id=rs.getInt("charId");prepared=true;
                }
            }
        }
        Player player=prepared?Player.load(id):Player.create(PlayerTemplateData.getInstance().getTemplate(spec.classId),spec.account,spec.name,new PlayerAppearance((byte)0,(byte)0,(byte)0,spec.female));
        if(player==null) throw new IllegalStateException("No se pudo crear/cargar "+spec.name);
        player.setOnlineStatus(true,false);
        try
        {
            if(player.getRace()!=spec.race || player.getBaseClass()!=spec.classId || !player.getSubClasses().isEmpty())
                throw new IllegalStateException("Raza, principal o subs incorrectas: "+spec.name);
            player.setDead(false);
            if(!prepared)
            {
                maximize(player);
                equip(player,spec);
                for(int dye:spec.dyes) if(!player.addHenna(HennaData.getInstance().getHenna(dye))) throw new IllegalStateException("Dye no permitido "+dye+" para "+spec.name);
                player.setTitle("Perfil PvP normal +4");
                player.setXYZ(147450,spec.female?46550:46350,-3400);
                if(player.getInventory().addItem(ItemProcessType.NONE,57,1000000,player,null)==null) throw new IllegalStateException("No se pudo asignar consumibles a "+spec.name);
                player.storeMe();
            }
            player.stopAllEffects();
            applyBuffs(player,spec.buffSet);
            player.setCurrentHpMp(player.getMaxHp(),player.getMaxMp());player.setCurrentCp(player.getMaxCp());player.storeMe();
            if(!LabTelemetry.capturePilotStatsNow(player)) throw new IllegalStateException("No se pudo guardar telemetria de "+spec.name);
            if(!prepared)
            {
                try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("INSERT INTO lab_normal_npc_profiles (npc_template_id,char_id,char_name,recipe_version,prepared_ms,role_name) VALUES (?,?,?,?,?,?)"))
                {ps.setInt(1,spec.npcId);ps.setInt(2,player.getObjectId());ps.setString(3,spec.name);ps.setString(4,VERSION);ps.setLong(5,System.currentTimeMillis());ps.setString(6,spec.role);ps.executeUpdate();}
            }
            applyNpcStats(spec,player);
            LOGGER.info("Rival normal calculado: "+spec.name+" "+spec.race+" class="+player.getPlayerClass().getId()+" MAtk="+player.getMAtk(null,null)+" PAtk="+player.getPAtk(null)+" stats="+player.getSTR()+"/"+player.getDEX()+"/"+player.getCON()+"/"+player.getINT()+"/"+player.getWIT()+"/"+player.getMEN());
        }
        finally { player.storeMe();player.deleteMe();player.setOnlineStatus(false,true); }
    }

    private static void maximize(Player p)
    {
        int level=ExperienceData.getInstance().getMaxLevel()-1;p.getStat().setExp(ExperienceData.getInstance().getExpForLevel(level));p.getStat().setLevel((byte)level);p.rewardSkills();p.storeMe();
    }

    private static void equip(Player player,Profile p)
    {
        int[] armor=p.mage?new int[]{6383,6384,6385,6386,6377}:p.light?new int[]{6379,6380,6381,6382}:new int[]{6373,6374,6375,6376,6378};
        List<Integer> gear=new ArrayList<>();for(int id:armor)gear.add(id);for(int[] j:JEWELRY)for(int i=0;i<j[1];i++)gear.add(j[0]);gear.add(p.weapon);
        for(int id:gear){Item item=player.getInventory().addItem(ItemProcessType.NONE,id,1,player,null);if(item==null)throw new IllegalStateException("Objeto inexistente "+id+" para "+p.name);item.setEnchantLevel(4);player.getInventory().equipItem(item);item.updateDatabase(true);}
    }

    private static void applyBuffs(Player p,String role)
    {
        int[][] extras=role.equals("MAGE")?MAGE_BUFFS:PHYSICAL_BUFFS;
        for(int[][] group:new int[][][]{COMMON_BUFFS,extras})for(int[] entry:group){Skill skill=SkillData.getInstance().getSkill(entry[0],entry[1]);if(skill==null)throw new IllegalStateException("Buff inexistente "+entry[0]+":"+entry[1]);skill.applyEffects(p,p);}
    }

    private static void applyNpcStats(Profile p,Player source)
    {
        for(WorldObject obj:World.getVisibleObjects())
        {
            if(!obj.isNpc()||obj.getId()!=p.npcId||obj.getInstanceId()!=0||obj.calculateDistance2D(148900,46100, -3400)>5000)continue;
            Npc npc=obj.asNpc();List<AbstractFunction> old=APPLIED.remove(npc.getObjectId());if(old!=null)npc.removeStatFuncs(old.toArray(AbstractFunction[]::new));
            List<AbstractFunction> funcs=new ArrayList<>();
            set(funcs,npc,Stat.STAT_STR,source.getSTR());set(funcs,npc,Stat.STAT_DEX,source.getDEX());set(funcs,npc,Stat.STAT_CON,source.getCON());set(funcs,npc,Stat.STAT_INT,source.getINT());set(funcs,npc,Stat.STAT_WIT,source.getWIT());set(funcs,npc,Stat.STAT_MEN,source.getMEN());
            set(funcs,npc,Stat.MAX_HP,source.getMaxHp());set(funcs,npc,Stat.MAX_MP,source.getMaxMp());set(funcs,npc,Stat.MAX_CP,source.getMaxCp());
            set(funcs,npc,Stat.POWER_ATTACK,source.getPAtk(null));set(funcs,npc,Stat.MAGIC_ATTACK,source.getMAtk(null,null));set(funcs,npc,Stat.POWER_DEFENCE,source.getPDef(null));set(funcs,npc,Stat.MAGIC_DEFENCE,source.getMDef(null,null));
            set(funcs,npc,Stat.POWER_ATTACK_SPEED,source.getPAtkSpd());set(funcs,npc,Stat.MAGIC_ATTACK_SPEED,source.getMAtkSpd());set(funcs,npc,Stat.MOVE_SPEED,source.getRunSpeed());
            set(funcs,npc,Stat.ACCURACY_COMBAT,source.getStat().getAccuracy());set(funcs,npc,Stat.EVASION_RATE,source.getStat().getEvasionRate(null));set(funcs,npc,Stat.CRITICAL_RATE,source.getStat().getCriticalHit(null,null));set(funcs,npc,Stat.MCRITICAL_RATE,source.getStat().getMCriticalHit(null,null)/10.0);
            npc.addStatFuncs(funcs);APPLIED.put(npc.getObjectId(),funcs);npc.setCurrentHpMp(npc.getMaxHp(),npc.getMaxMp());npc.setCurrentCp(npc.getMaxCp());
            for(int[][] group:new int[][][]{COMMON_BUFFS,p.buffSet.equals("MAGE")?MAGE_BUFFS:PHYSICAL_BUFFS})for(int[] entry:group){Skill skill=SkillData.getInstance().getSkill(entry[0],entry[1]);if(skill!=null)skill.applyEffects(npc,npc);}
        }
    }

    private static void set(List<AbstractFunction> functions,Npc npc,Stat stat,double value)
    {
        functions.add(new FuncSet(stat,0x10000,npc,value,null));
    }

    private static final class Profile
    {
        final int npcId,classId,weapon;final String name,account,role,buffSet;final Race race;final boolean mage,light,female;final int[] dyes;
        Profile(int npcId,String name,String account,int classId,Race race,boolean mage,boolean light,int weapon,int[] dyes,String role)
        {this.npcId=npcId;this.name=name;this.account=account;this.classId=classId;this.race=race;this.mage=mage;this.light=light;this.weapon=weapon;this.dyes=dyes;this.role=role;this.buffSet=role;this.female=name.endsWith("Selene")||name.endsWith("Lethiel")||name.endsWith("Myrentha")||name.endsWith("Brunna");}
    }

    public static void main(String[] args){new NormalNpcRoster();}
}
