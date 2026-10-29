from pathlib import Path
import shutil,json,hashlib,datetime
r=Path('E:/l2-local'); work=Path(__file__).resolve().parent
src=work/'src/custom/ElvenPvpRoom';src.mkdir(parents=True,exist_ok=True)
runtime=r/'server/game/data/scripts/custom/ElvenPvpRoom'
brain=(runtime/'PvpSiegeBrain.java').read_text()
brain=brain.replace('public static void forget(Player p){STATES.remove(p);}', 'public static void forget(Player p){STATES.remove(p);PvpSiegeCombat.forget(p);}')
brain=brain.replace('  p.setRunning();State s=', '  PvpSiegeCombat.maintain(p);p.setRunning();State s=')
brain=brain.replace('  Player patient=p;', '  if(PvpSiegeCombat.summon(p))return;\n  PvpSiegeCombat.orderSummon(p,enemy);\n  Player patient=p;')
brain=brain.replace('if(!ally.isDead()&&', 'if(PvpSiegeRoster.owned(ally)&&!ally.isDead()&&')
brain=brain.replace('  boolean bow=', '''  for(Skill skill:p.getAllSkills().stream().filter(k->k.isDamage()&&!k.isAOE()&&!k.isSuicideAttack()&&!k.isToggle()&&!k.isPassive()&&(!p.isMageClass()||k.isMagic())).sorted(Comparator.comparingInt(Skill::getId)).toList())if(cast(p,skill,enemy,s,now))return;
  boolean bow=''',1)
brain=brain.replace('  if(p.getAI().getIntention()!=Intention.ATTACK', '''  if(p.isMageClass()){p.abortAttack();if(p.getAI().getIntention()==Intention.ATTACK)p.getAI().setIntentionActive();return;}
  PvpSiegeCombat.shot(p,false);
  if(p.getAI().getIntention()!=Intention.ATTACK''',1)
brain=brain.replace('p.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume())', 'p.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume()||p.getCurrentHp()<=skill.getHpConsume())')
brain=brain.replace('Math.max(40,skill.getCastRange())','Math.max(40,skill.getCastRange()<0?skill.getAffectRange():skill.getCastRange())')
brain=brain.replace('  boolean success=p.useMagic', '  PvpSiegeCombat.shot(p,skill.isMagic());\n  boolean success=p.useMagic')
brain=brain.replace('if(success)state.castAt=now+1_200_000_000L;', 'if(success){state.castAt=now+1_200_000_000L;PvpSiegeCombat.castAccepted(p,skill);}')
(src/'PvpSiegeBrain.java').write_text(brain)
roster=(runtime/'PvpSiegeRoster.java').read_text().replace('  p.fullRestore();p.setRunning();','  PvpSiegeCombat.stock(p);p.fullRestore();p.setRunning();')
(src/'PvpSiegeRoster.java').write_text(roster)
for p in runtime.glob('*.java'):
 if not (src/p.name).exists():shutil.copy2(p,src/p.name)
print('Prepared combat correction; production files untouched.')
