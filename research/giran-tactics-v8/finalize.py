from pathlib import Path
import hashlib, json, re, shutil

r = Path(__file__).resolve().parents[2]
s = Path(__file__).resolve().parent
b = r / 'backups/giran-tactics-v8-2026-10-11'
log = (r / 'logs/game-stderr.log').read_text(encoding='utf-8', errors='replace')
match = re.search(r'GIRAN_V8_VERIFY PASS checks=(\d+);([^\r\n]+)', log)
assert match and 'GIRAN_V8_VERIFY FAILED' not in log, 'Native verification not complete'
tags = ['GIRAN_V6_WALK_PASS', 'GIRAN_V6_RETURN_PASS', 'GIRAN_V8_SERVICES_PASS',
        'GIRAN_V8_COMBAT_PASS', 'GIRAN_V8_TRUCES_PASS', 'GIRAN_V8_COORDINATION_PASS']
assert all(tag in log for tag in tags)
before = json.loads((b / 'before.json').read_text())
after = json.loads((b / 'after.json').read_text())
for key in ['human', 'inventory', 'clans', 'skills', 'castle', 'guards']:
    assert before[key] == after[key], key
assert len(after['pilots']) == 19 and all(p['level'] == 80 and p['online'] == 0 for p in after['pilots'])
assert len(after['siege']) == 4 and all(int(row['type']) == 1 for row in after['siege'])
installed = json.loads((s / 'installed.json').read_text(encoding='utf-8-sig'))
baseline = json.loads((s / 'baseline.json').read_text())
for key, sha in installed.items():
    relative = ('server/libs/GameServer.jar' if key == 'GameServer.jar' else
                'server/game/data/' + key if key.startswith('geodata/') else
                'server/game/data/stats/npcs/custom/' + key[5:] if key.startswith('npcs/') else
                'server/game/data/scripts/custom/' + key)
    assert hashlib.sha256((r / relative).read_bytes()).hexdigest().lower() == sha.lower(), key
unchanged = ['GameServer.jar', 'geodata/23_22.l2j', 'npcs/giran_lab_guardians.xml',
             'GiranSiegeLab/GiranGuardianAI.java', 'GiranSiegeLab/GiranGuardianBrain.java',
             'GiranSiegeLab/GiranGuardians.java', 'GiranSiegeLab/GiranRules.java',
             'GiranSiegeLab/GiranOrders.java', 'GiranSiegeLab/GiranRoster.java']
for key in unchanged:
    assert installed[key].lower() == baseline[key].lower(), key
proof = {
    'native_checks': int(match[1]), 'native_result': match[0],
    'proofs': [line for line in log.splitlines() if any(tag in line for tag in tags)],
    'unchanged': {key: installed[key].lower() for key in unchanged},
    'persistence': 'Hellkevin/inventory,clans/skills/reputation/blood,castle/owner/schedule,guards preserved; four rival attackers registered;19 pilots offline80',
    'limits': ['Controlled native fixtures prove target selection, damage, temporary truces and access; full siege balance needs a player trial.',
               'Native engraving starts and is aborted; verification never completes conquest.',
               'Truces affect bot decisions, not native PvP legality or alliances; they do not create damage immunity.']
}
(s / 'verification.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
shutil.copy2(r / 'logs/game-stderr.log', b / 'native-tactics-pass.log')
for p in (r / 'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    for folder in [r / 'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab',
                   r / 'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab']:
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, folder / p.name)
doc = r / 'GIRAN-IA-TREGUAS-Y-SERVICIOS-V8.md'
t = doc.read_text(encoding='utf-8').replace(
    'Preparado y compilado; validación nativa pendiente.',
    f'Instalado y validado: **{match[1]} comprobaciones nativas PASS**; GameServer listo para jugar.')
