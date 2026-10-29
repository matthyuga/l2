from pathlib import Path
import shutil

root = Path('E:/l2-local')
src = root / 'source/L2J_Mobius_CT_0_Interlude'
java = src / 'java/org/l2jmobius/gameserver'
backup = root / 'backups/direct-threat-2026-10-12'

def edit(path, old, new):
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, (path, old[:90], text.count(old))
    dest = backup / path.relative_to(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists(): shutil.copy2(path, dest)
    path.write_text(text.replace(old, new), encoding='utf-8', newline='\n')

creature = java / 'entity/actor/Creature.java'
edit(creature, 'import org.l2jmobius.gameserver.entity.actor.tasks.creature.HitTask;', 'import org.l2jmobius.gameserver.entity.actor.tasks.creature.HitTask;\nimport org.l2jmobius.gameserver.mechanics.DirectThreat;')
edit(creature, 'new HitTask(this, target, damage1, crit1, miss1, shld1, attack.hasSoulshot(), rechargeShots)', 'new HitTask(this, target, damage1, crit1, miss1, shld1, attack.hasSoulshot(), rechargeShots, rechargeShots)')
edit(creature, 'new MagicUseTask(this, targets, skill, skillTime, simultaneously)', 'new MagicUseTask(this, targets, skill, skillTime, simultaneously, target)')
edit(creature, 'callSkill(mut.getSkill(), mut.getTargets());', '''try (var threat = DirectThreat.begin(this, mut.getPrimaryTarget(), mut.getSkill()))
			{
				callSkill(mut.getSkill(), mut.getTargets());
			}''')

hit = java / 'entity/actor/tasks/creature/HitTask.java'
edit(hit, 'import org.l2jmobius.gameserver.entity.actor.Creature;', 'import org.l2jmobius.gameserver.entity.actor.Creature;\nimport org.l2jmobius.gameserver.mechanics.DirectThreat;')
edit(hit, 'private final boolean _rechargeShots;', 'private final boolean _rechargeShots;\n\tprivate final boolean _primary;')
edit(hit, '''		_creature = creature;
		_hitTarget = target;''', '''		this(creature, target, damage, crit, miss, shld, soulshot, rechargeShots, true);
	}

	public HitTask(Creature creature, Creature target, int damage, boolean crit, boolean miss, byte shld, boolean soulshot, boolean rechargeShots, boolean primary)
	{
		_primary = primary;
		_creature = creature;
		_hitTarget = target;''')
edit(hit, '_creature.onHitTimer(_hitTarget, _damage, _crit, _miss, _shld, _soulshot, _rechargeShots);', '''try (var threat = DirectThreat.begin(_creature, _primary ? _hitTarget : null, null))
			{
				_creature.onHitTimer(_hitTarget, _damage, _crit, _miss, _shld, _soulshot, _rechargeShots);
			}''')

magic = java / 'entity/actor/tasks/creature/MagicUseTask.java'
edit(magic, 'private final Creature _creature;', 'private final Creature _creature;\n\tprivate final Creature _primaryTarget;')
edit(magic, '''		_creature = creature;
		_targets = targets;''', '''		this(creature, targets, s, hit, simultaneous, null);
	}

	public MagicUseTask(Creature creature, List<WorldObject> targets, Skill s, int hit, boolean simultaneous, Creature primaryTarget)
	{
		_primaryTarget = primaryTarget;
		_creature = creature;
		_targets = targets;''')
edit(magic, '\tpublic int getCount()', '\tpublic Creature getPrimaryTarget()\n\t{\n\t\treturn _primaryTarget;\n\t}\n\n\tpublic int getCount()')

player = java / 'entity/actor/Player.java'
edit(player, 'public class Player extends Playable\n{', '''public class Player extends Playable
{
	private volatile org.l2jmobius.gameserver.mechanics.DirectThreat.Entry _lastDirectThreat;

	public org.l2jmobius.gameserver.mechanics.DirectThreat.Entry getLastDirectThreat()
	{
		return _lastDirectThreat;
	}

	public void setLastDirectThreat(org.l2jmobius.gameserver.mechanics.DirectThreat.Entry entry)
	{
		_lastDirectThreat = entry;
	}
''')
edit(player, '''		// Kill the Player.
		if (!super.doDie(killer))''', '''		// Kill the Player.
		if (!super.doDie(killer))''')
# Clear only after a successful death, and on removal from the world.
edit(player, '''		if (!super.doDie(killer))
		{
			return false;
		}''', '''		if (!super.doDie(killer))
		{
			return false;
		}
		_lastDirectThreat = null;''')
edit(player, 'public boolean deleteMe()\n\t{', 'public boolean deleteMe()\n\t{\n\t\t_lastDirectThreat = null;')

status = java / 'entity/actor/status/PlayerStatus.java'
edit(status, 'import org.l2jmobius.gameserver.mechanics.script.QuestState;', 'import org.l2jmobius.gameserver.mechanics.script.QuestState;\nimport org.l2jmobius.gameserver.mechanics.DirectThreat;')
edit(status, '\t\t\t// Check and calculate transfered damage.', '''			// Record only accepted direct damage, before CP/MP/servitor absorption.
			DirectThreat.onDamage(player, attacker, value, isDOT, isHPConsumption);

			// Check and calculate transfered damage.''')

for base in [src / 'dist/game/data/scripts', root / 'server/game/data/scripts']:
    handler = base / 'handlers/MasterHandler.java'
    edit(handler, 'import handlers.chat.commands.voiced.SquadCommand;', 'import handlers.chat.commands.voiced.SquadCommand;\nimport handlers.chat.commands.voiced.ThreatCommand;')
    edit(handler, '\t\t\tSquadCommand.class,', '\t\t\tSquadCommand.class,\n\t\t\tThreatCommand.class,')

print('Core and handler hooks patched; backups:', backup)
