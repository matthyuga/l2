package custom.AmberContract;

import java.util.Map;
import java.util.ArrayList;
import java.util.List;
import java.sql.Connection;
import java.sql.PreparedStatement;
import org.l2jmobius.commons.database.DatabaseFactory;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Future;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.holders.ItemHolder;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogin;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogout;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.stats.Formulas;
import org.l2jmobius.gameserver.network.serverpackets.MagicSkillUse;
import org.l2jmobius.gameserver.network.serverpackets.SkillCoolTime;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import org.l2jmobius.gameserver.util.LocationUtil;

/** Private GM prototype. The contract owns only its temporary skills. */
public class AmberContract extends Script implements IVoicedCommandHandler
{
    public static final int NPC=902500, SUMMON=902501, MARKER=902502, SHOTS=6645;
    public static final int INVOKE=19001,FIRE=19002,RAIN=19003,BREAK=19004,FIRE_BUFF=19005;
    public static final int ASSIST=19014;
    static final int FIRE_INDICATOR=19011,RAIN_FALL_MS=650;
    public static final String CONTRACT="AMBER_CONTRACT_V1";
    static final Logger LOG=Logger.getLogger(AmberContract.class.getName());
    static final Map<Integer,Session> SESSIONS=new ConcurrentHashMap<>();
    static final int[] GRANTS={INVOKE,FIRE,RAIN,BREAK,ASSIST};
    static AmberContract instance;