t = t.replace('Pruebas previstas:', 'Pruebas nativas PASS:')
t += '\nPersistencia PASS: Hellkevin/inventario, clanes/skills/reputación, propietario/fecha de Giran y guardias conservados; cuatro rivales registrados y19 pilotos offline nivel80. Core, geodata, órdenes/alianzas y guardianes V7 sin cambios. Runtime/source/cloud sincronizados, sin commit ni push.\n'
doc.write_text(t, encoding='utf-8')
(r / 'cloud-repo/docs').mkdir(exist_ok=True)
shutil.copy2(doc, r / 'cloud-repo/docs' / doc.name)
for folder in ['CONTINUIDAD-W10', 'CONTINUIDAD-W11']:
    dest = r / folder / '39_GIRAN_IA_TREGUAS_Y_SERVICIOS_V8_2026-10-11.md'
    shutil.copy2(doc, dest)
    index = r / folder / 'LEER-PRIMERO.md'
    if index.exists() and dest.name not in index.read_text(encoding='utf-8-sig'):
        with index.open('a', encoding='utf-8') as f:
            f.write('\n- ' + dest.name + ': amenazas por piloto, treguas tácticas y vendedor/buffer en el trono; prueba nativa PASS.\n')
cloud = r / 'cloud-repo/research/giran-tactics-v8'
for p in s.rglob('*'):
    if p.is_file() and p.suffix in {'.java', '.json', '.js', '.ps1', '.py'} and 'classes' not in p.parts:
        q = cloud / p.relative_to(s)
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, q)
note = f'''# Giran V8 completado — 11/10/2026
E:\\l2-local. Los líderes antes iban al artefacto antes de evaluar amenazas y la escolta dejaba de pelear al superar formación. Cada piloto detecta defensores/guardias, agresores de party y conquistadores; combate/persecución local con límites/LOS/PvP nativos. Líder pelea ante amenaza inmediata y espera escolta en combate antes de conquistar; Seal nativo180s, no item,50MP. Treguas bilaterales20s entre atacantes bajo presión defensora; renovables, caducan sin presión, se rompen al iniciar conquista/agredir al socio con bloqueo15s. Clanes/alianzas/órdenes no cambian; los atacantes siguen enemigos legales, sin inmunidad. Evitan skills de área cerca de socios. Panel .giran muestra intención/treguas. Mirellas50010 y Thiago50008 adicionales en trono, menús nativos, suelo caminable, originales Coliseo preservados. {match[1]} comprobaciones nativas PASS: daño real de16 atacantes/4 captores y escoltas lejos del capitán, treguas/8roles/captura/traición/expiración20s real, espera escolta y Seal, servicios; regresión V6 (puertas,4HQ300gemas,recorrido hastaSeal,revive/buffs/Amber), guardianes V7/core/geo intactos. Fixtures aislados, sin cargar Hellkevin ni completar conquista; balance completo requiere jugar. Snapshot humano/inventario,clanes/skills/rep/blood,castillo/owner/fecha,382guardias idénticos;19pilotos offline80 y4rivales registrados. Runtime/source/cloud/continuidad39 W10/W11/Nexus guardados; sin commit/push. No reejecutar instaladores históricos.
Documento GIRAN-IA-TREGUAS-Y-SERVICIOS-V8.md; research/giran-tactics-v8 y backups/giran-tactics-v8-2026-10-11.
'''
n = Path('K:/_CodexNexus')
(n / 'inbox/20261011-giran-v8.md').write_text(note, encoding='utf-8')
(n / 'inbox/20261011-giran-v8-in-progress.md').write_text('COMPLETADO. Ver 20261011-giran-v8.md.\n', encoding='utf-8')
with (n / 'sessions/lineage2-local.md').open('a', encoding='utf-8') as f:
    f.write('\n' + note)
portable = r / 'CONTINUIDAD-W11/Nexus'
if portable.exists():
    (portable / 'inbox').mkdir(exist_ok=True)
    (portable / 'inbox/20261011-giran-v8.md').write_text(note, encoding='utf-8')
    with (portable / 'sessions/lineage2-local.md').open('a', encoding='utf-8') as f:
        f.write('\n' + note)
print('V8 native tactics/regression/persistence PASS; mirrors, docs and Nexus saved.')
