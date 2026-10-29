from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1];project=root.parent.parent
stage=root/'exports/contract/combat-vfx-v10'
baseline={}
for name in ['AmberContract.java','AmberContractVerification.java']:
 rel=Path('server/game/data/scripts/custom/AmberContract')/name
 source=project/rel;baseline[rel.as_posix()]=hashlib.sha256(source.read_bytes()).hexdigest()
 text=source.read_text()
 if name=='AmberContract.java':
  old='a.sendDamageMessage(victim,(int)damage,false,false,false);victim.reduceCurrentHp(damage,a,SkillData.getInstance().getSkill(RAIN,1));'
  new='''a.sendDamageMessage(victim,(int)damage,false,false,false);
                            var rainSkill=SkillData.getInstance().getSkill(RAIN,1);
                            victim.reduceCurrentHp(damage,a,rainSkill);
                            // Match native attacks: HP application alone does not notify damage listeners.
                            victim.notifyDamageReceived(damage,a,rainSkill,false,false);'''
  assert old in text;text=text.replace(old,new)
 else:
  imports='''import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
'''
  text=text.replace('import java.sql.Connection;',imports+'import java.sql.Connection;')
  text=text.replace('Player p=null,t=null;Npc npc=null;int instanceId=0;','Player p=null,t=null;Npc npc=null;int instanceId=0;ConsumerEventListener rainListener=null;')
  old='a.fullRestore();long shots='
  new='''final AmberServitor observedAttacker=a;final Player observedTarget=t;
            var rainEvents=new java.util.concurrent.atomic.AtomicInteger();
            var rainEventDamage=new java.util.concurrent.atomic.DoubleAdder();
            rainListener=new ConsumerEventListener(Containers.Global(),EventType.ON_CREATURE_DAMAGE_DEALT,(OnCreatureDamageDealt event)->{
                if(event.getAttacker()==observedAttacker&&event.getTarget()==observedTarget&&event.getSkill()!=null&&event.getSkill().getId()==AmberContract.RAIN){
                    rainEvents.incrementAndGet();rainEventDamage.add(event.getDamage());
                }
            },this);
            Containers.Global().addListener(rainListener);
            a.fullRestore();long shots='''
  assert old in text;text=text.replace(old,new)
  old='check(session.impacts==3&&session.damage>0,"Three actual Player impacts");'
  new=old+'''
            check(rainEvents.get()==3&&Math.abs(rainEventDamage.sum()-session.damage)<0.001,"Each rain hit notifies the global damage-number listener exactly once with Amber as attacker");
            Containers.Global().removeListener(rainListener);rainListener=null;'''
  assert old in text;text=text.replace(old,new)
  text=text.replace('if(npc!=null)npc.deleteMe();','if(rainListener!=null)Containers.Global().removeListener(rainListener);\n            if(npc!=null)npc.deleteMe();')
 dest=stage/'server/custom/AmberContract'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
(stage/'server-baseline.json').write_text(json.dumps(baseline,indent=2))
print('Server fix staged; global damage event follows the native attack order, with an opt-in integration assertion.')