    public AmberContract()
    {
        instance=this;addStartNpc(NPC);addTalkId(NPC);addFirstTalkId(NPC);
        VoicedCommandHandler.getInstance().registerHandler(this);
        Containers.Players().addListener(new ConsumerEventListener(Containers.Players(),EventType.ON_PLAYER_LOGIN,(OnPlayerLogin e)->ThreadPool.schedule(()->restore(e.getPlayer()),1000),this));
        Containers.Players().addListener(new ConsumerEventListener(Containers.Players(),EventType.ON_PLAYER_LOGOUT,(OnPlayerLogout e)->cleanup(e.getPlayer()),this));
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,(OnCreatureDamageDealt e)->{
            for(Player p:World.getPlayers())if(p.getSummon() instanceof AmberServitor a)
                a.assist.damaged(e.getAttacker(),e.getTarget(),e.getDamage());
        },this));
        ThreadPool.scheduleAtFixedRate(()->{
            for(Player p:World.getPlayers())if(p.getSummon() instanceof AmberServitor a)
                try{synchronized(session(p)){a.assist.tick();}}
                catch(RuntimeException e){LOG.log(java.util.logging.Level.WARNING,"Amber assist failed owner="+p.getName(),e);}
        },1500,500);
        ThreadPool.scheduleAtFixedRate(()->{
            for(Player p:World.getPlayers())if(contracted(p)&&p.isGM())restore(p);
        },5000,3000);
        LOG.info("AmberContract: GM quest, bow servitor with assist AI, fire and fixed 3500ms rain channel.");
    }
    public static boolean contracted(Player p){return p.getVariables().getBoolean(CONTRACT,false);}
    /** Actual restored HP/CP only; observing a heal never changes its effect or native PvP rules. */
    public static void notifyHealing(Creature healer,Creature recipient,double restored)
    {
        if(restored<=0||healer==null||recipient==null||healer==recipient||SESSIONS.isEmpty())return;
        for(int id:SESSIONS.keySet())
        {
            Player p=World.getPlayer(id);
            if(p!=null&&p.getSummon() instanceof AmberServitor a)
                try{a.assist.healed(healer,recipient,restored);}
                catch(RuntimeException e){LOG.log(java.util.logging.Level.WARNING,"Amber healing observation failed owner="+p.getName(),e);}
        }
    }
    /** Native toggle lifecycle; also rejects restored/stale effects without a live contract actor. */
    public static void assistEffect(Player p,boolean enabled)
    {
        synchronized(session(p))
        {
            AmberServitor a=p.getSummon() instanceof AmberServitor actor?actor:null;
            if(enabled&&(!p.isGM()||!contracted(p)||a==null||a.isDead()||!a.isSpawned()
                ||p.isDead()||p.isMounted()||p.isInDuel()||p.isInOlympiadMode()))
            {
                p.getEffectList().stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,ASSIST);
                p.sendMessage("Asistencia de Amber: invoca a Amber con un contrato vigente primero.");return;
            }
            if(a!=null)a.assist.setEnabled(enabled);
            p.sendMessage(enabled?"Amber: asistencia IA activada.":"Amber: asistencia IA desactivada; control manual.");
        }
    }
    static Session session(Player p){return SESSIONS.computeIfAbsent(p.getObjectId(),id->new Session());}
    static void grant(Player p)
    {
        boolean changed=false;
        for(int id:GRANTS)if(p.getKnownSkill(id)==null){p.addSkill(SkillData.getInstance().getSkill(id,1),false);changed=true;}
        if(changed){p.sendSkillList();syncCooldowns(p);}
    }
    static void restore(Player p){if(p.isGM()&&contracted(p))grant(p);}
    static void cleanup(Player p)
    {
        Session s=SESSIONS.get(p.getObjectId());if(s!=null)s.cancel();
        if(p.getSummon() instanceof AmberServitor a)a.unSummon(p);
        p.getEffectList().stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,ASSIST);
        p.getEffectList().stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,FIRE_INDICATOR);
        for(int id:GRANTS)if(p.getKnownSkill(id)!=null)p.removeSkill(p.getKnownSkill(id),false);
        SESSIONS.remove(p.getObjectId());
    }
    static void revokeSavedEffects(Player p)
    {
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("DELETE FROM character_summon_skills_save WHERE ownerId=? AND summonSkillId=?"))
        {q.setInt(1,p.getObjectId());q.setInt(2,INVOKE);q.executeUpdate();}
        catch(Exception e){LOG.log(java.util.logging.Level.WARNING,"Amber saved-effect cleanup failed",e);}
    }
    @Override public String onFirstTalk(Npc npc,Player p){menu(p,npc);return null;}
    @Override public String onTalk(Npc npc,Player p){menu(p,npc);return null;}
    @Override public String onEvent(String event,Npc npc,Player p)
    {
        if(npc==null||npc.getId()!=NPC||p.getInstanceId()!=npc.getInstanceId()||p.calculateDistance3D(npc)>250)return null;
        if(!p.isGM()){p.sendMessage("Contrato Amber: laboratorio GM por ahora.");return null;}
        if(event.equals("accept"))
        {
            if(p.isDead()||p.isInCombat()||p.isInOlympiadMode()||p.isInDuel()){p.sendMessage("Firma fuera de combate y de duelos.");return null;}
            p.getVariables().set(CONTRACT,true);p.getVariables().storeMe();grant(p);
            p.sendMessage("Contrato firmado: habilidades temporales de Amber disponibles.");
            if(!p.hasSummon())order(p,INVOKE);else p.sendMessage("Retira tu summon actual antes de invocar a Amber.");
        }
        else if(event.equals("break"))order(p,BREAK);
        menu(p,npc);return null;
    }
    @Override public String[] getCommandList(){return new String[]{"amber"};}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        if(!p.isGM()){p.sendMessage("Amber: laboratorio GM.");return true;}
        restore(p);
        String action=params==null?"":params.trim().toLowerCase(java.util.Locale.ROOT);
        switch(action){case "firmar"->{
            if(!(p.getTarget() instanceof Npc npc)||npc.getId()!=NPC||p.getInstanceId()!=npc.getInstanceId()||p.calculateDistance3D(npc)>250)
                p.sendMessage("Selecciona a Amber y acercate para firmar el contrato.");
            else onEvent("accept",npc,p);
        }case "toggle"->{
            if(p.getSummon() instanceof AmberServitor a&&contracted(p))a.assist.enable(!a.assist.enabled());
            else p.sendMessage("Invoca a Amber con contrato vigente primero.");
        }case "invocar"->order(p,INVOKE);case "fuego"->order(p,FIRE);case "lluvia"->order(p,RAIN);case "romper"->order(p,BREAK);
        case "auto","manual"->{control(p,action);menu(p);}
        case "atacar","seguir","detener","retirar"->control(p,action);default->menu(p);}
        return true;
    }
    static void menu(Player p){menu(p,null);}
    static void menu(Player p,Npc npc)
    {
        NpcHtmlMessage packet=new NpcHtmlMessage(npc==null?0:npc.getObjectId());packet.setHtml(menuHtml(p));p.sendPacket(packet);
    }
    static String menuHtml(Player p)
    {
        String html="<html><body><center><font color=LEVEL>Contrato con Amber</font><br>Arquera invocable | Prueba GM gratuita<br>";
        html+=contracted(p)?"Contrato vigente.<br>"+skillButton("Contract","Invocar Amber","invocar")
            +"<table width=280><tr><td width=36><img src=\"AmberAssistIconsV1.Assist\" width=32 height=32></td><td>Asistencia de Amber: activable (Alt+K)</td></tr></table>"
            +button("Activar asistencia IA","voice .amber auto")+button("Control manual","voice .amber manual")
            +button("Atacar al objetivo","voice .amber atacar")+button("Seguirme","voice .amber seguir")+button("Detener","voice .amber detener")
            +skillButton("Fire","Flechas de fuego","fuego")+skillButton("Rain","Lluvia de flechas","lluvia")
            +button("Retirar Amber","voice .amber retirar")+skillButton("Break","Romper contrato","romper"):"Habla conmigo en el Coliseo y firma.<br>"+skillButton("Contract","Firmar contrato e invocar","firmar");
        if(p.getSummon() instanceof AmberServitor a)
            html+="<br>Amber: "+(a.charging?"cargando lluvia":a.assist.status())+" | MP "+(int)a.getCurrentMp()+" / "+(int)a.getMaxMp()+"<br>";
        html+=button("Comparar modelos de Amber","voice .ambers")+"Beast Soulshots: "+p.getInventory().getInventoryItemCount(SHOTS,-1)+"<br>"
            +"Infinity Bow hero: solo visual.<br>Fuego: 60MP / +25% PAtk / 15s / recarga30s.<br>"
            +"Lluvia: potencia3000 por impacto.<br>120MP + 3 shots / carga3,5s.<br>Radio200 / 3 impactos / recarga45s.<br>"
            +"Invocada en manual. Asistencia de Amber:<br>un clic activa IA, otro la desactiva.<br>IA: protege al grupo y elige enemigos/summons.<br>Lluvia: controles > UD; evalua grupos y riesgo.<br>Detecta Anchor, Lightning y controles de cubics.<br>Concentra el area para cubrir mas enemigos.<br>Seguir/Detener apagan el activable.<br>Un summon a la vez; activa shots con clic derecho.<br>"
            +"Habilidades (Alt+K): arrastra los cinco iconos<br>a tu barra. Asistencia no consume MP.<br>"
            +"Romper revoca solo mis habilidades.<br>No regala arma ni shots.</center></body></html>";
        return html;
    }
    private static String button(String label,String action){return "<button value=\""+label+"\" action=\"bypass -h "+action+"\" width=280 height=21 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
    private static String skillButton(String icon,String label,String action)
    {
        return "<table width=280><tr><td width=36><img src=\"AmberIconsV1."+icon+"\" width=32 height=32></td>"
            +"<td><button value=\""+label+"\" action=\"bypass -h voice .amber "+action+"\" width=236 height=28 "
            +"back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\"></td></tr></table>";
    }
    static void control(Player p,String action)
    {
        try
        {
            if(!p.isGM()||!contracted(p))throw new IllegalStateException("Firma primero el contrato con Amber.");
            if(p.isDead()||p.isMounted()||p.isInDuel()||p.isInOlympiadMode())throw new IllegalStateException("No disponible en este estado.");
            if(!(p.getSummon() instanceof AmberServitor a)||a.isDead())throw new IllegalStateException("Invoca a Amber primero.");
            synchronized(session(p))
            {
                if(a.charging&&!action.equals("manual")&&!action.equals("auto"))throw new IllegalStateException("Amber esta cargando la lluvia; espera o rompe el contrato fuera de combate.");
                switch(action)
                {
                    case "auto"->a.assist.enable(true);
                    case "manual"->a.assist.enable(false);
                    case "atacar"->{if(a.canAttack(false))a.doSummonAttack(p.getTarget());}
                    case "seguir"->{a.abortAttack();a.cancelAction();a.stopMove(null);a.setFollowStatus(true);}
                    case "detener"->{a.abortAttack();a.cancelAction();a.setFollowStatus(false);a.stopMove(null);}
                    case "retirar"->{
                        if(p.isInCombat()||a.isInCombat()||a.isAttackingNow()||a.isCastingNow())throw new IllegalStateException("Retira a Amber fuera de combate.");
                        a.unSummon(p);p.sendMessage("Amber retirada; conservas el contrato y sus habilidades.");
                    }
                }
            }
        }
        catch(IllegalStateException e){p.sendMessage("Amber: "+e.getMessage());}
    }
    public static void order(Creature caster,int id)
    {executeOrder(caster,id,null,false);}
    static boolean automaticOrder(AmberServitor caster,int id,Creature target)
    {return executeOrder(caster,id,target,true);}
    private static boolean executeOrder(Creature caster,int id,Creature requestedTarget,boolean automatic)
    {
        Player p=caster.isSummon()?caster.asSummon().getOwner():caster.asPlayer();
        if(p==null)return false;
        try
        {
            if(!p.isGM()||!contracted(p))throw new IllegalStateException("Firma primero el contrato con Amber.");
            if(p.isDead()||p.isInOlympiadMode()||p.isInDuel()||p.isMounted())throw new IllegalStateException("No disponible en este estado.");
            Session s=session(p);
            synchronized(s)
            {
                if(id==BREAK)
                {
                    if(p.isInCombat()||p.isAttackingNow()||p.isCastingNow()&&caster!=p)throw new IllegalStateException("Rompe el contrato fuera de combate.");
                    p.getVariables().set(CONTRACT,false);p.getVariables().storeMe();cleanup(p);revokeSavedEffects(p);p.sendSkillList();p.sendMessage("Contrato roto: Amber y sus habilidades retiradas.");return true;
                }
                if(id==INVOKE)
                {
                    if(p.hasSummon())throw new IllegalStateException("Ya tienes un summon. Retiralo primero.");
                    cooldown(p,INVOKE,120000);
                    AmberServitor a=new AmberServitor(NpcData.getInstance().getTemplate(AmberModelVariants.templateId(p)),p);
                    a.setName("Amber");a.setTitle(p.getName());a.setReferenceSkill(INVOKE);a.setExpMultiplier(1);
                    a.setLifeTime(86400000);a.setItemConsume(new ItemHolder(0,0));a.setItemConsumeInterval(60000);a.setAttackRange(700);
                    a.setInstanceId(p.getInstanceId());a.fullRestore();a.setHeading(p.getHeading());p.setPet(a);a.spawnMe(p.getX()+35,p.getY()+35,p.getZ());a.setRunning();a.setFollowStatus(true);syncCooldowns(p);
                    p.sendMessage("Amber invocada en manual. Activa Asistencia de Amber desde Alt+K o tu barra. Beast Soulshots: clic derecho.");return true;
                }
                if(!(p.getSummon() instanceof AmberServitor a)||a.isDead())throw new IllegalStateException("Invoca a Amber primero.");
                if(caster.isSummon()&&caster!=a)throw new IllegalStateException("Esta orden pertenece a Amber.");
                if(!automatic)a.assist.manualSkill();
                if(automatic&&(p.isInvul()||!a.assist.enabled()))return false;
                if(a.isCastingNow()||a.isStunned()||a.isParalyzed()||a.isMuted())throw new IllegalStateException("Amber no puede usar esa habilidad ahora.");
                if(id==FIRE)
                {
                    if(a.getCurrentMp()<60)throw new IllegalStateException("Amber necesita60MP.");
                    cooldown(p,FIRE,30000);a.getStatus().reduceMp(60);SkillData.getInstance().getSkill(FIRE_BUFF,1).applyEffects(a,a);
                    SkillData.getInstance().getSkill(FIRE_INDICATOR,1).applyEffects(p,p);a.updateEffectIcons(true);
                    a.broadcastPacket(new MagicSkillUse(a,a,FIRE,1,0,30000));
                    if(!automatic)p.sendMessage("Flechas de fuego: 15s, PAtk +25%, ataque de fuego +20. Recarga: 30s.");return true;
                }
                if(id==RAIN)
                {
                    Creature target=automatic?requestedTarget:p.getTarget()==null?null:p.getTarget().asCreature();
                    String rejection=targetRejection(p,a,target,a.isForcedTarget(target));
                    if(rejection!=null)throw new IllegalStateException(rejection);
                    if(target.isDoor())throw new IllegalStateException("Contra puertas usa las flechas normales o las de fuego; la lluvia es para combatientes.");
                    if(a.calculateDistance3D(target)>900||!GeoEngine.getInstance().canSeeTarget(a,target))throw new IllegalStateException("El objetivo debe estar visible y a900 o menos de Amber.");
                    if(a.getCurrentMp()<120)throw new IllegalStateException("Amber necesita120MP.");
                    if(p.getInventory().getInventoryItemCount(SHOTS,-1)<3)throw new IllegalStateException("Necesitas3 Beast Soulshots para la lluvia.");
                    cooldown(p,RAIN,45000);
                    if(!p.destroyItemByItemId(ItemProcessType.NONE,SHOTS,3,a,true))throw new IllegalStateException("No se pudieron consumir los shots.");
                    a.getStatus().reduceMp(120);startRain(p,a,target,s);return true;
                }
            }
        }
        catch(RuntimeException e){if(!(e instanceof IllegalStateException))LOG.log(java.util.logging.Level.WARNING,"Amber order failed id="+id,e);if(!automatic)p.sendMessage("Amber: "+e.getMessage());}
        return false;
    }
    static void cooldown(Player p,int id,long duration)
    {
        String key="AMBER_REUSE_"+id;long now=System.currentTimeMillis(),until=p.getVariables().getLong(key,0);
        if(until>now)throw new IllegalStateException("Habilidad en recarga: "+((until-now+999)/1000)+"s.");
        p.getVariables().set(key,now+duration);p.getVariables().storeMe();
        syncCooldowns(p);
    }
    /** Keeps the authoritative persistent reuse and the native skill-bar clock in sync. */
    static void syncCooldowns(Player p)
    {
        long now=System.currentTimeMillis();
        for(int id:new int[]{INVOKE,FIRE,RAIN})
        {
            long until=p.getVariables().getLong("AMBER_REUSE_"+id,0);if(until<=now)continue;
            var skill=SkillData.getInstance().getSkill(id,1);long duration=id==INVOKE?120000:id==FIRE?30000:45000;
            p.addTimeStamp(skill,duration,until);p.disableSkill(skill,until-now);
            if(p.getSummon() instanceof AmberServitor a&&id!=INVOKE){a.addTimeStamp(skill,duration,until);a.disableSkill(skill,until-now);}
        }
        p.sendPacket(new SkillCoolTime(p));
    }
    static double attributeBonus(int power,int resistance)
    {
        // Same Interlude attribute curve as Formulas.calcAttributeBonus; preserves launch-time element power.
        int diff=power-resistance;if(diff==0)return 1;
        double magnitude=Math.sqrt(Math.pow(Math.abs((double)diff),3)/2)*0.0001;
        return diff>0?Math.min(1.025+magnitude,1.25):Math.max(0.975-magnitude,0.75);
    }
    static boolean validVictim(Player p,AmberServitor a,Creature t)
    {
        return targetRejection(p,a,t,a.isForcedTarget(t))==null;
    }
    static String targetRejection(Player p,AmberServitor a,Creature t,boolean force)
    {
        if(t==null)return "Selecciona un objetivo.";
        if(t==a||t==p)return "No puede atacarte a vos ni a ella misma.";
        if(t.isDead())return "El objetivo esta muerto.";
        if(t.isInvul())return "El objetivo es invulnerable; si es un piloto, espera el inicio del combate.";
        if(t.isInvisible())return "El objetivo no es visible.";
        if(t.getInstanceId()!=a.getInstanceId()||p.getInstanceId()!=a.getInstanceId())return "El objetivo esta en otra instancia.";
        if(p.isInsideZone(ZoneId.PEACE)||a.isInsideZone(ZoneId.PEACE)||t.isInsideZone(ZoneId.PEACE))return "No se puede atacar en una zona de paz.";
        if(t.isNpc()&&(t.asNpc().getId()==NPC||t.asNpc().getId()==MARKER))return "No ataca al NPC del contrato ni a los marcadores.";
        if(t instanceof org.l2jmobius.gameserver.entity.actor.instance.Door door)
            return custom.GiranSiegeLab.GiranRules.doorAllowed(p,door)?null:"Solo ataca puertas cerradas de un asedio activo donde sos atacante.";
        if(t instanceof org.l2jmobius.gameserver.entity.actor.instance.Defender||t instanceof org.l2jmobius.gameserver.entity.actor.Tower)
            return t.isAutoAttackable(p)?null:"Ese guardian o cristal pertenece al bando que defendes.";
        Player other=t.isSummon()?t.asSummon().getOwner():t.asPlayer();
        if(other!=null)
        {
            if(other==p)return "No ataca a tus otros summons.";
            if(p.isInsideZone(ZoneId.NO_PVP)||t.isInsideZone(ZoneId.NO_PVP))return "Esta zona no permite PvP.";
            if(p.isInDuel()||p.isInOlympiadMode()||other.isInDuel()||other.isInOlympiadMode())return "El contrato de prueba no participa en duelos ni Olimpiadas.";
            if(p.isInParty()&&other.isInParty()&&p.getParty()==other.getParty())return "No ataca a miembros de tu party.";
            if(p.isSiegeFriend(t))return "Es un aliado de asedio.";
            if(force||t.isAutoAttackable(p))return null;
            return "Ese jugador no es un blanco PvP automatico. Para ordenar un ataque forzado, usa Ctrl + Atacar del summon.";
        }
        return t.isAttackable()||t.isAutoAttackable(p)?null:"Ese NPC no es un objetivo de combate.";
    }
    static void flagRainAttack(Player p,Creature victim)
    {
        // Ordinary bow attacks already take this path in Creature.doAttack. Custom rain applies HP directly.
        p.updatePvPStatus(victim);
        if(victim.isFakePlayer()&&!org.l2jmobius.gameserver.config.custom.FakePlayersConfig.FAKE_PLAYER_AUTO_ATTACKABLE
            ||victim.isRaid()&&org.l2jmobius.gameserver.config.PvpConfig.FLAG_PLAYER_ON_RAID_ATTACK
            ||victim.isChampion()&&org.l2jmobius.gameserver.config.PvpConfig.FLAG_PLAYER_ON_CHAMPION_ATTACK)p.updatePvPStatus();
    }
    static void startRain(Player p,AmberServitor a,Creature target,Session s)
    {
        int x=target.getX(),y=target.getY(),z=target.getZ(),instanceId=a.getInstanceId();
        s.cancel();s.impacts=0;s.damage=0;s.hpDamage=0;s.cpDamage=0;
        s.marker=instance.addSpawn(MARKER,x,y,z,0,false,0,false,instanceId);
        if(s.marker==null)throw new IllegalStateException("No se pudo preparar la zona de lluvia.");
        s.marker.setInvul(true);
        a.abortAttack();a.setFollowStatus(false);a.stopMove(null);a.setHeading(LocationUtil.calculateHeadingFrom(a,target));
        a.charging=true;a.setCastingNow(true);s.charging=a;
        double launchPAtk=a.getPAtk(target);boolean fire=a.getEffectList().getBuffInfoBySkillId(FIRE_BUFF)!=null;
        byte launchElement=a.getAttackElement();int launchPower=a.getAttackElementValue(launchElement);
        a.broadcastPacket(new MagicSkillUse(a,a,RAIN,1,0,45000));
        a.broadcastPacket(new MagicSkillUse(a,s.marker,19010,1,0,0));
        a.broadcastPacket(new MagicSkillUse(a,a,19012,1,0,0));
        a.broadcastPacket(new MagicSkillUse(a,a,19006,1,3500,0));
        long started=System.currentTimeMillis();
        s.channel=ThreadPool.scheduleAtFixedRate(()->{
            synchronized(s)
            {
                if(!contracted(p)||p.getSummon()!=a||a.isDead()||p.isDead()||a.isStunned()||a.isParalyzed()||a.isMuted()||!a.isCastingNow()||a.getInstanceId()!=instanceId)
                {s.cancel();p.sendMessage("Lluvia interrumpida.");return;}
                if(System.currentTimeMillis()-started<3500)return;
                s.channel.cancel(false);s.channel=null;s.charging=null;a.charging=false;a.setCastingNow(false);a.getAI().notifyActionFinishCasting();
                a.setFollowStatus(true);
                s.rain=ThreadPool.scheduleAtFixedRate(new Runnable(){int pulse;
                    public void run(){synchronized(s){
                        if(!contracted(p)||p.getSummon()!=a||a.isDead()||p.isDead()||a.getInstanceId()!=instanceId){s.cancel();return;}
                        int visual=fire?19008:19007;Npc anchor=s.marker;
                        a.broadcastPacket(new MagicSkillUse(a,anchor,visual,pulse+1,0,0));
                        int volley=++pulse;
                        s.falling.add(ThreadPool.schedule(()->{synchronized(s){
                        if(!contracted(p)||p.getSummon()!=a||a.isDead()||p.isDead()||a.getInstanceId()!=instanceId||s.marker!=anchor)return;
                        World.forEachVisibleObjectInRange(anchor,Creature.class,250,victim->{
                            if(victim.isDoor()||!validVictim(p,a,victim)||Math.abs(victim.getZ()-z)>100||Math.hypot(victim.getX()-x,victim.getY()-y)>200||!GeoEngine.getInstance().canSeeTarget(a,victim))return;
                            double damage=rainDamage(a,victim,launchPAtk,launchElement,launchPower,Formulas.calcShldUse(a,victim));
                            a.sendDamageMessage(victim,(int)damage,false,false,false);
                            var rainSkill=SkillData.getInstance().getSkill(RAIN,1);
                            flagRainAttack(p,victim);
                            double hpBefore=victim.getCurrentHp(),cpBefore=victim.getCurrentCp();
                            victim.reduceCurrentHp(damage,a,rainSkill);
                            s.hpDamage+=Math.max(0,hpBefore-victim.getCurrentHp());s.cpDamage+=Math.max(0,cpBefore-victim.getCurrentCp());
                            // Match native attacks: HP application alone does not notify damage listeners.
                            victim.notifyDamageReceived(damage,a,rainSkill,false,false);
                            s.impacts++;s.damage+=damage;
                        });
                        if(volley==3){s.falling.clear();Npc finishedMarker=s.marker;s.marker=null;ThreadPool.schedule(()->finishedMarker.deleteMe(),1000);p.sendMessage("Lluvia de Amber: "+s.impacts+" impactos | CP: "+(int)s.cpDamage+" | HP: "+(int)s.hpDamage+".");LOG.info("AMBER_RAIN "+p.getName()+" fixed="+x+","+y+","+z+" fire="+fire+" impacts="+s.impacts+" damage="+s.damage+" hpLoss="+s.hpDamage+" cpLoss="+s.cpDamage);}
                        }},RAIN_FALL_MS));
                        if(pulse>=3){s.rain.cancel(false);s.rain=null;}
                    }}},0,500);
                p.sendMessage("Lluvia lanzada; Amber vuelve a moverse.");
            }
        },50,50);
    }
    static double rainDamage(AmberServitor a,Creature victim,double launchPAtk,byte launchElement,int launchPower,byte shield)
    {
        var skill=SkillData.getInstance().getSkill(RAIN,1);
        double damage=Formulas.calcPhysDam(a,victim,skill,shield,false,true);
        // A native perfect shield block remains one point, regardless of fire snapshots or added skill power.
        if(shield==Formulas.SHIELD_DEFENSE_PERFECT_BLOCK)return damage;
        double power=skill.getPower(a,victim,a.isPlayable()&&victim.isPlayable(),a.isPlayable()&&victim.isAttackable());
        damage*=(launchPAtk*2+power)/Math.max(1,a.getPAtk(victim)*2+power);
        return damage*attributeBonus(launchPower,victim.getDefenseElementValue(launchElement))/Formulas.calcAttributeBonus(a,victim,skill);
    }
    static final class Session
    {
        Future<?> channel,rain;final List<Future<?>> falling=new ArrayList<>();Npc marker;AmberServitor charging;int impacts;double damage,hpDamage,cpDamage;
        synchronized void cancel(){if(channel!=null)channel.cancel(false);if(rain!=null)rain.cancel(false);channel=rain=null;
            for(Future<?> hit:falling)hit.cancel(false);falling.clear();
            if(marker!=null){marker.deleteMe();marker=null;}
            if(charging!=null){AmberServitor a=charging;charging=null;a.charging=false;a.abortCast();a.setFollowStatus(true);} }
    }
    public static void main(String[] args){new AmberContract();}
}
