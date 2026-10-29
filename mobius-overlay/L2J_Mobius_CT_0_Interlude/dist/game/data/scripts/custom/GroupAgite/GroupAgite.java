package custom.GroupAgite;

import java.sql.*;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.clan.Clan;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.entity.item.enums.*;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType;
import org.l2jmobius.gameserver.network.serverpackets.*;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.RealHumanPilots.RealHumanPilots;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;

/** Opt-in real Player parties. Normal skills/items/targets, not scripted damage or forced aggro. */
public class GroupAgite extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(GroupAgite.class.getName());
    private static final Object LOCK=new Object();
    private static final String[] CLANS={"Hellsing","Holly","Sacred"};
    private static final String[][] NAMES={{"Hellkevin","Vaelkor","Noctis","Selene"},
        {"Kaelis","Gorvak","Myrentha","Ignara"},{"Caelan","Arden","Zhurak","Morvain"}};
    private static final String[][] ROLES={{"MAGE","DAGGER","SUPPORT","HEALER"},
        {"ARCHER","FRONT","HEALER","MAGE"},{"ARCHER","FRONT","SUPPORT","MAGE"}};
    private static final int[][] COMMON={{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
    private static final int[][] PHYS={{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1},
        {271,1},{272,1},{274,1},{275,1},{269,1},{266,1},{264,1},{267,1},{268,1},{304,1}};
    private static final int[][] MAGIC={{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},
        {273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1}};
    private final ConcurrentLinkedQueue<Row> queue=new ConcurrentLinkedQueue<>();
    private Match match;
    private boolean schema,smokeAttempted;
    private long dropped;

    private GroupAgite()
    {
        try(Connection c=DatabaseFactory.getConnection();Statement st=c.createStatement())
        {
            st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_group_runs(run_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,started_ms BIGINT NOT NULL,ended_ms BIGINT NOT NULL DEFAULT 0,controller_id INT NOT NULL,test_mode VARCHAR(12) NOT NULL,outcome VARCHAR(40) NOT NULL DEFAULT 'PREPARED') ENGINE=InnoDB");
            st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_group_events(event_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,run_id BIGINT UNSIGNED NOT NULL,round_no INT NOT NULL,observed_ms BIGINT NOT NULL,team_no INT NOT NULL,actor_id INT NOT NULL,target_id INT NOT NULL,event_name VARCHAR(32) NOT NULL,detail_text TEXT NOT NULL,KEY idx_group_run(run_id,observed_ms)) ENGINE=InnoDB");
            schema=true;
        }
        catch(Exception e) {LOG.log(Level.SEVERE,"GroupAgite disabled: telemetry schema",e);}
        VoicedCommandHandler.getInstance().registerHandler(this);
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,
            (OnCreatureDamageDealt e)->damage(e),this));
        ThreadPool.scheduleAtFixedRate(this::tick,1500,500);
        ThreadPool.scheduleAtFixedRate(this::flush,1000,1000);
        LOG.info("Agite 4vs4 v1.1: .agite preparar | iniciar | estado | cubrir | asalto | senuelo | seguir | cancelar");
    }
    @Override public String[] getCommandList() {return new String[]{"agite"};}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        if(!p.isGM() || !p.getName().equals("Hellkevin")) {p.sendMessage("Evento reservado a Hellkevin GM.");return true;}
        synchronized(LOCK)
        {
            String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
            try
            {
                switch(action)
                {
                    case "preparar" -> prepare(p,false);
                    case "iniciar" -> {
                        if(match==null) p.sendMessage("Usa .agite preparar primero.");
                        else if(match.phase.equals("READY")) beginRound();
                        else p.sendMessage("El evento ya comenzo.");
                    }
                    case "cancelar" -> {if(match!=null) finish("CANCELLED");}
                    case "estado" -> {if(match==null) p.sendMessage("Sin agite preparado.");else announce(status());}
                    case "cubrir","asalto","senuelo","seguir" -> {
                        if(match==null) p.sendMessage("Prepara el agite primero.");
                        else {
                            match.teams[0].order=action;
                            for(Member a:match.teams[0].members) if(a.bot) {
                                a.p.abortAttack();a.p.getAI().setIntentionIdle();
                                if(a.p.hasSummon()) {a.p.getSummon().abortAttack();a.p.getSummon().setFollowStatus(true);}
                            }
                            announce("Orden Hellsing: "+action);audit(0,p,null,"ORDER",action);
                        }
                    }
                    default -> p.sendMessage(".agite preparar | iniciar | estado | cubrir | asalto | senuelo | seguir | cancelar");
                }
            }
            catch(Exception e) {LOG.log(Level.SEVERE,"Agite command failed",e);if(match!=null) finish("ERROR");p.sendMessage("No se completo: "+e.getMessage());}
        }
        return true;
    }
    private void prepare(Player operator,boolean smoke) throws Exception
    {
        if(match!=null) throw new IllegalStateException("Ya hay un evento preparado");
        if(!schema || !NormalNpcRoster.isReady()) throw new IllegalStateException("Espera el roster completo");
        if(operator.isInParty() || operator.isInCombat() || operator.isDead()) throw new IllegalStateException("Sal de party/combate antes de preparar");
        if(!smoke && (operator.getInstanceId()!=0 || operator.calculateDistance2D(148900,46100,operator.getZ())>2500 || !operator.isInsideZone(ZoneId.PVP)))
            throw new IllegalStateException("Entra al suelo PvP del Coliseo");
        if(!smoke && operator.isInvul()) throw new IllegalStateException("Desactiva invulnerabilidad GM");
        if(!SoloArenaGauntlet.tryClaimPilot()) throw new IllegalStateException("Coliseo ocupado por .arena o .ia");
        Match m=new Match(operator,smoke);match=m;
        try
        {
            m.fightInstance=InstanceManager.getInstance().createDynamicInstance(0).getId();
            m.waitInstance=InstanceManager.getInstance().createDynamicInstance(0).getId();
            for(int t=0;t<3;t++)
            {
                Team team=new Team(t);m.teams[t]=team;
                for(int i=0;i<4;i++)
                {
                    Player p=t==0 && i==0?operator:load(NAMES[t][i]);
                    Member a=new Member(p,t,i,ROLES[t][i],smoke || p!=operator);team.members.add(a);
                    if(a.bot) {p.setLabControlled(true);p.setOnlineStatus(true,true);p.setDead(false);p.setEnteredWorld();}
                }
            }
            // Preflight every membership BEFORE creating any persistent clan.
            if(!smoke)
            {
                for(Team t:m.teams)
                {
                    Clan clan=ClanTable.getInstance().getClanByName(CLANS[t.id]);
                    if(clan!=null && clan.getLeaderId()!=t.members.get(0).p.getObjectId()) throw new IllegalStateException("Clan existente con otro lider: "+CLANS[t.id]);
                    for(Member a:t.members) if(a.p.getClanId()!=0 && (clan==null || a.p.getClanId()!=clan.getId()))
                        throw new IllegalStateException("Otro clan en "+a.p.getName()+": no se reemplaza");
                }
                for(Team t:m.teams)
                {
                    Clan clan=ClanTable.getInstance().getClanByName(CLANS[t.id]);
                    if(clan==null) clan=ClanTable.getInstance().createClan(t.members.get(0).p,CLANS[t.id]);
                    if(clan==null) throw new IllegalStateException("No se pudo crear "+CLANS[t.id]);
                    for(Member a:t.members)
                    {
                        if(clan.getClanMember(a.p.getObjectId())==null) clan.addClanMember(a.p);
                        else {a.p.setClan(clan);clan.getClanMember(a.p.getObjectId()).setPlayer(a.p);}
                        a.p.storeMe();
                    }
                }
            }
            for(Team t:m.teams)
            {
                Player leader=t.members.get(0).p;Party party=new Party(leader,PartyDistributionType.FINDERS_KEEPERS);leader.setParty(party);
                for(int i=1;i<4;i++) t.members.get(i).p.joinParty(party);
            }
            try(Connection c=DatabaseFactory.getConnection();PreparedStatement ps=c.prepareStatement(
                "INSERT INTO lab_group_runs(started_ms,controller_id,test_mode) VALUES(?,?,?)",Statement.RETURN_GENERATED_KEYS))
            {ps.setLong(1,m.started);ps.setInt(2,operator.getObjectId());ps.setString(3,smoke?"SMOKE":"MANUAL");ps.executeUpdate();try(ResultSet r=ps.getGeneratedKeys()){r.next();m.run=r.getLong(1);}}
            for(Team t:m.teams) for(Member a:t.members) reset(a,true);
            announce("Clanes/parties preparados: Hellsing, Holly y Sacred. .agite iniciar. Primero en sumar 3 victorias.");
            audit(-1,operator,null,"PREPARED",String.join(";",Arrays.stream(NAMES).map(n->String.join(",",n)).toList()));
        }
        catch(Exception e) {finish("SETUP_ERROR");throw e;}
    }
    private Player load(String name) throws Exception
    {
        int id;
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement ps=c.prepareStatement(
            "SELECT c.charId,c.online,c.account_name,p.recipe_version FROM characters c JOIN lab_normal_npc_profiles p ON c.charId=p.char_id WHERE c.char_name=?"))
        {
            ps.setString(1,"Arena"+name);try(ResultSet r=ps.executeQuery())
            {
                if(!r.next() || r.getInt("online")!=0 || !Set.of("telemetryarena1","telemetryarena2","telemetryarena3").contains(r.getString("account_name")) || !r.getString("recipe_version").equals("normal-pvp-s4-hybrid-v2"))
                    throw new IllegalStateException("Perfil ocupado/no reservado: "+name);
                id=r.getInt("charId");
            }
        }
        if(World.getPlayer(id)!=null) throw new IllegalStateException("Perfil en uso: "+name);
        Player p=Player.load(id);
        if(p==null || p.getClient()!=null || p.getClassIndex()!=0 || p.getSubClasses().size()!=3 || p.getLevel()!=80)
        {if(p!=null) p.deleteMe();throw new IllegalStateException("Perfil modificado: "+name);}
        RealHumanPilots.verifyActiveSkills(p);return p;
    }
    private void reset(Member a,boolean waiting)
    {
        Player p=a.p;p.abortCast();p.abortAttack();p.getAI().setIntentionIdle();p.setTarget(null);
        if(a.bot && p.hasSummon()) p.getSummon().unSummon(p);
        if(p.isDead()) p.doRevive();p.stopAllEffects();p.resetDisabledSkills();p.resetTimeStamps();p.enableAllSkills();
        for(int[][] group:new int[][][]{COMMON,a.magical()?MAGIC:PHYS})
            for(int[] b:group) SkillData.getInstance().getSkill(b[0],b[1]).applyEffects(p,p);
        p.setCurrentHpMp(p.getMaxHp(),p.getMaxMp());p.setCurrentCp(p.getMaxCp());p.setInvul(true);p.setRunning();
        if(p.hasSummon()) {p.getSummon().setCurrentHpMp(p.getSummon().getMaxHp(),p.getSummon().getMaxMp());p.getSummon().setFollowStatus(true);}
        a.reuse.clear();a.lastHeal=0;a.summons=0;a.pendingSummon=0;a.potions.clear();
        if(a.bot)
        {
            for(int[] item:new int[][]{{5592,50},{728,30},{1539,10},{1467,2000},{3952,2000},{1345,2000}}) stock(p,item[0],item[1]);
            a.potions.put(5592,50);a.potions.put(728,30);a.potions.put(1539,10);
            for(Skill s:p.getAllSkills()) if(!s.isPassive() && s.getItemConsumeId()>0) stock(p,s.getItemConsumeId(),Math.min(2000,Math.max(100,s.getItemConsumeCount()*5)));
        }
        if(waiting) placeWaiting(a);
    }
    private void teleport(Player p,int x,int y,int z,int instance)
    {
        if(p.getWorldRegion()==null) {p.setInstanceId(instance);p.spawnMe(x,y,z);p.revalidateZone(true);}
        else {p.teleToLocation(x,y,z,0,instance,false);if(p.getClient()==null) p.onTeleported();}
    }
    private void placeWaiting(Member a)
    {
        GeoEngine g=GeoEngine.getInstance();
        int x=148750,y=44850+a.slot*20;
        // Pick a walkable floor near the entrance, not the roof/stands of the north wall.
        boolean found=false;
        for(int dx=-96;dx<=96 && !found;dx+=16) for(int dy=-64;dy<=64 && !found;dy+=16)
        {
            int z=g.getHeight(x+dx,y+dy,-3408);
            if(Math.abs(z+3408)<100 && g.canMoveToTarget(x+dx,y+dy,z,x+dx,y+dy+16,z,match.waitInstance))
            {teleport(a.p,x+dx,y+dy,z,match.waitInstance);found=true;}
        }
        if(!found) throw new IllegalStateException("No hay suelo seguro tras la entrada");
    }
    private void beginRound()
    {
        Match m=match;m.phase="PREPARING";m.phaseStarted=System.currentTimeMillis();m.lastSnapshot=0;
        for(Team t:m.teams)
        {
            boolean active=t.id!=m.ladder.waiting;
            for(Member a:t.members)
            {
                reset(a,!active);
                if(active)
                {
                    int side=t.id==m.ladder.holder?-1:1;
                    int x=148900+side*(a.slot==1?250:450),y=46600+(a.slot-1)*150;
                    int z=GeoEngine.getInstance().getHeight(x,y,-3400);
                    if(Math.abs(z+3408)>100 || !GeoEngine.getInstance().canMoveToTarget(x,y,z,148900,46600,-3408,m.fightInstance))
                        throw new IllegalStateException("Formacion sobre suelo no transitable");
                    teleport(a.p,x,y,z,m.fightInstance);
                }
            }
        }
        announce("Ronda "+m.ladder.round+": "+CLANS[m.ladder.holder]+" vs "+CLANS[m.ladder.challenger]+". Preparacion: 20 segundos. "+CLANS[m.ladder.waiting]+" espera tras la entrada.");
        audit(-1,m.operator,null,"ROUND_PREPARE",status());
    }
    private void tick()
    {
        synchronized(LOCK)
        {
            try
            {
                if(match==null)
                {
                    if(schema && Boolean.getBoolean("lab.agite.smoke") && !smokeAttempted && NormalNpcRoster.isReady())
                    {
                        smokeAttempted=true;Player stub=load("Aelira");prepare(stub,true);beginRound();
                    }
                    return;
                }
                Match m=match;long now=System.currentTimeMillis();
                if(!m.smoke && (!m.operator.isOnline() || m.operator.getClient()==null)) {finish("DISCONNECTED");return;}
                if(now-m.started>3600000 || (m.phase.equals("READY") && now-m.started>300000)) {finish("TIME_LIMIT");return;}
                for(Team t:m.teams) for(Member a:t.members)
                {
                    if(!a.bot && !m.phase.equals("INTERMISSION") && a.p.getInstanceId()!=(t.id==m.ladder.waiting || m.phase.equals("READY")?m.waitInstance:m.fightInstance))
                    {finish("LEFT_INSTANCE");return;}
                    if(a.bot && a.p.isDead() && a.p.isReviveRequested())
                    {a.p.reviveAnswer(1);audit(a.team,a.p,null,"REVIVE_CONFIRM",a.p.isDead()?"PENDING":"REVIVED");}
                }
                if(m.phase.equals("READY")) return;
                if(m.phase.equals("INTERMISSION")) {if(now-m.phaseStarted>=10000) beginRound();return;}
                if(m.phase.equals("PREPARING"))
                {
                    for(Team t:m.teams) if(t.id!=m.ladder.waiting) for(Member a:t.members) if(a.bot && !a.p.isCastingNow()) prepareSkills(a);
                    if(now-m.phaseStarted>=20000)
                    {
                        for(Team t:m.teams) if(t.id!=m.ladder.waiting) for(Member a:t.members) {a.p.setInvul(false);a.p.revalidateZone(true);}
                        m.phase="FIGHT";m.phaseStarted=now;announce("Combate! "+status());audit(-1,m.operator,null,"ROUND_START",status());
                    }
                    return;
                }
                int left=living(m.teams[m.ladder.holder]),right=living(m.teams[m.ladder.challenger]);
                if(left==0 || right==0)
                {
                    if(left==0 && right==0) conclude(-1,"DOUBLE_KO");else conclude(left==0?m.ladder.challenger:m.ladder.holder,"ELIMINATION");return;
                }
                if(now-m.phaseStarted>360000) {conclude(-1,"ROUND_TIMEOUT");return;}
                for(Team t:m.teams) if(t.id!=m.ladder.waiting) for(Member a:t.members) if(a.bot && !a.p.isDead()) act(a);
                if(now-m.lastSnapshot>=2000)
                {
                    m.lastSnapshot=now;
                    for(Team t:m.teams) for(Member a:t.members) snapshot(a);
                    hud();
                }
                if(m.smoke && now-m.started>70000)
                {
                    boolean pass=m.hits>0 && m.accepted>10 && m.summonSeen && Arrays.stream(m.teams).allMatch(t->t.members.size()==4 && t.members.get(0).p.getParty()!=null && t.members.get(0).p.getParty().getMemberCount()==4);
                    LOG.info("GROUP_SMOKE "+(pass?"PASS":"FAIL")+" hits="+m.hits+" casts="+m.accepted+" summon="+m.summonSeen);
                    finish(pass?"SMOKE_PASS":"SMOKE_FAIL");
                }
            }
            catch(Exception e) {LOG.log(Level.SEVERE,"GroupAgite stopped safely",e);if(match!=null) finish("ERROR");}
        }
    }
    private int living(Team t) {return (int)t.members.stream().filter(a->!a.p.isDead()).count();}
    private Player captain(Team t)
    {
        for(int i:t.id==0?new int[]{0,2,1,3}:new int[]{0,1,2,3}) if(!t.members.get(i).p.isDead()) return t.members.get(i).p;
        return t.members.get(0).p;
    }
    private void prepareSkills(Member a)
    {
        Player p=a.p;long now=System.currentTimeMillis();
        if(p.hasSummon() && p.getSummon().isDead()) p.getSummon().unSummon(p);
        if(!p.hasSummon() && p.isAffectedBySkill(1262)) p.stopSkillEffects(SkillFinishType.REMOVED,1262);
        if(p.hasSummon() && !p.getSummon().isDead()) {match.summonSeen=true;if(cast(a,1262,p,"TRANSFER_PAIN",false)) return;}
        if(!p.hasSummon() && now>=a.pendingSummon && GroupPolicy.canSummon(a.summons,hp(p),match.phase.equals("PREPARING")))
            for(int id:new int[]{1333,1129,1128,1225,1226,1227,1228})
            {
                Skill s=p.getKnownSkill(id);
                if(s!=null && s.getName().toLowerCase(Locale.ROOT).contains("summon") && !s.getName().contains("Cubic") && cast(a,id,p,"SUMMON",false))
                {a.summons++;a.pendingSummon=now+20000;return;}
            }
        for(int id:new int[]{33,22,278,1281})
        {
            int cubic=switch(id){case 33->5;case 22->2;case 278->3;default->1;};
            if(p.getCubicById(cubic)==null && cast(a,id,p,"CUBIC",false)) return;
        }
    }
    private void act(Member a)
    {
        Player p=a.p;Team team=match.teams[a.team];long now=System.currentTimeMillis();
        potions(a);
        if(p.isCastingNow() || p.isOutOfControl() || p.isControlBlocked()) return;
        Player leader=captain(team);Team enemies=match.teams[a.team==match.ladder.holder?match.ladder.challenger:match.ladder.holder];
        Player target=choose(a,enemies,leader);
        if(target==null) return;
        if(team.order.equals("seguir")) {formation(a,leader);return;}
        if(hp(p)<.30 && threatened(p) && cast(a,110,p,"EMERGENCY_UD",false)) return;
        if(p.isAffectedBySkill(337) && (hp(p)<.6 || mp(p)<.35)) p.stopSkillEffects(SkillFinishType.REMOVED,337);
        if(p.isAffectedBySkill(1283) && mp(p)<.25) p.stopSkillEffects(SkillFinishType.REMOVED,1283);
        if(!team.order.equals("asalto"))
        {
            List<Member> dead=team.members.stream().filter(b->b.p.isDead()).toList();
            if(!dead.isEmpty())
            {
                Player body=dead.get(0).p;
                if(GroupPolicy.massRevive(dead.size(),hp(p),threatened(p)) && cast(a,1254,body,"MASS_RESURRECTION",true)) return;
                if(!threatened(p) && castOrApproach(a,1016,body,"RESURRECTION")) return;
            }
            Member patient=team.members.stream().filter(b->!b.p.isDead()).max(Comparator.comparingDouble(b->GroupPolicy.concern(hp(b.p),pressure(b.p),b.p==leader,b.role.equals("HEALER")))).orElse(a);
            if(GroupPolicy.heal(hp(patient.p),pressure(patient.p)) && now-a.lastHeal>=1200)
            {
                // Exit offensive toggles before spending MP on critical support.
                for(int id:new int[]{337,1283}) if(p.isAffectedBySkill(id)) p.stopSkillEffects(SkillFinishType.REMOVED,id);
                for(int id:new int[]{1401,1218,1217}) if(castOrApproach(a,id,patient.p,"HEAL_ALLY")) {a.lastHeal=now;return;}
                if(cast(a,1256,patient.p,"CLAN_HP",false)) return;
            }
            if(team.members.stream().anyMatch(b->!b.p.isDead() && cp(b.p)<.55) && cast(a,1305,p,"CLAN_CP",true)) return;
            if(p.hasSummon() && !p.getSummon().isDead() && hp(p.getSummon())<.45 && cast(a,1127,p.getSummon(),"HEAL_SUMMON",true)) return;
        }
        prepareSkills(a);if(p.isCastingNow()) return;
        if(p.hasSummon() && !p.getSummon().isDead())
        {Summon pet=p.getSummon();pet.setRunning();pet.setFollowStatus(false);pet.setTarget(target);pet.getAI().setIntentionAttack(target);match.summonSeen=true;}
        Creature victim=target;
        int near=(int)enemies.members.stream().filter(b->!b.p.isDead() && b.p.calculateDistance2D(leader)<300).count();
        if(target.hasSummon() && !target.getSummon().isDead() && GroupPolicy.focusPet(hp(target.getSummon()),target.isAffectedBySkill(1262),near,hp(leader))) victim=target.getSummon();
        if(team.order.equals("senuelo") && (a.role.equals("FRONT") || a.role.equals("SUPPORT")))
        {
            if(hp(p)<.45 && p!=leader) {formation(a,leader);return;}
            for(int id:new int[]{28,18}) if(cast(a,id,target,"LURE_AGGRESSION",false)) return;
        }
        Player endangered=team.members.stream().filter(b->!b.p.isDead() && hp(b.p)<.25 && threatened(b.p))
            .max(Comparator.comparingDouble(b->GroupPolicy.concern(hp(b.p),pressure(b.p),b.p==leader,b.role.equals("HEALER"))))
            .map(b->b.p).orElse(null);
        if(endangered!=null && endangered!=p && !team.order.equals("asalto"))
        {
            for(int id:new int[]{358,1208,402,1246}) if(cast(a,id,target,"COVER_ALLY",false)) return;
        }
        if(a.role.equals("DAGGER"))
        {for(int id:new int[]{445,358,344,263,11,12}) if(cast(a,id,id==445?p:victim,"DAGGER_PRESSURE",false)) return;}
        if(a.role.equals("FRONT"))
        {for(int id:new int[]{121,282,261,347,48}) if(cast(a,id,(id==121||id==282)?p:victim,"FRONT_PRESSURE",false)) return;}
        if(a.magical())
        {
            if(victim.isCastingNow() && cast(a,1246,victim,"SILENCE",false)) return;
            for(int id:new int[]{1208,402,122,1056}) if(cast(a,id,victim,"CONTROL",false)) return;
            int[] attacks=p.getKnownSkill(1245)!=null && a.role.equals("SUPPORT")?new int[]{1245,1234,1239,1230,1235,1148}:new int[]{1239,1230,1235,1148,1234,1245};
            for(int id:attacks) if(cast(a,id,victim,"DAMAGE",true)) return;
            if(a.role.equals("HEALER") && p!=leader && p.calculateDistance2D(leader)>250) {formation(a,leader);return;}
            if(p.calculateDistance2D(victim)>500) approach(a,victim,430);
            else if(p.calculateDistance2D(victim)<180 && p!=leader) formation(a,leader);
        }
        else
        {
            if(!team.order.equals("asalto") && p!=leader && p.calculateDistance2D(leader)>900) {formation(a,leader);return;}
            shot(a,false);p.setTarget(victim);p.getAI().setIntentionAttack(victim);
        }
    }
    private Player choose(Member a,Team enemies,Player leader)
    {
        Player chosen=null;double best=-Double.MAX_VALUE;
        for(Member b:enemies.members)
        {
            Player p=b.p;if(p.isDead() || p.getInstanceId()!=a.p.getInstanceId()) continue;
            double score=1000/(1+a.p.calculateDistance2D(p)/100)+pressureFrom(p,leader)*3+(p.calculateDistance2D(leader)<300?90:0)+(p.isCastingNow()?30:0)+(1-hp(p))*35;
            if(leader.getTarget()==p) score+=120;
            if(score>best) {chosen=p;best=score;}
        }
        return chosen;
    }
    private void formation(Member a,Player leader)
    {
        if(a.p==leader) return;
        int x=leader.getX()+(a.slot==1?150:-180),y=leader.getY()+(a.slot-2)*160;
        if(a.p.calculateDistance2D(x,y,a.p.getZ())>100 && System.currentTimeMillis()-a.lastMove>1000)
        {a.p.getAI().setIntentionMoveTo(new Location(x,y,leader.getZ()));a.lastMove=System.currentTimeMillis();audit(a.team,a.p,leader,"FORMATION",match.teams[a.team].order);}
    }
    private void approach(Member a,Creature target,int range)
    {
        if(System.currentTimeMillis()-a.lastMove<1000) return;
        double angle=Math.atan2(a.p.getY()-target.getY(),a.p.getX()-target.getX());
        int x=target.getX()+(int)(Math.cos(angle)*Math.max(40,range-50)),y=target.getY()+(int)(Math.sin(angle)*Math.max(40,range-50));
        a.p.getAI().setIntentionMoveTo(new Location(x,y,target.getZ()));a.lastMove=System.currentTimeMillis();
    }
    private boolean castOrApproach(Member a,int id,Creature target,String why)
    {
        Skill s=a.p.getKnownSkill(id);if(s==null || a.p.isSkillDisabled(s) || a.p.getCurrentMp()<s.getMpConsume()+s.getMpInitialConsume()) return false;
        if(a.p.calculateDistance2D(target)>Math.max(40,s.getCastRange())+30 || !GeoEngine.getInstance().canSeeTarget(a.p,target))
        {approach(a,target,Math.max(40,s.getCastRange()));return true;}
        return cast(a,id,target,why,true);
    }
    private boolean cast(Member a,int id,Creature target,String why,boolean repeat)
    {
        Player p=a.p;Skill s=p.getKnownSkill(id);long now=System.currentTimeMillis();
        if(s==null || s.isPassive() || p.isCastingNow() || now<a.reuse.getOrDefault(id,0L)) return false;
        a.reuse.put(id,now+1200);
        if(p.isSkillDisabled(s) || p.getCurrentMp()<s.getMpConsume()+s.getMpInitialConsume() || p.getCurrentHp()<=s.getHpConsume()) return false;
        if(!repeat && target.isAffectedBySkill(id)) return false;
        if(target!=p && (target.getInstanceId()!=p.getInstanceId() || p.calculateDistance2D(target)>Math.max(40,s.getCastRange()<0?s.getAffectRange():s.getCastRange())+35 || !GeoEngine.getInstance().canSeeTarget(p,target))) return false;
        if(s.getItemConsumeId()>0 && p.getInventory().getInventoryItemCount(s.getItemConsumeId(),-1)<s.getItemConsumeCount()) return false;
        p.setTarget(target);if(!s.checkCondition(p,target,false)) return false;
        shot(a,s.isMagic());boolean accepted=p.useMagic(s,true,true);
        if(accepted) match.accepted++;
        audit(a.team,p,target,why,id+":"+s.getLevel()+":"+(accepted?"REQUEST_ACCEPTED":"REQUEST_REJECTED"));return accepted;
    }
    private void potions(Member a)
    {
        if(cp(a.p)<.7) item(a,5592,true);
        if(hp(a.p)<.65 && !a.p.isAffectedBySkill(2037)) item(a,1539,true);
        if(mp(a.p)<.5) item(a,728,true);
    }
    private void shot(Member a,boolean magic)
    {if(!a.p.isChargedShot(magic?ShotType.BLESSED_SPIRITSHOTS:ShotType.SOULSHOTS)) item(a,magic?3952:1467,false);}
    private boolean item(Member a,int id,boolean potion)
    {
        Player p=a.p;Item it=p.getInventory().getItemByItemId(id);
        if(it==null || it.getCount()==0 || p.isOutOfControl() || p.isControlBlocked() || (potion && a.potions.getOrDefault(id,0)<=0)) return false;
        if(p.getItemRemainingReuseTime(it.getObjectId())>0 || (it.getReuseDelay()>0 && p.getReuseDelayOnGroup(it.getSharedReuseGroup())>0) || !it.getTemplate().checkCondition(p,p,false)) return false;
        IItemHandler h=ItemHandler.getInstance().getHandler(it.getEtcItem());if(h==null) return false;
        if(potion) p.setTarget(p);long before=it.getCount();boolean accepted=h.onItemUse(p,it,false);
        if(accepted && it.getReuseDelay()>0) p.addTimeStampItem(it,it.getReuseDelay());
        if(accepted && potion) {a.potions.merge(id,-1,Integer::sum);audit(a.team,p,p,"POTION",id+":"+(it.getCount()<before?"CONSUMED":"ACCEPTED"));}
        return accepted;
    }
    private static void stock(Player p,int id,int count)
    {long have=p.getInventory().getInventoryItemCount(id,-1);if(have<count && p.getInventory().addItem(ItemProcessType.NONE,id,(int)(count-have),p,null)==null) throw new IllegalStateException("Reagent stock failed: "+id);}
    private static double hp(Creature p) {return p.getCurrentHp()/Math.max(1,p.getMaxHp());}
    private static double mp(Creature p) {return p.getCurrentMp()/Math.max(1,p.getMaxMp());}
    private static double cp(Player p) {return p.getCurrentCp()/Math.max(1,p.getMaxCp());}
    private boolean threatened(Player p) {return pressure(p)>20;}
    private double pressure(Player p)
    {return match.threats.stream().filter(h->h.target==p.getObjectId() && System.currentTimeMillis()-h.time<4000).mapToDouble(h->h.damage/p.getMaxHp()*100).sum();}
    private double pressureFrom(Player attacker,Player victim)
    {return match.threats.stream().filter(h->h.attacker==attacker.getObjectId() && h.target==victim.getObjectId() && System.currentTimeMillis()-h.time<4000).mapToDouble(h->h.damage/victim.getMaxHp()*100).sum();}
    private Member member(Creature p)
    {if(p==null) return null;Player owner=p.isSummon()?p.asSummon().getOwner():p.asPlayer();if(owner==null) return null;for(Team t:match.teams) if(t!=null) for(Member a:t.members) if(a.p==owner) return a;return null;}
    private void damage(OnCreatureDamageDealt e)
    {
        synchronized(LOCK)
        {
            if(match==null || !match.phase.equals("FIGHT") || e.getDamage()<=0) return;
            Member actor=member(e.getAttacker()),target=member(e.getTarget());
            if(actor==null || target==null || actor.team==target.team || actor.team==match.ladder.waiting || target.team==match.ladder.waiting) return;
            match.hits++;match.threats.addLast(new Hit(actor.p.getObjectId(),target.p.getObjectId(),System.currentTimeMillis(),e.getDamage()));
            while(match.threats.size()>200) match.threats.removeFirst();
            audit(actor.team,e.getAttacker(),e.getTarget(),"DAMAGE",e.getDamage()+":skill="+(e.getSkill()==null?0:e.getSkill().getId())+":critical="+e.isCritical());
            if(!match.smoke && e.getTarget()==match.operator)
            {
                boolean magic=e.getSkill()!=null && e.getSkill().isMagic();
                int id=magic?(e.isCritical()?2207:2206):(e.isCritical()?2205:2204);
                match.operator.sendPacket(new AgiteDamageMessage(id,e.getAttacker().getName(),(int)Math.round(e.getDamage())));
            }
        }
    }
    private void snapshot(Member a)
    {
        Player p=a.p;audit(a.team,p,p.getTarget()==null?null:p.getTarget().asCreature(),"STATE",
            "hp="+p.getCurrentHp()+"/"+p.getMaxHp()+";cp="+p.getCurrentCp()+"/"+p.getMaxCp()+";mp="+p.getCurrentMp()+"/"+p.getMaxMp()+";xyz="+p.getX()+","+p.getY()+","+p.getZ()+";dead="+p.isDead()+";casting="+p.isCastingNow()+";silenced="+p.isMuted()+";rooted="+p.isRooted()+";stunned="+p.isStunned()+";effects="+p.getEffectList().getEffects().stream().map(i->i.getSkill().getId()+":"+i.getSkill().getLevel()).toList());
        if(p.hasSummon()) {Summon s=p.getSummon();audit(a.team,s,p,"SUMMON_STATE","hp="+s.getCurrentHp()+";xyz="+s.getX()+","+s.getY()+","+s.getZ()+";dead="+s.isDead());}
    }
    private void hud()
    {
        if(match.smoke) return;Player p=match.operator;
        if(p.getTarget()!=null && p.getTarget().isPlayer() && member(p.getTarget().asCreature())!=null)
        {p.sendPacket(new ExOlympiadMode(2));p.sendPacket(new ExOlympiadUserInfo(p.getTarget().asPlayer(),1));p.sendPacket(new ExOlympiadUserInfo(p,0));match.hud=true;}
        else if(match.hud) {p.sendPacket(new ExOlympiadMode(0));match.hud=false;}
    }
    private void conclude(int winner,String reason)
    {
        Match m=match;
        for(Team t:m.teams) for(Member a:t.members)
        {
            a.p.abortCast();a.p.abortAttack();a.p.getAI().setIntentionIdle();a.p.setInvul(true);a.p.stopAllEffects();
            if(a.p.hasSummon())
            {
                a.p.getSummon().abortCast();a.p.getSummon().abortAttack();
                if(a.bot) a.p.getSummon().unSummon(a.p);
                else {a.p.getSummon().stopAllEffects();a.p.getSummon().setFollowStatus(true);}
            }
        }
        audit(winner,m.operator,null,"ROUND_END",reason+":"+status());
        if(winner>=0) {m.ladder.win(winner);announce("Victoria de "+CLANS[winner]+"! "+status());}
        else {
            announce("Ronda empatada: "+reason+". No suma puntos.");
            if(++m.draws>2) {finish("STALEMATE");return;}
        }
        if(m.ladder.champion>=0) {finish("WINNER_"+CLANS[m.ladder.champion]);return;}
        m.phase="INTERMISSION";m.phaseStarted=System.currentTimeMillis();announce("10 segundos hasta la preparacion de la siguiente ronda.");
    }
    private String status()
    {Match m=match;return "Hellsing "+m.ladder.points[0]+" | Holly "+m.ladder.points[1]+" | Sacred "+m.ladder.points[2]+" / "+m.phase+" / run "+m.run;}
    private void announce(String message)
    {if(match!=null && !match.smoke && match.operator.isOnline()) match.operator.sendMessage(message);LOG.info("GROUP_AGITE "+message);}
    private void finish(String outcome)
    {
        Match m=match;if(m==null) return;
        announce("Evento terminado: "+outcome+". "+status());audit(-1,m.operator,null,"EVENT_END",outcome+":dropped="+dropped);
        try
        {
            for(Team t:m.teams) if(t!=null) for(Member a:t.members)
            {
                Player p=a.p;
                try
                {
                    p.abortCast();p.abortAttack();p.getAI().setIntentionIdle();p.leaveParty();p.setInvul(false);
                    if(a.bot)
                    {
                        if(p.hasSummon()) p.getSummon().unSummon(p);
                        if(p.isDead()) p.doRevive();p.stopAllEffects();p.resetDisabledSkills();p.resetTimeStamps();
                        for(int[][] g:new int[][][]{COMMON,a.magical()?MAGIC:PHYS}) for(int[] b:g) SkillData.getInstance().getSkill(b[0],b[1]).applyEffects(p,p);
                        p.setCurrentHpMp(p.getMaxHp(),p.getMaxMp());p.setCurrentCp(p.getMaxCp());
                        p.decayMe();p.setInstanceId(a.origin.getInstanceId());p.setXYZInvisible(a.origin.getX(),a.origin.getY(),a.origin.getZ());p.storeMe();
                    }
                    else if(p.isOnline())
                    {
                        if(p.isDead()) p.doRevive();p.setTarget(null);p.sendPacket(new ExOlympiadMode(0));
                        teleport(p,a.origin.getX(),a.origin.getY(),a.origin.getZ(),a.origin.getInstanceId());
                    }
                }
                catch(Exception e) {LOG.log(Level.SEVERE,"Group cleanup "+p.getName(),e);}
                finally
                {
                    if(a.bot) {p.deleteMe();p.setLabControlled(false);p.setOnlineStatus(false,true);if(p.getClan()!=null && p.getClan().getClanMember(p.getObjectId())!=null) p.getClan().getClanMember(p.getObjectId()).setPlayer(null);}
                }
            }
            if(m.run>0) try(Connection c=DatabaseFactory.getConnection();PreparedStatement ps=c.prepareStatement("UPDATE lab_group_runs SET ended_ms=?,outcome=? WHERE run_id=?"))
            {ps.setLong(1,System.currentTimeMillis());ps.setString(2,outcome);ps.setLong(3,m.run);ps.executeUpdate();}
        }
        catch(Exception e) {LOG.log(Level.SEVERE,"Group cleanup failed",e);}
        finally
        {match=null;SoloArenaGauntlet.releasePilot();if(m.fightInstance>0) InstanceManager.getInstance().destroyInstance(m.fightInstance);if(m.waitInstance>0) InstanceManager.getInstance().destroyInstance(m.waitInstance);}
    }
    private void audit(int team,Creature actor,Creature target,String event,String detail)
    {
        if(match==null || match.run==0) return;
        if(queue.size()>=4096) {dropped++;return;}
        queue.offer(new Row(match.run,match.ladder.round,System.currentTimeMillis(),team,actor==null?0:actor.getObjectId(),target==null?0:target.getObjectId(),event,detail));
    }
    private void flush()
    {
        List<Row> batch=new ArrayList<>();for(int i=0;i<512;i++){Row r=queue.poll();if(r==null) break;batch.add(r);}if(batch.isEmpty()) return;
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement ps=c.prepareStatement("INSERT INTO lab_group_events(run_id,round_no,observed_ms,team_no,actor_id,target_id,event_name,detail_text) VALUES(?,?,?,?,?,?,?,?)"))
        {for(Row r:batch){ps.setLong(1,r.run);ps.setInt(2,r.round);ps.setLong(3,r.time);ps.setInt(4,r.team);ps.setInt(5,r.actor);ps.setInt(6,r.target);ps.setString(7,r.event);ps.setString(8,r.detail);ps.addBatch();}ps.executeBatch();}
        catch(Exception e) {dropped+=batch.size();LOG.log(Level.SEVERE,"Group telemetry lost "+batch.size()+" rows",e);}
    }
    private record Row(long run,int round,long time,int team,int actor,int target,String event,String detail) {}
    private record Hit(int attacker,int target,long time,double damage) {}
    private static final class Member
    {
        final Player p;final int team,slot;final String role;final boolean bot;final Location origin;
        final Map<Integer,Long> reuse=new HashMap<>();final Map<Integer,Integer> potions=new HashMap<>();long lastHeal,lastMove,pendingSummon;int summons;
        Member(Player p,int team,int slot,String role,boolean bot) {this.p=p;this.team=team;this.slot=slot;this.role=role;this.bot=bot;this.origin=new Location(p);}
        boolean magical() {return role.equals("MAGE") || role.equals("SUPPORT") || role.equals("HEALER");}
    }
    private static final class Team
    {final int id;final List<Member> members=new ArrayList<>();String order="cubrir";Team(int id){this.id=id;}}
    private static final class Match
    {
        final Player operator;final boolean smoke;final long started=System.currentTimeMillis();final Team[] teams=new Team[3];
        final GroupPolicy.Ladder ladder=new GroupPolicy.Ladder();final Deque<Hit> threats=new ArrayDeque<>();
        long run,phaseStarted,lastSnapshot,hits,accepted;int fightInstance,waitInstance,draws;String phase="READY";boolean summonSeen,hud;
        Match(Player operator,boolean smoke){this.operator=operator;this.smoke=smoke;}
    }
    public static void main(String[] args) {new GroupAgite();}
}
