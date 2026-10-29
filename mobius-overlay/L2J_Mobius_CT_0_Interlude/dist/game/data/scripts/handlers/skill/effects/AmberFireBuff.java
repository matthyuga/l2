package handlers.skill.effects;

import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.mechanics.conditions.Condition;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType;
import org.l2jmobius.gameserver.util.StatSet;

/** Amber's elemental enchant; its owner's timer is informational and has no stats. */
public class AmberFireBuff extends Buff
{
    public AmberFireBuff(Condition attach,Condition apply,StatSet set,StatSet params){super(attach,apply,set,params);}
    @Override public void onExit(Creature effector,Creature effected,Skill skill)
    {
        if(effected.isSummon()&&effected.getId()==902501)
            effected.asSummon().getOwner().getEffectList().stopSkillEffects(SkillFinishType.REMOVED,19011);
    }
}
