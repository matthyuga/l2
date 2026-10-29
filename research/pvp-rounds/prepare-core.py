from pathlib import Path
root=Path('E:/l2-local');stage=Path(__file__).resolve().parent
base=root/'source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver'
hook='org.l2jmobius.gameserver.managers.RoomCombatRules'
def edit(rel,old,new):
    source=(base/rel).read_text();assert source.count(old)==1,(rel,source.count(old))
    dest=stage/'src/org/l2jmobius/gameserver'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(source.replace(old,new))
edit('entity/actor/Player.java',
     '\t\t// Check if the attacker is not in the same party. NOTE:',
     f'\t\tfinal int roomDecision = {hook}.decision(attacker, this);\n\t\tif (roomDecision >= 0) return roomDecision == 1;\n\t\t// Check if the attacker is not in the same party. NOTE:')
p=stage/'src/org/l2jmobius/gameserver/entity/actor/Player.java'
text=p.read_text();old='\t\tif (!target.isPlayable())\n\t\t{\n\t\t\treturn true;\n\t\t}'
assert text.count(old)==1
text=text.replace(old,old+f'\n\t\tif (skill.isDamage() || skill.isDebuff() || skill.hasNegativeEffect())\n\t\t{{\n\t\t\tfinal int roomDecision = {hook}.decision(this, target.asPlayer());\n\t\t\tif (roomDecision >= 0) return roomDecision == 1;\n\t\t}}')
p.write_text(text)
edit('entity/actor/Creature.java','\tpublic void doAttack(Creature target)\n\t{',f'\tpublic void doAttack(Creature target)\n\t{{\n\t\tif ({hook}.decision(this, target) == 0) {{ sendPacket(org.l2jmobius.gameserver.network.serverpackets.ActionFailed.STATIC_PACKET); return; }}')
edit('entity/actor/status/PlayerStatus.java',
     '\t\tfinal Player player = getActiveChar();\n\t\tif (player.isDead())',
     f'\t\tfinal Player player = getActiveChar();\n\t\tif (!isHPConsumption && {hook}.decision(attacker, player) == 0) return;\n\t\tif (player.isDead())')
edit('mechanics/skill/Skill.java',
     '\tpublic void applyEffects(Creature effector, Creature effected, boolean self, boolean passive, boolean instant, int abnormalTime)\n\t{',
     f'\tpublic void applyEffects(Creature effector, Creature effected, boolean self, boolean passive, boolean instant, int abnormalTime)\n\t{{\n\t\tif (!self && (isDamage() || isDebuff() || hasNegativeEffect()) && {hook}.decision(effector, effected) == 0) return;')
edit('entity/actor/status/SummonStatus.java',
     '\t\tfinal Summon summon = getActiveChar();\n\t\tif ((attacker == null) || summon.isDead())',
     f'\t\tfinal Summon summon = getActiveChar();\n\t\tif (!isHPConsumption && {hook}.decision(attacker, summon) == 0) return;\n\t\tif ((attacker == null) || summon.isDead())')
p=stage/'src/org/l2jmobius/gameserver/mechanics/skill/Skill.java'
text=p.read_text();old='\tpublic void applyEffectScope(EffectScope effectScope, BuffInfo info, boolean applyInstantEffects, boolean addContinuousEffects)\n\t{'
assert text.count(old)==1
p.write_text(text.replace(old,old+f'\n\t\tif ((isDamage() || isDebuff() || hasNegativeEffect()) && {hook}.decision(info.getEffector(), info.getEffected()) == 0) return;'))
text=p.read_text();old='\t\t\t\tfinal Party party = player.getParty();'
assert text.count(old)==1
p.write_text(text.replace(old,f'\t\t\t\tfinal int roomDecision = {hook}.decision(caster, target);\n\t\t\t\tif (roomDecision >= 0) return roomDecision == 1 && GeoEngine.getInstance().canSeeTarget(caster, target);\n'+old))
print('Prepared five existing combat classes; originals remain unchanged.')
