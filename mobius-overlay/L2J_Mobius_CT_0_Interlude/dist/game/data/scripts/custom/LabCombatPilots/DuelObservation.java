package custom.LabCombatPilots;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;

/** Observations, NOT inferred resist/cancel causes. Scoped to manual .ia runs. */
final class DuelObservation
{
    private static final Logger LOGGER=Logger.getLogger(DuelObservation.class.getName());
    private final ArrayBlockingQueue<Row> queue=new ArrayBlockingQueue<>(4096);
    private final Map<Integer,Set<String>> previous=new HashMap<>();
    private boolean ready;
    private long run,dropped;

    DuelObservation()
    {
        try(Connection con=DatabaseFactory.getConnection();var st=con.createStatement())
        {
            st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_duel_observations (observation_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,run_id BIGINT UNSIGNED NOT NULL,observed_ms BIGINT UNSIGNED NOT NULL,actor_id INT NOT NULL,actor_name VARCHAR(45) NOT NULL,owner_id INT NOT NULL,event_name VARCHAR(24) NOT NULL,detail_text TEXT NOT NULL,hp DOUBLE NOT NULL,max_hp DOUBLE NOT NULL,cp DOUBLE NOT NULL,max_cp DOUBLE NOT NULL,mp DOUBLE NOT NULL,max_mp DOUBLE NOT NULL,world_x INT NOT NULL,world_y INT NOT NULL,world_z INT NOT NULL,target_id INT NOT NULL,is_casting BOOLEAN NOT NULL,is_dead BOOLEAN NOT NULL,KEY idx_run_time(run_id,observed_ms)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            ready=true;
            ThreadPool.scheduleAtFixedRate(this::flush,1000,1000);
        }
        catch(Exception e) {LOGGER.log(Level.SEVERE,"Duel observations unavailable",e);}
    }

    void begin(long id)
    {
        if(!ready) throw new IllegalStateException("No observation schema; manual AI not started");
        run=id;previous.clear();dropped=0;
    }

    void sample(long id,Player bot,Player player)
    {
        if(!ready || id!=run) return;
        List<Creature> actors=new ArrayList<>();
        if(bot!=null) {actors.add(bot);if(bot.hasSummon()) actors.add(bot.getSummon());}
        if(player!=null && player!=bot) {actors.add(player);if(player.hasSummon()) actors.add(player.getSummon());}
        Set<Integer> present=new HashSet<>();
        for(Creature actor:actors)
        {
            present.add(actor.getObjectId());
            Set<String> effects=new HashSet<>();
            for(var info:actor.getEffectList().getEffects())
                effects.add(info.getSkill().getId()+":"+info.getSkill().getLevel()+":"+(info.getEffector()==null?0:info.getEffector().getObjectId()));
            Set<String> old=previous.put(actor.getObjectId(),effects);
            if(old==null) offer(row(id,actor,"ACTOR_SEEN","baseline="+String.join(",",effects)));
            else
            {
                for(String effect:effects) if(!old.contains(effect)) offer(row(id,actor,"EFFECT_APPEARED",effect));
                for(String effect:old) if(!effects.contains(effect)) offer(row(id,actor,"EFFECT_DISAPPEARED",effect));
            }
            String flags="silenced="+actor.isMuted()+";rooted="+actor.isRooted()+";stunned="+actor.isStunned();
            if(actor.isPlayer()) flags+=";cubics="+actor.asPlayer().getCubics().keySet();
            offer(row(id,actor,"STATE",flags));
        }
        for(Integer idGone:new HashSet<>(previous.keySet()))
            if(!present.contains(idGone))
            {
                previous.remove(idGone);
                offer(new Row(id,System.currentTimeMillis(),idGone,"",0,"ACTOR_NOT_VISIBLE","not a death/resurrection assertion",0,0,0,0,0,0,0,0,0,0,false,false));
            }
    }

    void end(long id)
    {
        if(dropped>0) LOGGER.warning("Duel observation run="+id+" dropped="+dropped+"; incomplete evidence");
        previous.clear();run=0;
    }
    private Row row(long id,Creature actor,String event,String detail)
    {
        int owner=actor.isSummon()?actor.asSummon().getOwner().getObjectId():actor.getObjectId();
        return new Row(id,System.currentTimeMillis(),actor.getObjectId(),actor.getName(),owner,event,detail,
            actor.getCurrentHp(),actor.getMaxHp(),actor.getCurrentCp(),actor.getMaxCp(),actor.getCurrentMp(),actor.getMaxMp(),
            actor.getX(),actor.getY(),actor.getZ(),actor.getTarget()==null?0:actor.getTarget().getObjectId(),actor.isCastingNow(),actor.isDead());
    }
    private void offer(Row row) {if(!queue.offer(row)) dropped++;}
    private void flush()
    {
        List<Row> rows=new ArrayList<>(512);queue.drainTo(rows,512);
        if(rows.isEmpty()) return;
        try(Connection con=DatabaseFactory.getConnection();PreparedStatement ps=con.prepareStatement(
            "INSERT INTO lab_duel_observations (run_id,observed_ms,actor_id,actor_name,owner_id,event_name,detail_text,hp,max_hp,cp,max_cp,mp,max_mp,world_x,world_y,world_z,target_id,is_casting,is_dead) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"))
        {
            for(Row r:rows)
            {
                ps.setLong(1,r.run);ps.setLong(2,r.time);ps.setInt(3,r.actor);ps.setString(4,r.name);ps.setInt(5,r.owner);ps.setString(6,r.event);ps.setString(7,r.detail);
                ps.setDouble(8,r.hp);ps.setDouble(9,r.maxHp);ps.setDouble(10,r.cp);ps.setDouble(11,r.maxCp);ps.setDouble(12,r.mp);ps.setDouble(13,r.maxMp);
                ps.setInt(14,r.x);ps.setInt(15,r.y);ps.setInt(16,r.z);ps.setInt(17,r.target);ps.setBoolean(18,r.casting);ps.setBoolean(19,r.dead);ps.addBatch();
            }
            ps.executeBatch();
        }
        catch(Exception e) {LOGGER.log(Level.SEVERE,"Lost "+rows.size()+" duel observations; incomplete evidence",e);}
    }
    private record Row(long run,long time,int actor,String name,int owner,String event,String detail,double hp,double maxHp,double cp,double maxCp,double mp,double maxMp,int x,int y,int z,int target,boolean casting,boolean dead) {}
}
