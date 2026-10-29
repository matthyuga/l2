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
import org.l2jmobius.gameserver.config.PlayerConfig;
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
import custom.RealHumanPilots.RealHumanPilots;

/** Prepares real-player profiles and caches their combat sheets for NPC opponents spawned on demand. */
public class NormalNpcRoster extends Script implements org.l2jmobius.gameserver.handler.IVoicedCommandHandler
{
    private static final Logger LOGGER = Logger.getLogger(NormalNpcRoster.class.getName());
    private static final String VERSION = "normal-pvp-s4-hybrid-v2";
    private static final String LEGACY_VERSION = "normal-pvp-level80-s4-v1";
    private static final int[][] COMMON_BUFFS = {{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
    private static final int[][] PHYSICAL_BUFFS = {{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1},
        {271,1},{272,1},{274,1},{275,1},{269,1},{266,1},{264,1},{267,1},{268,1},{304,1}};
    private static final int[][] MAGE_BUFFS = {{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},
        {273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1}};
    private static final int[][] JEWELRY = {{858,2},{858,2},{889,2},{889,2},{920,1}};
    private static final Map<Integer, PreparedNpc> PREPARED = new HashMap<>();
    private static final Stat[] NPC_STATS = {Stat.STAT_STR,Stat.STAT_DEX,Stat.STAT_CON,Stat.STAT_INT,Stat.STAT_WIT,Stat.STAT_MEN,
        Stat.MAX_HP,Stat.MAX_MP,Stat.MAX_CP,Stat.POWER_ATTACK,Stat.MAGIC_ATTACK,Stat.POWER_DEFENCE,Stat.MAGIC_DEFENCE,
        Stat.POWER_ATTACK_SPEED,Stat.MAGIC_ATTACK_SPEED,Stat.MOVE_SPEED,Stat.ACCURACY_COMBAT,Stat.EVASION_RATE,Stat.CRITICAL_RATE,Stat.MCRITICAL_RATE};
    private static volatile boolean READY;
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
        new Profile(901108,"ArenaBrunna","telemetryarena2",118,Race.DWARF,false,false,6365,new int[]{169,174},"FIGHTER"),
        new Profile(901109,"ArenaKaelis","telemetryarena2",92,Race.HUMAN,false,true,7577,new int[]{169,174},"ARCHER"),
        new Profile(901110,"ArenaRiven","telemetryarena2",93,Race.HUMAN,false,true,6367,new int[]{169,174},"FIGHTER"),
        new Profile(901111,"ArenaNoctis","telemetryarena2",115,Race.ORC,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901112,"ArenaCaelan","telemetryarena3",92,Race.HUMAN,false,true,7577,new int[]{169,174},"ARCHER"),
        new Profile(901113,"ArenaIgnara","telemetryarena3",94,Race.HUMAN,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901114,"ArenaAelira","telemetryarena3",103,Race.ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901115,"ArenaKorvash","telemetryarena3",115,Race.ORC,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901116,"ArenaMorvain","telemetryarena3",95,Race.HUMAN,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901117,"ArenaSylira","telemetryarena3",110,Race.ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901118,"ArenaVelith","telemetryarena3",110,Race.DARK_ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901119,"ArenaDarion","telemetryarena4",88,Race.HUMAN,false,false,6580,new int[]{169,174},"FIGHTER"),
        new Profile(901120,"ArenaValerian","telemetryarena4",90,Race.HUMAN,false,false,6364,new int[]{169,174},"FIGHTER"),
        new Profile(901121,"ArenaMalrik","telemetryarena4",91,Race.HUMAN,false,false,6364,new int[]{169,174},"FIGHTER"),
        new Profile(901122,"ArenaLucien","telemetryarena4",96,Race.HUMAN,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901123,"ArenaSeraphine","telemetryarena4",98,Race.HUMAN,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901124,"ArenaDarius","telemetryarena4",89,Race.HUMAN,false,false,6607,new int[]{169,174},"FIGHTER"),
        new Profile(901125,"ArenaThalion","telemetryarena4",99,Race.ELF,false,false,6364,new int[]{169,174},"FIGHTER"),
        new Profile(901126,"ArenaElowen","telemetryarena5",100,Race.ELF,false,false,6364,new int[]{169,174},"FIGHTER"),
        new Profile(901127,"ArenaFaelith","telemetryarena5",104,Race.ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901128,"ArenaNerys","telemetryarena5",105,Race.ELF,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901129,"ArenaDraven","telemetryarena5",106,Race.DARK_ELF,false,false,6364,new int[]{169,174},"FIGHTER"),
        new Profile(901130,"ArenaNysera","telemetryarena5",107,Race.DARK_ELF,false,false,6580,new int[]{169,174},"FIGHTER"),
        new Profile(901131,"ArenaVeyron","telemetryarena5",109,Race.DARK_ELF,false,true,7577,new int[]{169,174},"ARCHER"),
        new Profile(901132,"ArenaZareth","telemetryarena5",111,Race.DARK_ELF,true,true,6608,new int[]{175,180},"MAGE"),
        new Profile(901133,"ArenaSaevra","telemetryarena6",112,Race.DARK_ELF,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901134,"ArenaRhogar","telemetryarena6",114,Race.ORC,false,true,6371,new int[]{169,174},"FIGHTER"),
        new Profile(901135,"ArenaMazhura","telemetryarena6",116,Race.ORC,true,true,6608,new int[]{180},"MAGE"),
        new Profile(901136,"ArenaUrkan","telemetryarena6",88,Race.ORC,false,false,6580,new int[]{169,174},"FIGHTER"),
        new Profile(901137,"ArenaDagna","telemetryarena6",117,Race.DWARF,false,false,6365,new int[]{169,174},"FIGHTER"),
        new Profile(901138,"ArenaBorin","telemetryarena6",90,Race.DWARF,false,false,6364,new int[]{169,174},"FIGHTER")
    };

    private static volatile boolean preparing;
    private NormalNpcRoster() {
        org.l2jmobius.gameserver.handler.VoicedCommandHandler.getInstance().registerHandler(this);
        LOGGER.info("ROSTER_MANUAL_READY: combat profiles deferred; use .roster preparar when required.");
    }
    @Override public String[] getCommandList(){return new String[]{"roster"};}
    @Override public synchronized boolean onCommand(String command,Player player,String params){
        if(!player.isGM()){player.sendMessage("Roster: acceso de laboratorio GM.");return true;}
        if(params!=null && params.trim().equalsIgnoreCase("preparar") && !READY && !preparing){
            preparing=true;
            ThreadPool.execute(()->{try{RealHumanPilots.prepareOnDemand();prepareAndApply();}finally{preparing=false;}});
        }
        player.sendMessage(READY?"Roster listo para los combates.":preparing?"Preparando perfiles de combate; consulta .roster estado.":"Roster en reposo. Usa .roster preparar para habilitar los combates de prueba.");
        return true;
    }

    private void prepareAndApply()
    {
        try
        {
            if(!PlayerConfig.CUMULATIVE_SUBCLASS_SKILLS || !PlayerConfig.CUMULATIVE_SUBCLASS_THIRD_SKILLS_ACTIVE_ONLY)
                throw new IllegalStateException("El roster requiere segunda acumulada y tercera solo activa");
            try (var con=DatabaseFactory.getConnection();var st=con.createStatement())
            {
                st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_normal_npc_profiles (npc_template_id INT NOT NULL PRIMARY KEY,char_id INT UNSIGNED NOT NULL UNIQUE,char_name VARCHAR(35) NOT NULL UNIQUE,recipe_version VARCHAR(40) NOT NULL,prepared_ms BIGINT UNSIGNED NOT NULL,role_name VARCHAR(20) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            }
            int ready=0;
            for(Profile profile:PROFILES)
            {
                try { prepareAndApplyOne(profile);ready++; }
                catch(Exception e) { LOGGER.log(Level.SEVERE,"No se preparo el perfil normal de "+profile.name,e); }
            }
            if(ready!=PROFILES.length) throw new IllegalStateException("Perfiles listos "+ready+"/"+PROFILES.length);
            READY=true;
            LOGGER.info("Roster Coliseo: "+ready+" perfiles Player preparados; rivales NPC aparecen solo durante su duelo.");
        }
        catch(Exception e) { LOGGER.log(Level.SEVERE,"Roster Coliseo normal: preparacion parcial; duelos bloqueados hasta preparar todos los perfiles.",e); }
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
                    boolean interruptedCreation=spec.npcId==901117 && rs.getString("recipe_version")==null && rs.getInt("npc_template_id")==0;
                    if(!spec.account.equals(rs.getString("account_name")) || (!interruptedCreation && (rs.getInt("npc_template_id")!=spec.npcId || !(VERSION.equals(rs.getString("recipe_version")) || LEGACY_VERSION.equals(rs.getString("recipe_version"))))))
                        throw new IllegalStateException("Perfil reservado o receta distinta: "+spec.name+"; no se sobrescribe.");
                    if(rs.getInt("online")!=0) throw new IllegalStateException("Perfil conectado; no se modifica: "+spec.name);
                    id=rs.getInt("charId");prepared=!interruptedCreation;
                }
            }
        }
        Player player=id>0?Player.load(id):Player.create(PlayerTemplateData.getInstance().getTemplate(spec.classId),spec.account,spec.name,new PlayerAppearance((byte)0,(byte)0,(byte)0,spec.female));
        if(player==null) throw new IllegalStateException("No se pudo crear/cargar "+spec.name);
        player.setOnlineStatus(true,false);
        double[] expectedStats=null;
        try
        {
            if(!prepared)
            {
                if(player.getLevel()!=1 || !player.getSubClasses().isEmpty() || !player.getInventory().getItems().isEmpty())
                    throw new IllegalStateException("Creacion incompleta con progreso; no se sobrescribe: "+spec.name);
                player.setRacialOrigin(spec.race,spec.mage);
            }
            if(player.getRace()!=spec.race || player.getBaseClass()!=spec.classId || player.isRacialMage()!=spec.mage)
                throw new IllegalStateException("Raza, principal o subs incorrectas: "+spec.name);
            // A pilot may have saved its active subclass at the end of a match.
            // Validate its persisted identity before selecting the existing main; never rebuild a recipe here.
            if(player.getClassIndex()!=0)
            {
                int savedSlot=player.getClassIndex();
                var active=player.getSubClasses().get(savedSlot);
                if(savedSlot<1 || savedSlot>3 || active==null || active.getId()!=player.getPlayerClass().getId())
                    throw new IllegalStateException("Sub activa guardada incorrecta: "+spec.name);
                player.setActiveClass(0);
                if(player.getClassIndex()!=0 || player.getPlayerClass().getId()!=spec.classId)
                    throw new IllegalStateException("No se pudo restaurar principal: "+spec.name);
                LOGGER.info("RosterSavedSubclass restored main: "+spec.name+" savedSlot="+savedSlot+" main="+spec.classId);
            }
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
            prepareSubclasses(player,spec);
            verifySlots(player,spec);
            player.stopAllEffects();
            applyBuffs(player,spec.buffSet);
            player.setCurrentHpMp(player.getMaxHp(),player.getMaxMp());player.setCurrentCp(player.getMaxCp());player.storeMe();
            expectedStats=stats(player);
            if(!LabTelemetry.capturePilotStatsNow(player)) throw new IllegalStateException("No se pudo guardar telemetria de "+spec.name);
            if(!prepared)
            {
                try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("INSERT INTO lab_normal_npc_profiles (npc_template_id,char_id,char_name,recipe_version,prepared_ms,role_name) VALUES (?,?,?,?,?,?)"))
                {ps.setInt(1,spec.npcId);ps.setInt(2,player.getObjectId());ps.setString(3,spec.name);ps.setString(4,VERSION);ps.setLong(5,System.currentTimeMillis());ps.setString(6,spec.role);ps.executeUpdate();}
            }
            cacheNpcStats(spec,player);
            try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("UPDATE lab_normal_npc_profiles SET recipe_version=?,prepared_ms=? WHERE char_id=?"))
            {ps.setString(1,VERSION);ps.setLong(2,System.currentTimeMillis());ps.setInt(3,player.getObjectId());ps.executeUpdate();}
            LOGGER.info("Rival normal calculado: "+spec.name+" "+spec.race+" class="+player.getPlayerClass().getId()+" MAtk="+player.getMAtk(null,null)+" PAtk="+player.getPAtk(null)+" stats="+player.getSTR()+"/"+player.getDEX()+"/"+player.getCON()+"/"+player.getINT()+"/"+player.getWIT()+"/"+player.getMEN());
        }
        finally { player.storeMe();player.deleteMe();player.setOnlineStatus(false,true); }
        Player reloaded=Player.load(player.getObjectId());
        if(reloaded==null) throw new IllegalStateException("No se pudo recargar "+spec.name);
        try
        {
            verifySlots(reloaded,spec);
            reloaded.stopAllEffects();applyBuffs(reloaded,spec.buffSet);
            double[] actual=stats(reloaded);
            for(int index=0;index<actual.length;index++)
                if(Math.abs(actual[index]-expectedStats[index])>0.00001)
                    throw new IllegalStateException("Stats diferentes tras recarga: "+spec.name+" index="+index);
            reloaded.setCurrentHpMp(reloaded.getMaxHp(),reloaded.getMaxMp());reloaded.setCurrentCp(reloaded.getMaxCp());
            if(!LabTelemetry.capturePilotStatsNow(reloaded)) throw new IllegalStateException("Fallo captura tras recarga "+spec.name);
            LOGGER.info("RosterHybridReload PASS "+spec.name+" skills="+reloaded.getAllSkills().size());
        }
        finally {reloaded.storeMe();reloaded.deleteMe();reloaded.setOnlineStatus(false,true);}
    }

    private static void prepareSubclasses(Player player,Profile spec)
    {
        if(player.getSubClasses().size()>3) throw new IllegalStateException("Demasiadas subs: "+spec.name);
        // Correct the historical SK recipe typo only on these reserved technical profiles.
        // 107 is Spectral Dancer; the requested Shillien Templar is 106.
        if(spec.npcId>=901109 && spec.npcId<=901111)
        {
            int slot=spec.npcId==901111?2:3;
            var old=player.getSubClasses().get(slot);
            if(old!=null && old.getId()==107 && spec.subs[slot-1]==106)
            {
                if(!player.modifySubClass(slot,106)) throw new IllegalStateException("No se pudo corregir SK: "+spec.name);
                try
                {
                    player.setActiveClass(slot);maximize(player);
                    for(int dye:new int[]{169,174})
                        if(!player.addHenna(HennaData.getInstance().getHenna(dye))) throw new IllegalStateException("Dye SK: "+spec.name);
                }
                finally {player.setActiveClass(0);player.storeMe();}
                LOGGER.info("Corrected SK recipe 107->106: "+spec.name+" slot="+slot);
            }
        }
        for(int slot=1;slot<=3;slot++)
        {
            var existing=player.getSubClasses().get(slot);
            if(existing!=null && existing.getId()!=spec.subs[slot-1])
                throw new IllegalStateException("Sub editada; no se sobrescribe: "+spec.name+" slot="+slot);
        }
        try
        {
            for(int slot=1;slot<=3;slot++)
            {
                if(player.getSubClasses().containsKey(slot)) continue;
                if(!player.addSubClass(spec.subs[slot-1],slot)) throw new IllegalStateException("No se pudo crear sub "+slot+" de "+spec.name);
                player.setActiveClass(slot);maximize(player);
                int[] dyes=player.getPlayerClass().isMage()?new int[]{175,180}:new int[]{169,174};
                for(int dye:dyes)
                {
                    var henna=HennaData.getInstance().getHenna(dye);
                    if(henna.isAllowedClass(player.getPlayerClass()) && !player.addHenna(henna))
                        throw new IllegalStateException("No se pudo aplicar dye "+dye+" a "+spec.name+" slot="+slot);
                }
                player.storeMe();
            }
        }
        finally {player.setActiveClass(0);player.storeMe();}
    }

    private static void verifySlots(Player player,Profile spec) throws Exception
    {
        var origin=player.getRacialBaseTemplate();
        try
        {
            for(int slot=0;slot<=3;slot++)
            {
                player.setActiveClass(slot);
                if(player.getPlayerClass().getId()!=(slot==0?spec.classId:spec.subs[slot-1])
                    || player.getLevel()!=ExperienceData.getInstance().getMaxLevel()-1
                    || player.getRace()!=spec.race || player.isRacialMage()!=spec.mage
                    || player.getRacialBaseTemplate()!=origin)
                    throw new IllegalStateException("Identidad/nivel/origen incorrectos: "+spec.name+" slot="+slot);
                RealHumanPilots.verifyActiveSkills(player);
            }
        }
        finally {player.setActiveClass(0);player.storeMe();}
    }

    private static int[] subclassRecipe(int npcId)
    {
        return switch(npcId)
        {
            case 901100 -> new int[]{91,116,114};
            case 901101 -> new int[]{90,101,115};
            case 901102 -> new int[]{91,98,114};
            case 901103 -> new int[]{90,96,115};
            case 901104 -> new int[]{107,95,116};
            case 901105 -> new int[]{107,111,97};
            case 901106 -> new int[]{90,114,116};
            case 901107 -> new int[]{99,96,94};
            case 901108 -> new int[]{107,114,116};
            case 901109,901110 -> new int[]{114,113,106};
            case 901111 -> new int[]{97,106,111};
            case 901112 -> new int[]{93,113,88};
            case 901113 -> new int[]{103,110,115};
            case 901114 -> new int[]{94,95,115};
            case 901115 -> new int[]{94,103,95};
            case 901116 -> new int[]{110,103,115};
            case 901117,901118 -> new int[]{94,103,115};
            case 901119 -> new int[]{114,113,116};
            case 901120 -> new int[]{97,100,116};
            case 901121 -> new int[]{111,114,116};
            case 901122 -> new int[]{97,106,98};
            case 901123 -> new int[]{97,105,115};
            case 901124 -> new int[]{113,100,116};
            case 901125 -> new int[]{105,100,116};
            case 901126 -> new int[]{97,99,116};
            case 901127 -> new int[]{97,106,98};
            case 901128 -> new int[]{97,115,99};
            case 901129 -> new int[]{111,97,116};
            case 901130 -> new int[]{114,113,116};
            case 901131 -> new int[]{114,113,116};
            case 901132 -> new int[]{97,106,115};
            case 901133 -> new int[]{97,115,99};
            case 901134 -> new int[]{113,106,116};
            case 901135 -> new int[]{97,100,115};
            case 901136 -> new int[]{114,113,116};
            case 901137 -> new int[]{114,113,116};
            case 901138 -> new int[]{97,100,116};
            default -> throw new IllegalArgumentException("Sin receta: "+npcId);
        };
    }

    private static void maximize(Player p)
    {
        int level=ExperienceData.getInstance().getMaxLevel()-1;p.getStat().setExp(ExperienceData.getInstance().getExpForLevel(level));p.getStat().setLevel((byte)level);p.rewardSkills();p.storeMe();
    }

    private static double[] stats(Player p)
    {
        return new double[]{p.getPAtk(null),p.getMAtk(null,null),p.getPDef(null),p.getMDef(null,null),p.getPAtkSpd(),p.getMAtkSpd(),p.getMaxHp(),p.getMaxMp(),p.getMaxCp(),p.getSTR(),p.getDEX(),p.getCON(),p.getINT(),p.getWIT(),p.getMEN()};
    }

    private static void equip(Player player,Profile p)
    {
        int[] armor=p.mage?new int[]{6383,6384,6385,6386,6377}:p.light?new int[]{6379,6380,6381,6382}:new int[]{6373,6374,6375,6376,6378};
        List<Integer> gear=new ArrayList<>();for(int id:armor)gear.add(id);for(int[] j:JEWELRY)for(int i=0;i<j[1];i++)gear.add(j[0]);gear.add(p.weapon);
        if(p.npcId>=901119 && !p.mage && (p.classId==90 || p.classId==91 || p.classId==99 || p.classId==100 || p.classId==106)) gear.add(6377);
        for(int id:gear){Item item=player.getInventory().addItem(ItemProcessType.NONE,id,1,player,null);if(item==null)throw new IllegalStateException("Objeto inexistente "+id+" para "+p.name);item.setEnchantLevel(4);player.getInventory().equipItem(item);item.updateDatabase(true);}
    }

    private static void applyBuffs(Player p,String role)
    {
        int[][] extras=role.equals("MAGE")?MAGE_BUFFS:PHYSICAL_BUFFS;
        for(int[][] group:new int[][][]{COMMON_BUFFS,extras})for(int[] entry:group){Skill skill=SkillData.getInstance().getSkill(entry[0],entry[1]);if(skill==null)throw new IllegalStateException("Buff inexistente "+entry[0]+":"+entry[1]);skill.applyEffects(p,p);}
    }

    private static void cacheNpcStats(Profile p,Player source)
    {
        double[] values={source.getSTR(),source.getDEX(),source.getCON(),source.getINT(),source.getWIT(),source.getMEN(),
            source.getMaxHp(),source.getMaxMp(),source.getMaxCp(),source.getPAtk(null),source.getMAtk(null,null),source.getPDef(null),source.getMDef(null,null),
            source.getPAtkSpd(),source.getMAtkSpd(),source.getRunSpeed(),source.getStat().getAccuracy(),source.getStat().getEvasionRate(null),
            source.getStat().getCriticalHit(null,null),source.getStat().getMCriticalHit(null,null)/10.0};
        synchronized(PREPARED) {PREPARED.put(p.npcId,new PreparedNpc(values,p.buffSet));}
    }

    /** Applies the verified Player sheet once to a newly spawned duel opponent. */
    public static void applyPreparedStats(Npc npc)
    {
        PreparedNpc profile;
        synchronized(PREPARED) {profile=PREPARED.get(npc.getId());}
        if(!READY || profile==null) throw new IllegalStateException("Perfil NPC aun no preparado: "+npc.getId());
        List<AbstractFunction> funcs=new ArrayList<>();
        for(int i=0;i<NPC_STATS.length;i++) funcs.add(new FuncSet(NPC_STATS[i],0x10000,npc,profile.values[i],null));
        npc.addStatFuncs(funcs);
        for(int[][] group:new int[][][]{COMMON_BUFFS,profile.buffSet.equals("MAGE")?MAGE_BUFFS:PHYSICAL_BUFFS})
            for(int[] entry:group) SkillData.getInstance().getSkill(entry[0],entry[1]).applyEffects(npc,npc);
        npc.fullRestore();
        if(!LabTelemetry.captureNpcStatsNow(npc)) throw new IllegalStateException("No se pudieron capturar stats NPC: "+npc.getId());
    }

    private record PreparedNpc(double[] values,String buffSet) {}

    public static boolean isReady() {return READY;}

    private static final class Profile
    {
        final int npcId,classId,weapon;final String name,account,role,buffSet;final Race race;final boolean mage,light,female;final int[] dyes,subs;
        Profile(int npcId,String name,String account,int classId,Race race,boolean mage,boolean light,int weapon,int[] dyes,String role)
        {this.npcId=npcId;this.name=name;this.account=account;this.classId=classId;this.race=race;this.mage=mage;this.light=light;this.weapon=weapon;this.dyes=dyes;this.subs=subclassRecipe(npcId);this.role=role;this.buffSet=role;this.female=name.endsWith("Selene")||name.endsWith("Lethiel")||name.endsWith("Myrentha")||name.endsWith("Brunna")||name.endsWith("Ignara")||name.endsWith("Aelira")||name.endsWith("Sylira")||name.endsWith("Velith")||name.endsWith("Seraphine")||name.endsWith("Elowen")||name.endsWith("Faelith")||name.endsWith("Nerys")||name.endsWith("Nysera")||name.endsWith("Saevra")||name.endsWith("Mazhura")||name.endsWith("Dagna");}
    }

    public static void main(String[] args){new NormalNpcRoster();}
}
