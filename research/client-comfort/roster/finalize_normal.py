from pathlib import Path
import re,json,shutil

root=Path(__file__).resolve().parents[3]
stage=Path(__file__).resolve().parent
backup=root/'backups/roster-startup-account-2026-10-10'
log=(root/'logs/game-stderr.log').read_text(errors='replace')
assert 'Roster Coliseo: 19 perfiles Player preparados' in log
assert 'RosterHybridReload PASS ArenaMyrentha' in log
assert 'No se preparo el perfil normal' not in log
arena=re.search(r'ArenaSpawnVerification SUCCESS: (\d+) checks',log)
assert arena and 'ArenaSpawnVerification FAILED' not in log
report=json.loads((stage/'verification.json').read_text())
report.update(final_roster_prepared=19,arena_spawn_checks=int(arena[1]),arena_spawn='PASS',game_pid=int((root/'run/game.pid').read_text().strip()),final_mode='Normal gameplay; group smoke disabled, one-shot arena verification finished')
(stage/'verification.json').write_text(json.dumps(report,indent=2))
shutil.copy2(root/'logs/game-stderr.log',backup/'normal-roster19-arena-pass.log')
doc=root/'COMBATES-ROSTER-ARRANQUE-CUENTA.md'
s='\n'.join(line for line in doc.read_text().split('\n') if not line.startswith('Estado:'))
s+='\nResultado: 19/19 perfiles preparados en ambos arranques; Myrentha recuperada desde sub2 y luego verificada de nuevo con sus cuatro clases. 4vs4 PASS con151 impactos,225 usos de habilidades y summons. ArenaSpawnVerification PASS con'+str(arena[1])+' comprobaciones: los19 rivales bajo demanda, cancelacion, victoria, siguiente ronda, derrota y desconexion. Cuenta hellkevin y nuevo hash de contrasena verificados; mismo ID y datos de Hellkevin. Cliente y core sin cambios.\n\nArranque final: ensayo grupal desactivado; comprobacion de arena de una sola ejecucion terminada y sus probes retirados. El servidor queda libre para jugar. Los siguientes arranques con 2-JUGAR utilizan las banderas normales de Start-L2Local.ps1.\n'
doc.write_text(s)
for rel in ('CONTINUIDAD-W10/27_COMBATES_ROSTER_CUENTA_2026-10-10.md','CONTINUIDAD-W11/27_COMBATES_ROSTER_CUENTA_2026-10-10.md','cloud-repo/docs/COMBATES-ROSTER-ARRANQUE-CUENTA.md','cloud-repo/CONTINUIDAD-W10/27_COMBATES_ROSTER_CUENTA_2026-10-10.md','cloud-repo/CONTINUIDAD-W11/27_COMBATES_ROSTER_CUENTA_2026-10-10.md'):
    shutil.copy2(doc,root/rel)
for folder in ('CONTINUIDAD-W10','CONTINUIDAD-W11'):
    p=root/folder/'LEER-PRIMERO.md'
    addition='\n## Combates y cuenta - 10/10/2026\n\nVer `27_COMBATES_ROSTER_CUENTA_2026-10-10.md`: recuperacion de subclase guardada en roster,19/19 listos,4vs4 y arena bajo demanda PASS. La cuenta de Hellkevin ahora se llama `hellkevin`; misma identidad y progreso, contrasena cambiada a pedido del usuario. Copias privadas de la migracion solo en backups locales, sin credenciales en Nexus/cloud.\n'
    if '27_COMBATES_ROSTER_CUENTA_2026-10-10.md' not in p.read_text():p.write_text(p.read_text()+addition)
    shutil.copy2(p,root/'cloud-repo'/folder/'LEER-PRIMERO.md')
cloud=root/'cloud-repo/research/client-comfort/roster';cloud.mkdir(parents=True,exist_ok=True)
for name in ('verification.json','restart_server.ps1','finalize.py','finalize_normal.py'):shutil.copy2(stage/name,cloud/name)
shutil.copy2(root/'research/client-comfort/rename_account.py',root/'cloud-repo/research/client-comfort/rename_account.py')
note='FINALIZADO: combates reparados y cuenta solo -> hellkevin, misma identidad/progreso, nueva contrasena a pedido (no guardar credenciales aqui). NormalNpcRoster normaliza sub activa valida antes de validar main; ArenaMyrentha era111 sub2/base110. Dos arranques19/19 PASS. Group smoke151hits225casts summontrue; arena spawn'+str(arena[1])+' checks PASS. Produccion soloNormalNpcRoster; Amber/core/cliente intactos. Runtime/source/cloud sincronizados. Backup roster-startup-account-2026-10-10 incluye filas privadas pre-migracion; no copiar dumps/hash a cloud. Continuidad27 y COMBATES-ROSTER-ARRANQUE-CUENTA.md. Servidor libre, group smoke false y verificacion one-shot arena acabada. Sin commit/push.\n'
Path('K:/_CodexNexus/inbox/20261010-lineage2-roster-account-fixed.md').write_text(note)
Path('K:/_CodexNexus/inbox/20261010-lineage2-roster-repair-in-progress.md').write_text('FINALIZADO; ventana liberada. Ver 20261010-lineage2-roster-account-fixed.md.\n')
session=Path('K:/_CodexNexus/sessions/lineage2-local.md')
if session.exists() and '20261010-lineage2-roster-account-fixed.md' not in session.read_text():session.write_text(session.read_text()+'\n10/10/2026: combates disponibles otra vez,19/19 preparados. Corregida sub activa persistida del perfil ArenaMyrentha. Pruebas4vs4 y arena PASS. Cuenta del usuario ahora `hellkevin`, mismos personajes y progreso; detalles sin credenciales en inbox/20261010-lineage2-roster-account-fixed.md y continuidad27.\n')
print(json.dumps(report,indent=2))
