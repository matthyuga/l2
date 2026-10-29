package handlers.skill.effects;

import custom.AmberContract.AmberContract;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.mechanics.conditions.Condition;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.util.StatSet;

/** The native owner toggle is the single source of Amber's assistance state. */
public class AmberAssistToggle extends Buff
{
    public AmberAssistToggle(Condition attach,Condition apply,StatSet set,StatSet params){super(attach,apply,set,params);}
    @Override public void onStart(Creature effector,Creature effected,Skill skill)
    {
        if(effected.isPlayer())AmberContract.assistEffect(effected.asPlayer(),true);
    }
    @Override public void onExit(Creature effector,Creature effected,Skill skill)
    {
        if(effected.isPlayer())AmberContract.assistEffect(effected.asPlayer(),false);
    }
}
