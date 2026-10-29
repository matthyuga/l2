from pathlib import Path
import re,json,hashlib,shutil

root=Path(__file__).resolve().parents[3]
stage=Path(__file__).resolve().parent
backup=root/'backups/roster-startup-account-2026-10-10'
log=(root/'logs/game-stderr.log').read_text(errors='replace')
assert 'RosterSavedSubclass restored main: ArenaMyrentha savedSlot=2 main=110' in log
assert 'Roster Coliseo: 19 perfiles Player preparados' in log
assert 'No se preparo el perfil normal' not in log
smoke=re.search(r'GROUP_SMOKE PASS hits=(\d+) casts=(\d+) summon=(\w+)',log)
assert smoke,'Real 4vs4 smoke incomplete'
rel=Path('game/data/scripts/custom/NormalNpcRoster/NormalNpcRoster.java')
b=(root/'server'/rel).read_bytes()
for base in ('source/L2J_Mobius_CT_0_Interlude/dist','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist'):
    assert (root/base/rel).read_bytes()==b
assert hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest()=='c2f649806ee4248e5d9cc507ea36088d2799d12c6dc4b61c20d0500111d0d888'
proof=json.loads((root/'research/client-comfort/v2/installed-client.json').read_text())
for name,sha in proof.items():
    p=root.parent/'l2'/('systextures' if name.endswith('.utx') else 'system-hud')/name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
shutil.copy2(root/'logs/game-stderr.log',backup/'roster19-group-smoke-pass.log')
report={'roster_prepared':19,'saved_subclass_recovery':'ArenaMyrentha slot2 -> existing main110','group_smoke':'PASS','hits':int(smoke[1]),'casts':int(smoke[2]),'summon':smoke[3]=='true','core_unchanged':True,'client_unchanged':True,'account_login':'hellkevin','account_report':'account-migration-verification.json'}
(stage/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
