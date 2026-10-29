from pathlib import Path
import hashlib
import json
import re
import shutil

root = Path(__file__).resolve().parents[2]
stage = Path(__file__).resolve().parent
backup = root / 'backups/giran-orders-v5-2026-10-11'
log = (root / 'logs/game-stderr.log').read_text(encoding='utf-8', errors='replace')
match = re.search(r'GIRAN_V5_VERIFY PASS checks=(\d+);([^\r\n]+)', log)
assert match and not re.search(r'GIRAN_V[345]_VERIFY FAILED', log), 'Native verification must pass first'
before = json.loads((backup / 'before.json').read_text(encoding='utf-8'))
after = json.loads((backup / 'after.json').read_text(encoding='utf-8'))
for key in ['human', 'inventory', 'clans', 'skills', 'castle', 'guards']:
    assert before[key] == after[key], 'Persistent change: ' + key
assert len(after['pilots']) == 19 and all(p['level'] == 80 and p['online'] == 0 for p in after['pilots'])
manifest = json.loads((stage / 'installed.json').read_text(encoding='utf-8-sig'))
baseline = json.loads((stage / 'baseline.json').read_text(encoding='utf-8-sig'))
for key, expected in manifest.items():
    p = root / ('server/libs/GameServer.jar' if key == 'GameServer.jar' else 'server/game/data/scripts/custom/' + key)
    assert hashlib.sha256(p.read_bytes()).hexdigest().lower() == expected.lower(), key
assert manifest['GameServer.jar'].lower() == baseline['GameServer.jar'].lower(), 'Core changed'
proof = {
    'native_checks': int(match[1]),
    'native_result': match[0],
    'core_unchanged_sha256': manifest['GameServer.jar'].lower(),
    'persistent_snapshot': 'Private before.json and after.json in backups/giran-orders-v5-2026-10-11; human/inventory, clans/skills/reputation/blood, castle/schedule and guards identical; 19 pilots offline level80.',
    'limits': [
        'Exact player mouse-click rampart stall remains pending /loc; two native upper-floor movement smoke tests passed.',
        'Full competitive siege and balance still need player trial.',
        'HQ retry cooldown and guardian revival timer accelerated only in verification.'
    ]
}
(stage / 'verification.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
shutil.copy2(root / 'logs/game-stderr.log', backup / 'native-orders-pass.log')
for p in (root / 'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    for dest in [root / 'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab', root / 'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab']:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest / p.name)
doc = root / 'GIRAN-ORDENES-V5.md'
t = doc.read_text(encoding='utf-8-sig')
t = t.replace('Preparado y compilado; pendiente de instalar con L2 cerrado y ejecutar prueba nativa.', f'Instalado y validado con L2 cerrado: **{match[1]} checks nativos PASS**. GameServer disponible; prueba aislada finalizada y pilotos descargados.')
t = t.replace('Compilación PASS. Prueba nativa pendiente;', f'Compilación PASS. Prueba nativa aislada **{match[1]} checks PASS**;')
t += '\nComparación persistente PASS: Hellkevin y su inventario, clanes/reputación/skills, propietario y fecha de Giran, y 382 guardias conservados. Los 19 pilotos quedaron offline nivel 80. Runtime, source/dist, overlay cloud y continuidad W10/W11 sincronizados; core y cliente sin cambios.\n'
doc.write_text(t, encoding='utf-8')
(root / 'cloud-repo/docs').mkdir(parents=True, exist_ok=True)
shutil.copy2(doc, root / 'cloud-repo/docs' / doc.name)
for folder in ['CONTINUIDAD-W10', 'CONTINUIDAD-W11']:
    dest = root / folder / '36_GIRAN_ORDENES_V5_2026-10-11.md'
    shutil.copy2(doc, dest)
    old = root / folder / '36_GIRAN_ORDENES_V5_PREPARADO_2026-10-11.md'
    if old.exists():
        old.write_text('INSTALADO Y VALIDADO. Ver 36_GIRAN_ORDENES_V5_2026-10-11.md.\n', encoding='utf-8')
    index = root / folder / 'LEER-PRIMERO.md'
    if index.exists():
        content = index.read_text(encoding='utf-8-sig')
        if dest.name not in content:
            index.write_text(content + '\n- ' + dest.name + ': órdenes solo a aliados, traslado al mismo piso y daño nativo físico/mágico a puertas; PASS. Atasco exacto del muro pendiente /loc.\n', encoding='utf-8')
cloud = root / 'cloud-repo/research/giran-orders-v5'
for p in stage.rglob('*'):
    if p.is_file() and p.suffix in {'.java', '.json', '.js', '.ps1', '.py'} and 'classes' not in p.parts:
        q = cloud / p.relative_to(stage)
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, q)
note = f'''# Giran V5 completado — 11/10/2026
Proyecto E:\\l2-local. Kevin cerró L2 y se instaló V5. Órdenes seguir/asalto/retirada evalúan clan, alianza y defensores actuales; los cuatro clanes rivales mantienen sus agendas. .giran traer teletraslada solo pilotos aliados vivos a celda conectada del mismo piso, sin revivir ni mover guardianes/humanos/enemigos. .giran diagnostico registra coordenadas cliente/servidor y estados IA. Ruptura de puerta no se interrumpe por distancia al capitán; magos usan nukes nativos y puerta requerida se prioriza antes que guardias en muralla. {match[1]} checks nativos PASS: exclusión rivales/posición conservada, aliado misma altura, movimiento en capas -2448/-2144, daño melee y mágico real puerta, regresión HQ/revival/Amber/Seal/guardianes. Snapshot privado antes/después conserva Hellkevin/inventario, clanes/rep/blood/skills, Giran/fecha y382guardias;19pilotos offline80. Core/cliente sin cambios. Muro: Kevin usa clic; falta /loc exacto, no afirmar corregido por smoke tests. Memoria anterior OOM2GB por pool ThreadLocal caminos; V2 limita32buffers65MiB, GS actual4GB. Runtime/source/cloud y continuidad36 sincronizados; sin commit/push. Prueba completa de defensa pendiente de Kevin.
Documento: E:\\l2-local\\GIRAN-ORDENES-V5.md. Prueba y respaldo: research/giran-orders-v5, backups/giran-orders-v5-2026-10-11. No reejecutar instaladores/generadores históricos.
'''
nexus = Path('K:/_CodexNexus')
(nexus / 'inbox/20261011-giran-v5.md').write_text(note, encoding='utf-8')
(nexus / 'inbox/20261011-giran-v5-in-progress.md').write_text('COMPLETADO. Ver 20261011-giran-v5.md.\n', encoding='utf-8')
summary = nexus / 'sessions/lineage2-local.md'
if summary.exists():
    with summary.open('a', encoding='utf-8') as f:
        f.write('\n' + note)
print('V5 finalized: native PASS, persistence preserved, runtime/source/cloud/docs/Nexus mirrored; core unchanged.')
