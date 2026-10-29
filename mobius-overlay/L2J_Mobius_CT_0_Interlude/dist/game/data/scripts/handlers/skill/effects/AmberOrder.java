package handlers.skill.effects;
import custom.AmberContract.AmberContract;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.mechanics.conditions.Condition;
import org.l2jmobius.gameserver.mechanics.effects.AbstractEffect;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.util.StatSet;
public class AmberOrder extends AbstractEffect
{
    public AmberOrder(Condition attach,Condition apply,StatSet set,StatSet params){super(attach,apply,set,params);}
    @Override public boolean isInstant(){return true;}
    @Override public void onStart(Creature effector,Creature effected,Skill skill){AmberContract.order(effector,skill.getId());}
}
