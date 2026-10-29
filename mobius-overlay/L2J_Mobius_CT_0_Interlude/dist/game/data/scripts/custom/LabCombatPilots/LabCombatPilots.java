package custom.LabCombatPilots;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.Summon;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.enums.ShotType;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IItemHandler;
import org.l2jmobius.gameserver.handler.ItemHandler;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.network.serverpackets.ExOlympiadMode;
import org.l2jmobius.gameserver.network.serverpackets.ExOlympiadUserInfo;
import org.l2jmobius.gameserver.network.serverpackets.ExOlympiadSpelledInfo;
import org.l2jmobius.gameserver.network.serverpackets.ExOlympiadMatchEnd;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import custom.LabTelemetry.LabTelemetry;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.RealHumanPilots.RealHumanPilots;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;

/** Two opt-in real Player AI pilots. No combat stats or effect successes are fabricated. */
public class LabCombatPilots extends Script implements IVoicedCommandHandler
{
    private static final Logger LOGGER=Logger.getLogger(LabCombatPilots.class.getName());
    private static final Object LOCK=new Object();
    private static final Location CENTER=new Location(148900,46100,-3400);
    private static final long PREPARATION_MS=20000, MAX_DUEL_MS=360000;
    private static final int[][] COMMON={{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
    private static final int[][] PHYSICAL={{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1},
        {271,1},{272,1},{274,1},{275,1},{269,1},{266,1},{264,1},{267,1},{268,1},{304,1}};
    private static final int[][] MAGICAL={{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},
        {273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1}};
    private static volatile Session active;
    private boolean schemaReady;
    private Smoke smoke;
    private boolean smokeAttempted;
    private final DuelObservation observation=new DuelObservation();

    private LabCombatPilots()
    {
        try(Connection con=DatabaseFactory.getConnection();var st=con.createStatement())
        {
            st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_ai_runs (run_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,controller_id INT NOT NULL,controller_name VARCHAR(45) NOT NULL,pilot_id INT NOT NULL,pilot_name VARCHAR(45) NOT NULL,role_name VARCHAR(16) NOT NULL,started_ms BIGINT UNSIGNED NOT NULL,combat_ms BIGINT UNSIGNED NOT NULL DEFAULT 0,ended_ms BIGINT UNSIGNED NOT NULL DEFAULT 0,outcome VARCHAR(40) NOT NULL DEFAULT 'PREPARING',rules_version VARCHAR(40) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_ai_actions (action_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,run_id BIGINT UNSIGNED NOT NULL,observed_ms BIGINT UNSIGNED NOT NULL,actor_id INT NOT NULL,target_id INT NOT NULL,action_name VARCHAR(24) NOT NULL,reference_id INT NOT NULL,reference_level INT NOT NULL,result_name VARCHAR(40) NOT NULL,hp DOUBLE NOT NULL,cp DOUBLE NOT NULL,mp DOUBLE NOT NULL,KEY idx_ai_run (run_id,observed_ms)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            st.executeUpdate("ALTER TABLE lab_ai_runs ADD COLUMN IF NOT EXISTS test_mode VARCHAR(16) NOT NULL DEFAULT 'MANUAL'");
            schemaReady=true;
        }
        catch(Exception e) {LOGGER.log(Level.SEVERE,"IA Player: no se habilita sin tablas de auditoria",e);}
        VoicedCommandHandler.getInstance().registerHandler(this);
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,
            (OnCreatureDamageDealt event)->incomingDamage(event),this));
        ThreadPool.scheduleAtFixedRate(this::tick,1000,500);
        LOGGER.info("IA Player piloto instalada: .ia fisico | mago | estado | cancelar. Activacion manual GM, sin spawn automatico.");
    }

    @Override public String[] getCommandList() {return new String[]{"ia"};}

    @Override public boolean onCommand(String command,Player operator,String params)
    {
        if(!operator.isGM()) {operator.sendMessage("Pilotos IA: laboratorio GM solamente.");return true;}
        String action=params==null?"":params.trim().toLowerCase(Locale.ROOT);
        synchronized(LOCK)
        {
            if(smoke!=null) {operator.sendMessage("Autoprueba aislada IA en curso; espera unos segundos.");return true;}
            if(action.equals("estado"))
                operator.sendMessage(active==null?"No hay piloto IA activo.":"Piloto "+active.bot.getName()+" / "+(active.fighting?"COMBATE":"PREPARACION")+" / run "+active.runId);
            else if(action.equals("efectos")) showEffects(operator);
            else if(action.equals("cancelar"))
            {
                if(active!=null) finish("CANCELLED",operator);else operator.sendMessage("No hay prueba IA activa.");
            }
            else if(action.equals("fisico") || action.equals("probar fisico")) start(operator,false);
            else if(action.equals("mago") || action.equals("probar mago")) start(operator,true);
            else operator.sendMessage(".ia fisico (Riven) | .ia mago (Noctis) | .ia estado | .ia cancelar");
        }
        return true;
    }

    /** Read-only combat relationship for assistants; clan membership alone cannot describe a lab duel. */
    public static boolean isCombatOpponent(Player operator,Creature candidate)
    {
        Session s=active;
        return s!=null&&s.fighting&&operator!=null&&candidate!=null
            &&s.controllerId==operator.getObjectId()&&candidate.asPlayer()==s.bot
            &&operator.getInstanceId()==s.bot.getInstanceId()&&!s.bot.isInvul();
    }

    private static boolean inside(Player player)
    {
        return player!=null && player.isOnline();
    }

    private void start(Player operator,boolean mage)
    {
        if(!schemaReady || !NormalNpcRoster.isReady()) {operator.sendMessage("Espera la preparacion completa del laboratorio.");return;}
        if(!inside(operator) || operator.isDead()) {operator.sendMessage("Debes estar conectado y vivo para invocar un piloto IA.");return;}
        if(active!=null)
        {
            if(active.controllerId!=operator.getObjectId()) {operator.sendMessage("Hay un piloto IA en uso por otro jugador.");return;}
            finish("RESPAWNED",operator);
        }
        if(!SoloArenaGauntlet.tryClaimPilot()) {operator.sendMessage("Termina primero el experimento .arena activo.");return;}
        Player bot=null;
        Session session=null;
        try
        {
            bot=loadProfile(mage);
            session=new Session(bot,operator,mage);
            bot.setLabControlled(true);
            bot.setOnlineStatus(true,true);
            bot.setDead(false);
            bot.stopAllEffects();
            // External laboratory buffer, same preset as the NPC roster; own skills use useMagic below.
            for(int[][] group:new int[][][]{COMMON,mage?MAGICAL:PHYSICAL})
                for(int[] buff:group) SkillData.getInstance().getSkill(buff[0],buff[1]).applyEffects(bot,bot);
            bot.setCurrentHpMp(bot.getMaxHp(),bot.getMaxMp());bot.setCurrentCp(bot.getMaxCp());
            stock(bot,1539,10);stock(bot,5592,50);stock(bot,728,30);stock(bot,1467,2000);stock(bot,3952,2000);
            for(int skillId:new int[]{33,22,278,1281,1333,1401})
            {
                Skill skill=bot.getKnownSkill(skillId);
                if(skill!=null && skill.getItemConsumeId()>0) stock(bot,skill.getItemConsumeId(),Math.max(100,skill.getItemConsumeCount()*5));
            }
            bot.setTitle(mage?"IA mago / Noctis":"IA fisico / Riven");
            bot.setInvul(true);bot.setRunning();
            bot.setEnteredWorld();
            bot.setInstanceId(operator.getInstanceId());
            Location spawn=GeoEngine.getInstance().getValidLocation(operator.getX(),operator.getY(),operator.getZ(),
                operator.getX(),operator.getY()-300,operator.getZ(),operator.getInstanceId());
            bot.spawnMe(spawn.getX(),spawn.getY(),spawn.getZ());
            bot.revalidateZone(true);
            bot.broadcastUserInfo();
            session.runId=createRun(session,operator);
            observation.begin(session.runId);
            active=session;
            LabTelemetry.capturePilotStatsNow(bot);
            operator.sendMessage("Piloto Player "+bot.getName()+": 20 segundos para preparacion. Usa .ia cancelar para detenerlo.");
        }
        catch(Exception e)
        {
            LOGGER.log(Level.SEVERE,"No se inicio el piloto Player",e);
            if(bot!=null) cleanup(bot,session);
            SoloArenaGauntlet.releasePilot();
            operator.sendMessage("No se pudo iniciar el piloto. Revisa el log; no se cambio tu personaje.");
        }
    }

    private static Player loadProfile(boolean mage) throws Exception
    {
        String name=mage?"ArenaNoctis":"ArenaRiven";
        int id=0;
        try(Connection con=DatabaseFactory.getConnection();PreparedStatement ps=con.prepareStatement(
            "SELECT c.charId,c.online,c.account_name,p.recipe_version,p.npc_template_id FROM characters c JOIN lab_normal_npc_profiles p ON p.char_id=c.charId WHERE c.char_name=?"))
        {
            ps.setString(1,name);
            try(ResultSet rs=ps.executeQuery())
            {
                if(!rs.next() || rs.getInt("online")!=0 || !"telemetryarena2".equals(rs.getString("account_name"))
                || rs.getInt("npc_template_id")!=(mage?901111:901110)
                || !"normal-pvp-s4-hybrid-v2".equals(rs.getString("recipe_version")))
                throw new IllegalStateException("Perfil reservado no disponible: "+name);
                id=rs.getInt("charId");
            }
        }
        if(World.getPlayer(id)!=null) throw new IllegalStateException("Perfil ya cargado: "+name);
        Player bot=Player.load(id);
        try
        {
            if(bot==null || bot.getClient()!=null || bot.getClassIndex()!=0 || bot.getInstanceId()!=0 || bot.getBaseClass()!=(mage?115:93))
            throw new IllegalStateException("Principal o cliente inesperado");
        int[] recipe=mage?new int[]{97,106,111}:new int[]{114,113,106};
        if(bot.getSubClasses().size()!=3) throw new IllegalStateException("Se requieren tres subs");
        for(int slot=1;slot<=3;slot++)
            if(bot.getSubClasses().get(slot)==null || bot.getSubClasses().get(slot).getId()!=recipe[slot-1])
                throw new IllegalStateException("Build editada; no se sobrescribe");
        RealHumanPilots.verifyActiveSkills(bot);
        return bot;
        }
        catch(Exception e)
        {
            if(bot!=null && bot.getClient()==null) bot.deleteMe();
            throw e;
        }
    }

    private void tick()
    {
        synchronized(LOCK)
        {
            if(schemaReady && Boolean.getBoolean("lab.ai.smoke") && !smokeAttempted && NormalNpcRoster.isReady())
            {smokeAttempted=true;beginSmoke();}
            if(smoke!=null) {advanceSmoke();return;}
            Session s=active;
            if(s==null) return;
            try
            {
                Player target=World.getPlayer(s.controllerId);
                observation.sample(s.runId,s.bot,target);
                updateHud(s,target);
                observeSummon(s);
                if(!inside(target) || !inside(s.bot) || target.getInstanceId()!=s.bot.getInstanceId())
                {finish("CONTROLLER_UNAVAILABLE",target);return;}
                if(s.bot.isDead()) {finish("PLAYER_WIN",target);return;}
                if(target.isDead()) {finish("PILOT_WIN",target);return;}
                long now=System.currentTimeMillis();
                if(now-s.started>MAX_DUEL_MS) {finish("TIME_LIMIT",target);return;}
                double hp=ratio(s.bot.getCurrentHp(),s.bot.getMaxHp()),mp=ratio(s.bot.getCurrentMp(),s.bot.getMaxMp());
                if(s.mage)
                {
                    if(!Policy.arcanePower(hp,mp,s.bot.isAffectedBySkill(337))) toggle(s,337,false);
                    if(!Policy.soulGuard(mp,s.bot.isAffectedBySkill(1283))) toggle(s,1283,false);
                    if(!s.bot.hasSummon() || s.bot.getSummon().isDead()) toggle(s,1262,false);
                }
                if(s.bot.isCastingNow() || s.bot.isOutOfControl() || s.bot.isControlBlocked()) return;
                if(!s.fighting)
                {
                    prepare(s);
                    if(now-s.started>=PREPARATION_MS && !s.bot.isCastingNow())
                    {
                        s.fighting=true;s.bot.setInvul(false);
                        updateRun(s,"FIGHTING",false);
                        target.sendMessage("Comienza la prueba contra "+s.bot.getName()+". Telemetria run "+s.runId+".");
                    }
                    return;
                }
                if(s.bot.isInvul()) {finish("UNEXPECTED_INVUL",target);return;}
                // Emergency skills precede HP potions, so their legal low-HP conditions can still be met.
                if(Policy.emergency(hp))
                {
                    if(!s.mage && !s.bot.isAffectedBySkill(139) && !s.bot.isAffectedBySkill(176)
                        && cast(s,hp<0.20?139:176,s.bot,"EMERGENCY",false)) return;
                    if(!s.mage && cast(s,420,s.bot,"ZEALOT",false)) return;
                    if(cast(s,110,s.bot,"DEFENCE",false)) return;
                }
                resources(s);
                if(s.bot.isCastingNow()) return;
                if(now-s.lastSetup>10000 && hp>0.60 && mp>0.35)
                {
                    s.lastSetup=now;
                    if(prepare(s)) return;
                }
                if(s.mage)
                {
                    // Give close-range control a chance before repeating a non-emergency heal.
                    if(hp>=0.25 && target.isCastingNow() && cast(s,1246,target,"SILENCE",false)) return;
                    if(hp>=0.25 && hp<0.60 && cast(s,1208,target,"ESCAPE_ROOT",false)) return;
                    if(Policy.selfHeal(hp,now-s.lastSelfHeal) && cast(s,1401,s.bot,"HEAL_SELF",true)) {s.lastSelfHeal=now;return;}
                    if(Policy.selfHeal(hp,now-s.lastSelfHeal) && cast(s,1218,s.bot,"HEAL_SELF",true)) {s.lastSelfHeal=now;return;}
                    Summon pet=s.bot.getSummon();
                    if(pet!=null && !pet.isDead() && ratio(pet.getCurrentHp(),pet.getMaxHp())<0.55)
                    {
                        Skill heal=s.bot.getKnownSkill(1127);
                        if(heal!=null && (s.bot.calculateDistance2D(pet)>heal.getCastRange() || !GeoEngine.getInstance().canSeeTarget(s.bot,pet)))
                        {
                            pet.abortAttack();pet.setFollowStatus(true);pet.getAI().setIntentionFollow(s.bot);
                            s.petRecallUntil=now+3000;
                            if(now-s.lastRecallAudit>3000) {audit(s,"RECALL_SUMMON",1127,heal.getLevel(),pet,"HEAL_RANGE_OR_LOS");s.lastRecallAudit=now;}
                        }
                        else if(cast(s,1127,pet,"HEAL_SUMMON",true)) return;
                    }
                    if(pet!=null && pet.isDead()) {pet.unSummon(s.bot);pet=null;}
                    if(pet==null && toggle(s,1262,false)) return;
                    if(pet==null && hp>0.60 && cast(s,1333,s.bot,"SUMMON",false)) return;
                    if(pet!=null && !pet.isDead())
                    {
                        if(cast(s,1262,s.bot,"TRANSFER_PAIN",false)) return;
                        if(now>=s.petRecallUntil) {pet.setFollowStatus(false);pet.setTarget(target);pet.getAI().setIntentionAttack(target);}
                    }
                    if(toggle(s,337,Policy.arcanePower(hp,mp,s.bot.isAffectedBySkill(337)))) return;
                    if(toggle(s,1283,Policy.soulGuard(mp,s.bot.isAffectedBySkill(1283)))) return;
                    if(target.isCastingNow() && cast(s,1246,target,"SILENCE",false)) return;
                    if(cast(s,1208,target,"ROOT",false)) return;
                    if(cast(s,1366,target,"CURSE",false)) return;
                    if(cast(s,1245,target,"DRAIN",true)) return;
                }
                else
                {
                    if(toggle(s,312,Policy.stance(mp,s.bot.isAffectedBySkill(312)))) return;
                    if(hp<0.55 && cast(s,121,s.bot,"BATTLE_ROAR",false)) return;
                    if(cast(s,445,s.bot,"MIRAGE",false)) return;
                    if(cast(s,358,target,"BLUFF",false)) return;
                    if(cast(s,402,target,"ROOT",false)) return;
                    if(cast(s,122,target,"HEX",false)) return;
                    if(behind(s.bot,target) && cast(s,30,target,"BACKSTAB",true)) return;
                    if(cast(s,344,target,"LETHAL_BLOW",true)) return;
                    if(cast(s,263,target,"DEADLY_BLOW",true)) return;
                    if(cast(s,11,target,"TRICK",false)) return;
                    if(cast(s,12,target,"SWITCH",false)) return;
                    if(s.bot.calculateDistance2D(target)>250 && cast(s,4,s.bot,"DASH",false)) return;
                }
                moveOrAttack(s,target);
                if(now-s.lastStats>3000) {LabTelemetry.capturePilotStatsNow(s.bot);s.lastStats=now;}
            }
            catch(Exception e) {LOGGER.log(Level.SEVERE,"IA Player detenida por error",e);finish("ERROR",World.getPlayer(s.controllerId));}
        }
    }

    private boolean prepare(Session s)
    {
        int[] ids=s.mage?new int[]{1333,33,1281,278,1262,1283,337}:new int[]{33,22,278,282,312};
        for(int id:ids)
        {
            if(id==1333 && s.bot.hasSummon()) continue;
            if(id==1333 && (!Policy.canSummon(s.summons,s.summonAttempts,s.summonPendingUntil,System.currentTimeMillis())
                || (s.fighting && ratio(s.bot.getCurrentHp(),s.bot.getMaxHp())<=0.60))) continue;
            if(id==1262 && !s.bot.hasSummon()) continue;
            if(id==337 && !Policy.arcanePower(ratio(s.bot.getCurrentHp(),s.bot.getMaxHp()),ratio(s.bot.getCurrentMp(),s.bot.getMaxMp()),false)) continue;
            if((id==1283 || id==312) && ratio(s.bot.getCurrentMp(),s.bot.getMaxMp())<0.45) continue;
            int cubicId=cubicId(id);
            if(cubicId>=0 && s.bot.getCubicById(cubicId)!=null) continue;
            if(cast(s,id,s.bot,"PREPARE",false)) return true;
        }
        return false;
    }

    private boolean toggle(Session s,int id,boolean enabled)
    {
        Skill skill=s.bot.getKnownSkill(id);
        if(skill==null || !skill.isToggle() || s.bot.isAffectedBySkill(id)==enabled) return false;
        if(!enabled)
        {
            s.bot.stopSkillEffects(SkillFinishType.REMOVED,id);
            audit(s,"TOGGLE_OFF",id,skill.getLevel(),s.bot,s.bot.isAffectedBySkill(id)?"STILL_ACTIVE":"EFFECT_REMOVED");
            return true;
        }
        return cast(s,id,s.bot,enabled?"TOGGLE_ON":"TOGGLE_OFF",true);
    }

    private boolean cast(Session s,int id,Creature target,String reason,boolean repeat)
    {
        Skill skill=s.bot.getKnownSkill(id);
        long now=System.currentTimeMillis();
        if(skill==null || skill.isPassive() || now<s.nextAttempt.getOrDefault(id,0L)) return false;
        if(id==1333 && !Policy.canSummon(s.summons,s.summonAttempts,s.summonPendingUntil,now)) return false;
        if(!repeat && target.isAffectedBySkill(id)) return false;
        s.nextAttempt.put(id,now+1500);
        String blocked=null;
        if(s.bot.isSkillDisabled(skill)) blocked="REUSE";
        else if(s.bot.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume()) blocked="NO_MP";
        else if(s.bot.getCurrentHp()<=skill.getHpConsume()) blocked="NO_HP";
        else if(target!=s.bot && !GeoEngine.getInstance().canSeeTarget(s.bot,target)) blocked="NO_LINE_OF_SIGHT";
        else if(target!=s.bot && s.bot.calculateDistance2D(target)>Math.max(40,skill.getCastRange()<0?skill.getAffectRange():skill.getCastRange())+35) blocked="RANGE";
        else if(skill.getItemConsumeId()>0 && s.bot.getInventory().getInventoryItemCount(skill.getItemConsumeId(),-1)<skill.getItemConsumeCount()) blocked="NO_REAGENT";
        if(blocked!=null) {audit(s,"SKILL",id,skill.getLevel(),target,blocked);return false;}
        s.bot.setTarget(target);
        if(!skill.checkCondition(s.bot,target,false)) {audit(s,"SKILL",id,skill.getLevel(),target,"CONDITION");return false;}
        charge(s,skill.isMagic());
        boolean accepted=s.bot.useMagic(skill,true,true);
        if(id==1333 && accepted) {s.summonAttempts++;s.summonPendingUntil=now+Math.max(20000,skill.getHitTime()+5000);}
        audit(s,reason,id,skill.getLevel(),target,accepted?"CAST_REQUEST_ACCEPTED":"CAST_REQUEST_REJECTED");
        // Accepted is not landed: actual casts/damage/resists remain engine events in lab_combat_events.
        return accepted;
    }

    private void resources(Session s)
    {
        if(Policy.cpPotion(ratio(s.bot.getCurrentCp(),s.bot.getMaxCp()))) item(s,5592,true);
        if(Policy.hpPotion(ratio(s.bot.getCurrentHp(),s.bot.getMaxHp())) && !s.bot.isAffectedBySkill(2037)) item(s,1539,true);
        if(Policy.mpPotion(ratio(s.bot.getCurrentMp(),s.bot.getMaxMp()))) item(s,728,true);
    }

    private void charge(Session s,boolean magic)
    {
        if(magic?!s.bot.isChargedShot(ShotType.BLESSED_SPIRITSHOTS):!s.bot.isChargedShot(ShotType.SOULSHOTS))
            item(s,magic?3952:1467,false);
    }

    private boolean item(Session s,int id,boolean potion)
    {
        if(potion && s.potions.getOrDefault(id,0)<=0) return false;
        Item item=s.bot.getInventory().getItemByItemId(id);
        if(item==null || item.getCount()<=0 || s.bot.isOutOfControl() || s.bot.isControlBlocked()) return false;
        if(s.bot.getItemRemainingReuseTime(item.getObjectId())>0 || (item.getReuseDelay()>0 && s.bot.getReuseDelayOnGroup(item.getSharedReuseGroup())>0)) return false;
        if(!item.getTemplate().checkCondition(s.bot,s.bot,false)) return false;
        IItemHandler handler=ItemHandler.getInstance().getHandler(item.getEtcItem());
        if(handler==null) {audit(s,"ITEM",id,0,s.bot,"NO_HANDLER");return false;}
        if(potion) s.bot.setTarget(s.bot);
        long before=item.getCount();
        boolean used=handler.onItemUse(s.bot,item,false);
        if(used && item.getReuseDelay()>0) s.bot.addTimeStampItem(item,item.getReuseDelay());
        if(used && potion) s.potions.merge(id,-1,Integer::sum);
        audit(s,potion?"POTION":"SHOT",id,0,s.bot,used?(item.getCount()<before?"CONSUMED":"ACCEPTED"):"REJECTED");
        return used;
    }

    private void moveOrAttack(Session s,Player target)
    {
        double distance=s.bot.calculateDistance2D(target);
        long now=System.currentTimeMillis();
        s.bot.setTarget(target);
        if(s.mage && distance<150 && now-s.lastMove>1500)
        {
            double angle=Math.atan2(s.bot.getY()-target.getY(),s.bot.getX()-target.getX());
            Location dest=GeoEngine.getInstance().getValidLocation(s.bot.getX(),s.bot.getY(),s.bot.getZ(),
                s.bot.getX()+(int)(Math.cos(angle)*220),s.bot.getY()+(int)(Math.sin(angle)*220),s.bot.getZ(),s.bot.getInstanceId());
            s.bot.getAI().setIntentionMoveTo(dest);s.lastMove=now;return;
        }
        if(s.mage && distance>550) s.bot.getAI().setIntentionFollow(target);
        else if(!s.mage) {charge(s,false);s.bot.getAI().setIntentionAttack(target);}
    }

    private static boolean behind(Creature actor,Creature target)
    {
        double radians=target.getHeading()*2.0*Math.PI/65536.0;
        return (actor.getX()-target.getX())*Math.cos(radians)+(actor.getY()-target.getY())*Math.sin(radians)<-15;
    }
    private static double ratio(double value,double max) {return max>0?value/max:0;}
    private static void stock(Player bot,int id,int count)
    {
        long current=bot.getInventory().getInventoryItemCount(id,-1);
        if(current<count && bot.getInventory().addItem(ItemProcessType.NONE,id,(int)(count-current),bot,null)==null)
            throw new IllegalStateException("No existe consumible "+id);
    }

    private long createRun(Session s,Player operator) throws Exception
    {
        try(Connection con=DatabaseFactory.getConnection();PreparedStatement ps=con.prepareStatement(
            "INSERT INTO lab_ai_runs (controller_id,controller_name,pilot_id,pilot_name,role_name,started_ms,rules_version,test_mode) VALUES (?,?,?,?,?,?,?,?)",java.sql.Statement.RETURN_GENERATED_KEYS))
        {
            ps.setInt(1,operator.getObjectId());ps.setString(2,operator.getName());ps.setInt(3,s.bot.getObjectId());ps.setString(4,s.bot.getName());
            ps.setString(5,s.mage?"MAGICAL":"PHYSICAL");ps.setLong(6,s.started);ps.setString(7,"fixed-racial-hybrid-third-v1");ps.setString(8,s.smoke?"SMOKE":"MANUAL");ps.executeUpdate();
            try(ResultSet rs=ps.getGeneratedKeys()) {if(!rs.next()) throw new IllegalStateException("Sin run IA");return rs.getLong(1);}
        }
    }
    private void updateRun(Session s,String outcome,boolean ended)
    {
        try(Connection con=DatabaseFactory.getConnection();PreparedStatement ps=con.prepareStatement(ended?
            "UPDATE lab_ai_runs SET outcome=?,ended_ms=? WHERE run_id=?":"UPDATE lab_ai_runs SET outcome=?,combat_ms=? WHERE run_id=?"))
        {ps.setString(1,outcome);ps.setLong(2,System.currentTimeMillis());ps.setLong(3,s.runId);ps.executeUpdate();}
        catch(Exception e) {LOGGER.log(Level.WARNING,"No se actualizo run IA",e);}
    }
    private void audit(Session s,String action,int reference,int level,Creature target,String result)
    {
        long time=System.currentTimeMillis();int targetId=target==null?0:target.getObjectId();
        double hp=s.bot.getCurrentHp(),cp=s.bot.getCurrentCp(),mp=s.bot.getCurrentMp();
        ThreadPool.execute(()->{
            try(Connection con=DatabaseFactory.getConnection();PreparedStatement ps=con.prepareStatement(
                "INSERT INTO lab_ai_actions (run_id,observed_ms,actor_id,target_id,action_name,reference_id,reference_level,result_name,hp,cp,mp) VALUES (?,?,?,?,?,?,?,?,?,?,?)"))
            {ps.setLong(1,s.runId);ps.setLong(2,time);ps.setInt(3,s.bot.getObjectId());ps.setInt(4,targetId);ps.setString(5,action);ps.setInt(6,reference);ps.setInt(7,level);ps.setString(8,result);ps.setDouble(9,hp);ps.setDouble(10,cp);ps.setDouble(11,mp);ps.executeUpdate();}
            catch(Exception e) {LOGGER.log(Level.WARNING,"No se guardo decision IA",e);}
        });
    }
    private void finish(String outcome,Player operator)
    {
        Session s=active;active=null;
        if(s==null) return;
        try {closeHud(s,operator);observation.sample(s.runId,s.bot,operator);observation.end(s.runId);updateRun(s,outcome,true);cleanup(s.bot,s);}
        finally {SoloArenaGauntlet.releasePilot();}
        if(operator!=null) operator.sendMessage("Prueba IA terminada: "+outcome+". Run "+s.runId+".");
    }
    private static void cleanup(Player bot,Session s)
    {
        try
        {
            bot.abortAttack();bot.abortCast();bot.getAI().setIntentionIdle();
            if(bot.hasSummon()) bot.getSummon().unSummon(bot);
            bot.setTarget(null);bot.setInvul(false);bot.stopAllEffects();
            if(s!=null) {bot.setTitle(s.title);bot.decayMe();bot.setInstanceId(0);bot.setXYZInvisible(s.origin.getX(),s.origin.getY(),s.origin.getZ());}
            bot.storeMe();
        }
        finally {bot.deleteMe();bot.setLabControlled(false);bot.setOnlineStatus(false,true);}
    }

    private static final class Session
    {
        final Player bot;final int controllerId;final boolean mage;final Location origin;final String title;
        final long started=System.currentTimeMillis();
        final Map<Integer,Long> nextAttempt=new HashMap<>();
        final Map<Integer,Integer> potions=new HashMap<>();
        long runId,lastMove,lastStats,lastSetup,lastSelfHeal,summonPendingUntil,petRecallUntil,lastRecallAudit;
        int lastSummonId,summons,summonAttempts;volatile boolean fighting;boolean smoke,hud;
        long lastHudEffects;
        Session(Player bot,Player operator,boolean mage)
        {this.bot=bot;this.controllerId=operator.getObjectId();this.mage=mage;origin=new Location(bot);title=bot.getTitle();potions.put(1539,10);potions.put(5592,50);potions.put(728,30);}
    }

    private void updateHud(Session s,Player operator)
    {
        if(operator==null) return;
        if(operator.getTarget()!=s.bot) {closeHud(s,operator);return;}
        if(!s.hud) {operator.sendPacket(new ExOlympiadMode(2));s.hud=true;}
        operator.sendPacket(new ExOlympiadUserInfo(s.bot,1));
        long now=System.currentTimeMillis();
        if(now-s.lastHudEffects>=1000)
        {
            ExOlympiadSpelledInfo spells=new ExOlympiadSpelledInfo(s.bot);
            for(var info:s.bot.getEffectList().getEffects()) if(info.isInUse() && !info.getSkill().isPassive()) spells.addSkill(info);
            operator.sendPacket(spells);s.lastHudEffects=now;
        }
    }
    private void closeHud(Session s,Player operator)
    {
        if(!s.hud || operator==null) return;
        s.hud=false;s.lastHudEffects=0;
        operator.sendPacket(ExOlympiadMatchEnd.STATIC_PACKET);operator.sendPacket(new ExOlympiadMode(0));
        // Do not hide the existing NPC HUD if the operator switched to a roster NPC.
        if(operator.getTarget()!=null && operator.getTarget().isNpc() && operator.getTarget().asNpc().isFakePlayer())
        {
            operator.sendPacket(new ExOlympiadMode(2));operator.sendPacket(new ExOlympiadUserInfo(operator.getTarget().asNpc(),1));
        }
    }
    private void incomingDamage(OnCreatureDamageDealt event)
    {
        synchronized(LOCK)
        {
            Session s=active;
            if(s==null || !s.fighting || event.getDamage()<=0 || event.getTarget()==null || event.getTarget().getObjectId()!=s.controllerId) return;
            Creature attacker=event.getAttacker();
            if(attacker==null || (attacker!=s.bot && !(attacker.isSummon() && attacker.asSummon().getOwner()==s.bot))) return;
            Player operator=World.getPlayer(s.controllerId);
            if(operator==null) return;
            boolean magic=event.getSkill()!=null && event.getSkill().isMagic();
            int id=magic?(event.isCritical()?2207:2206):(event.isCritical()?2205:2204);
            operator.sendPacket(new PilotDamageMessage(id,attacker.getName(),(int)Math.round(event.getDamage())));
        }
    }
    private void showEffects(Player operator)
    {
        Session s=active;
        if(s==null || s.controllerId!=operator.getObjectId()) {operator.sendMessage("Primero inicia .ia fisico o .ia mago.");return;}
        StringBuilder html=new StringBuilder("<html><body><center><font color=LEVEL>Efectos de "+escape(s.bot.getName())+"</font></center><br>Buffs y maldiciones activos, no intentos de casteo.<br><table width=285>");
        int count=0;
        for(var info:s.bot.getEffectList().getEffects())
        {
            Skill skill=info.getSkill();
            if(!info.isInUse() || skill.isPassive()) continue;
            if(++count>36) break;
            html.append("<tr><td><font color=").append(skill.isDebuff()?"FF7777":"99DDFF").append(">")
                .append(skill.isDebuff()?"Debuff: ":"Buff: ").append(escape(skill.getName())).append(" Lv").append(skill.getLevel())
                .append("</font></td><td>").append(info.getTime()).append("s</td></tr>");
        }
        html.append("</table><br>Actualiza con .ia efectos. Max36 efectos en esta vista.</body></html>");
        NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(html.toString());operator.sendPacket(packet);
    }
    private static String escape(String value) {return value.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;");}

    /** Pure, testable thresholds. All spell legality and successes stay with the game engine. */
    public static final class Policy
    {
        public static boolean emergency(double hp) {return hp<0.30;}
        public static boolean cpPotion(double cp) {return cp<0.55;}
        public static boolean hpPotion(double hp) {return hp<0.65;}
        public static boolean mpPotion(double mp) {return mp<0.35;}
        public static boolean arcanePower(double hp,double mp,boolean active) {return active?hp>0.35 && mp>0.20:hp>0.65 && mp>0.50;}
        public static boolean soulGuard(double mp,boolean active) {return mp>(active?0.20:0.45);}
        public static boolean stance(double mp,boolean active) {return mp>(active?0.15:0.40);}
        public static boolean selfHeal(double hp,long sinceLast) {return hp<0.25 || (hp<0.60 && sinceLast>=4000);}
        public static boolean canSummon(int confirmed,int attempts,long pendingUntil,long now) {return confirmed<2 && attempts<2 && now>=pendingUntil;}
    }
    private void observeSummon(Session s)
    {
        Summon pet=s.bot.getSummon();
        if(pet!=null && pet.getObjectId()!=s.lastSummonId)
        {
            s.lastSummonId=pet.getObjectId();s.summons++;s.summonPendingUntil=0;
            audit(s,"SUMMON_OBSERVED",1333,s.summons,pet,pet.isDead()?"DEAD":"ALIVE");
        }
    }
    public static int cubicId(int skillId)
    {
        return switch(skillId) {case 22 -> 2;case 33 -> 5;case 278 -> 4;case 1281 -> 8;default -> -1;};
    }

    /** Explicit JVM opt-in only. Real casts in a private instance; never attacks the user's character. */
    private void beginSmoke()
    {
        if(!SoloArenaGauntlet.tryClaimPilot()) {LOGGER.warning("AI_SMOKE skipped: arena occupied");return;}
        Smoke test=new Smoke();smoke=test;
        try
        {
            test.instanceId=InstanceManager.getInstance().createDynamicInstance(0).getId();
            if(Boolean.getBoolean("lab.geo.verify"))
            {
                GeoEngine geo=GeoEngine.getInstance();
                if(!geo.hasGeo(148900,46100) || !geo.hasGeo(45500,48300)) throw new IllegalStateException("Missing Coliseum/Elven geodata");
                var nodes=javax.xml.parsers.DocumentBuilderFactory.newInstance().newDocumentBuilder()
                    .parse(new java.io.File("data/spawns/Others/SoloArena.xml")).getElementsByTagName("npc");
                int checked=0;
                for(int i=0;i<nodes.getLength();i++)
                {
                    var e=(org.w3c.dom.Element)nodes.item(i);int id=Integer.parseInt(e.getAttribute("id"));
                    if(id<901100 || id>901118) continue;
                    int x=Integer.parseInt(e.getAttribute("x")),y=Integer.parseInt(e.getAttribute("y"));
                    int z=geo.getHeight(x,y,-3400);
                    if(Math.abs(z+3400)>100 || !geo.canMoveToTarget(x,y,z,148900,46100,-3408,test.instanceId))
                        throw new IllegalStateException("Unsafe waiting spot: "+id);
                    checked++;
                }
                if(checked!=19 || geo.canMoveToTarget(148300,45600,-3408,148300,44900,-2936,test.instanceId))
                    throw new IllegalStateException("Roster coverage/north boundary check failed");
                LOGGER.info("GEO_SMOKE PASS: 19 interior floor/routes, north raised boundary blocked, Elven preserved");
            }
            Player physical=loadProfile(false),magical=null;
            test.physical=new Session(physical,physical,false);
            magical=loadProfile(true);test.magical=new Session(magical,physical,true);
            for(Session s:new Session[]{test.physical,test.magical})
            {
                s.smoke=true;s.bot.setLabControlled(true);s.bot.setOnlineStatus(true,true);s.bot.setDead(false);
                s.bot.stopAllEffects();
                for(int[][] group:new int[][][]{COMMON,s.mage?MAGICAL:PHYSICAL})
                    for(int[] buff:group) SkillData.getInstance().getSkill(buff[0],buff[1]).applyEffects(s.bot,s.bot);
                s.bot.setCurrentHpMp(s.bot.getMaxHp(),s.bot.getMaxMp());s.bot.setCurrentCp(s.bot.getMaxCp());
                stock(s.bot,5592,50);stock(s.bot,728,30);stock(s.bot,1539,10);stock(s.bot,1467,2000);stock(s.bot,3952,2000);
                for(int id:new int[]{1333,33,22,1401})
                {
                    Skill skill=s.bot.getKnownSkill(id);
                    if(skill!=null && skill.getItemConsumeId()>0) stock(s.bot,skill.getItemConsumeId(),Math.max(100,skill.getItemConsumeCount()*5));
                }
                s.bot.setInstanceId(test.instanceId);s.bot.setEnteredWorld();
                s.bot.spawnMe(148900,s.mage?46100:46200,-3400);s.bot.revalidateZone(true);
                s.runId=createRun(s,physical);
                if(s.bot.isOnlineInt()!=2 || World.getPlayer(s.bot.getObjectId())!=s.bot)
                    throw new IllegalStateException("Headless Player not visible/registered");
            }
            observation.begin(test.magical.runId);
            LOGGER.info("AI_SMOKE START: two visible Players, private instance="+test.instanceId);
        }
        catch(Exception e) {LOGGER.log(Level.SEVERE,"AI_SMOKE setup failed",e);endSmoke(false);}
    }

    private void advanceSmoke()
    {
        Smoke t=smoke;
        try
        {
            if(System.currentTimeMillis()-t.started>120000) throw new IllegalStateException("Smoke timed out");
            Session mage=t.magical,phys=t.physical;
            observation.sample(mage.runId,mage.bot,phys.bot);
            if(mage.bot.isCastingNow() || phys.bot.isCastingNow() || System.currentTimeMillis()<t.waitUntil) return;
            if(t.pending)
            {
                boolean passed=switch(t.stage)
                {
                    case 0 -> mage.bot.hasSummon() && mage.bot.getSummon().getInstanceId()==t.instanceId;
                    case 1 -> mage.bot.getCubicById(5)!=null;
                    case 2 -> mage.bot.isAffectedBySkill(1262);
                    case 3 -> phys.bot.isAffectedBySkill(282);
                    case 4 -> phys.bot.getCubicById(2)!=null;
                    case 5 -> phys.bot.getPDef(null)>t.before;
                    case 6 -> mage.bot.getCurrentHp()>t.before;
                    case 7 -> mage.bot.getSummon().getCurrentHp()>t.before;
                    case 8 -> phys.bot.getCurrentCp()>t.before && phys.bot.getInventory().getInventoryItemCount(5592,-1)<t.itemBefore;
                    case 9 -> mage.bot.getCurrentMp()>t.before && mage.bot.getInventory().getInventoryItemCount(728,-1)<t.itemBefore;
                    case 10 -> mage.bot.getSummon().isInsideRadius2D(mage.bot,180);
                    case 11 -> phys.bot.getCurrentHp()+phys.bot.getCurrentCp()<t.before;
                    default -> false;
                };
                if(!passed) throw new IllegalStateException("Smoke stage="+t.stage+" no real result");
                LOGGER.info("AI_SMOKE PASS stage="+t.stage);
                audit(mage,"SMOKE_CHECK",t.stage,0,phys.bot,"REAL_RESULT_PASS");
                t.stage++;t.pending=false;
                if(t.stage==12) {endSmoke(true);return;}
            }
            boolean accepted=false;
            switch(t.stage)
            {
                case 0 -> accepted=cast(mage,1333,mage.bot,"SMOKE_SUMMON",true);
                case 1 -> accepted=cast(mage,33,mage.bot,"SMOKE_CUBIC",true);
                case 2 -> accepted=cast(mage,1262,mage.bot,"SMOKE_TP",true);
                case 3 -> accepted=cast(phys,282,phys.bot,"SMOKE_TOTEM",true);
                case 4 -> accepted=cast(phys,22,phys.bot,"SMOKE_CUBIC",true);
                case 5 -> {t.before=phys.bot.getPDef(null);accepted=cast(phys,110,phys.bot,"SMOKE_UD",true);}
                case 6 -> {mage.bot.setCurrentHp(mage.bot.getMaxHp()*0.40);t.before=mage.bot.getCurrentHp();accepted=cast(mage,1401,mage.bot,"SMOKE_HEAL_SELF",true);}
                case 7 -> {mage.bot.getSummon().setCurrentHp(mage.bot.getSummon().getMaxHp()*0.40);t.before=mage.bot.getSummon().getCurrentHp();accepted=cast(mage,1127,mage.bot.getSummon(),"SMOKE_HEAL_PET",true);}
                case 8 -> {phys.bot.setCurrentCp(phys.bot.getMaxCp()*0.40);t.before=phys.bot.getCurrentCp();t.itemBefore=phys.bot.getInventory().getInventoryItemCount(5592,-1);accepted=item(phys,5592,true);}
                case 9 -> {mage.bot.setCurrentMp(mage.bot.getMaxMp()*0.40);t.before=mage.bot.getCurrentMp();t.itemBefore=mage.bot.getInventory().getInventoryItemCount(728,-1);accepted=item(mage,728,true);}
                case 10 -> {
                    mage.bot.teleToLocation(149300,46100,-3408,0,t.instanceId,false);mage.bot.onTeleported();
                    mage.bot.getSummon().teleToLocation(148900,46100,-3408,0,t.instanceId,false);
                    mage.bot.getSummon().setRunning();mage.bot.getSummon().setFollowStatus(true);
                    mage.bot.getSummon().getAI().setIntentionFollow(mage.bot);accepted=true;
                }
                case 11 -> {
                    phys.bot.stopSkillEffects(SkillFinishType.REMOVED,110);phys.bot.setInvul(false);
                    phys.bot.setCurrentHpMp(phys.bot.getMaxHp(),phys.bot.getMaxMp());phys.bot.setCurrentCp(phys.bot.getMaxCp());
                    phys.bot.teleToLocation(149500,46100,-3408,0,t.instanceId,false);phys.bot.onTeleported();
                    mage.bot.getSummon().teleToLocation(148900,46100,-3408,0,t.instanceId,false);
                    t.before=phys.bot.getCurrentHp()+phys.bot.getCurrentCp();
                    mage.bot.getSummon().setFollowStatus(false);mage.bot.getSummon().setTarget(phys.bot);
                    mage.bot.getSummon().getAI().setIntentionAttack(phys.bot);accepted=true;
                }
            }
            if(accepted) {t.pending=true;t.waitUntil=System.currentTimeMillis()+(t.stage>=10?6000:1500);}
        }
        catch(Exception e) {LOGGER.log(Level.SEVERE,"AI_SMOKE FAILED",e);endSmoke(false);}
    }

    private void endSmoke(boolean pass)
    {
        Smoke t=smoke;smoke=null;
        if(t.magical!=null) observation.end(t.magical.runId);
        try
        {
            for(Session s:new Session[]{t.physical,t.magical})
            {
                if(s==null) continue;
                if(s.runId>0) updateRun(s,pass?"SMOKE_PASS":"SMOKE_FAIL",true);
                try
                {
                    // Restore standard comparison sheets, not transient UD/TP/test-resource snapshots.
                    s.bot.abortCast();s.bot.stopAllEffects();
                    for(int[][] group:new int[][][]{COMMON,s.mage?MAGICAL:PHYSICAL})
                        for(int[] buff:group) SkillData.getInstance().getSkill(buff[0],buff[1]).applyEffects(s.bot,s.bot);
                    s.bot.setCurrentHpMp(s.bot.getMaxHp(),s.bot.getMaxMp());s.bot.setCurrentCp(s.bot.getMaxCp());
                    LabTelemetry.capturePilotStatsNow(s.bot);
                }
                finally {cleanup(s.bot,s);}
            }
        }
        finally
        {
            if(t.instanceId>0) InstanceManager.getInstance().destroyInstance(t.instanceId);
            SoloArenaGauntlet.releasePilot();
        }
        LOGGER.info("AI_SMOKE "+(pass?"SUCCESS 12/12":"FAILED")+": pilots unloaded; original characters untouched");
    }
    private static final class Smoke
    {
        Session physical,magical;int instanceId,stage;boolean pending;double before;long itemBefore,waitUntil;
        final long started=System.currentTimeMillis();
    }
    public static void main(String[] args) {new LabCombatPilots();}
}
