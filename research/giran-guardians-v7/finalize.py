from pathlib import Path
import hashlib,json,re,shutil
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent;b=r/'backups/giran-guardians-v7-2026-10-11'
log=(r/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
match=re.search(r'GIRAN_V7_VERIFY PASS checks=(\d+);([^\r\n]+)',log)
assert match and 'GIRAN_V7_VERIFY FAILED' not in log
tags=['GIRAN_V7_PATROL_PASS','GIRAN_V7_GUARDIAN_PASS','GIRAN_V6_WALK_PASS','GIRAN_V6_RETURN_PASS']
assert all(tag in log for tag in tags)
before=json.loads((b/'before.json').read_text());after=json.loads((b/'after.json').read_text())
for key in ['human','inventory','clans','skills','castle','guards']:assert before[key]==after[key],key
assert len(after['pilots'])==19 and all(p['level']==80 and p['online']==0 for p in after['pilots'])
m=json.loads((s/'installed.json').read_text(encoding='utf-8-sig'));base=json.loads((s/'baseline.json').read_text())
for k,sha in m.items():
    p=r/('server/libs/GameServer.jar' if k=='GameServer.jar' else 'server/game/data/'+k if k.startswith('geodata/') else 'server/game/data/stats/npcs/custom/'+k[5:] if k.startswith('npcs/') else 'server/game/data/scripts/custom/'+k)
    assert hashlib.sha256(p.read_bytes()).hexdigest().lower()==sha.lower(),k
for k in ['GameServer.jar','geodata/23_22.l2j','npcs/giran_lab_guardians.xml']:assert m[k].lower()==base[k].lower(),k
proof={'native_checks':int(match[1]),'native_result':match[0],'guardian_proofs':[line for line in log.splitlines() if any(tag in line for tag in tags+['GIRAN_V7_COMBAT_PASS'])],'unchanged':{k:m[k].lower() for k in ['GameServer.jar','geodata/23_22.l2j','npcs/giran_lab_guardians.xml']},'persistence':'human/inventory,clans/skills/reputation/blood,castle/owner/schedule,guards preserved;19pilots offline80','limits':['Patrol and combat fixtures isolate route/target behavior; full competitive siege balance needs player trial.','Verification starts and aborts engraving; no conquest completed.','Native upper resurrection room is disconnected in geodata; revival-only castle transport exits it, then guardians walk to their posts.']}
(s/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');shutil.copy2(r/'logs/game-stderr.log',b/'native-guardians-pass.log')
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    for folder in [r/'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab',r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab']:
        folder.mkdir(parents=True,exist_ok=True);shutil.copy2(p,folder/p.name)
doc=r/'GIRAN-GUARDIANES-PATRULLA-V7.md';t=doc.read_text(encoding='utf-8').replace('Preparado y compilado; prueba nativa e instalación pendientes.',f'Instalado y validado: **{match[1]} comprobaciones nativas PASS**; GameServer listo para jugar.').replace('Validación prevista:', 'Validación nativa PASS:')
t+='\nPersistencia PASS: Hellkevin/inventario, clanes/skills/reputación, propietario/fecha de Giran y guardias conservados; 19 pilotos offline nivel80. Core, estadísticas de bosses y geodata V6 sin cambios. Runtime/source/cloud sincronizados, sin commit ni push.\n'
doc.write_text(t,encoding='utf-8');shutil.copy2(doc,r/'cloud-repo/docs'/doc.name)
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    dest=r/folder/'38_GIRAN_GUARDIANES_PATRULLA_V7_2026-10-11.md';shutil.copy2(doc,dest);index=r/folder/'LEER-PRIMERO.md'
    if index.exists() and dest.name not in index.read_text(encoding='utf-8-sig'):
        with index.open('a',encoding='utf-8') as f:f.write('\n- '+dest.name+': Ares/Nyx patrullan, detectan atacantes y defienden accesos/artefacto; prueba nativa PASS.\n')
cloud=r/'cloud-repo/research/giran-guardians-v7'
for p in s.rglob('*'):
    if p.is_file() and p.suffix in {'.java','.json','.js','.ps1','.py'} and 'classes' not in p.parts:
        q=cloud/p.relative_to(s);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
note=f'''# Giran V7 completado — 11/10/2026
E:\\l2-local. Ares y Nyx usaban SiegeGuardAI cuyo scan era alcance físico40 y sin Spawn no tenían retorno/patrulla. IA propia con eventos/formulas/casts/movimiento nativos: Ares patio/entradas, Nyx sala/pasillo/escalera norte/artefacto; patrulla en paz, escaneo1200 durante siege, prioridad Seal/agresor defensores, retención1600 y leash2000 del puesto. Dueño/defensores/neutrales protegidos, summons resuelven dueño, corpse60s/room10s. Sala superior aislada (BFS990 celdas, sin salida): transporte interno limitado a la resurrección hacia sala inferior, luego retorno caminando; Ares se queda en puesto interior cuando puertas cerradas, sin atravesarlas. {match[1]} comprobaciones PASS con ciclo completo ambas rutas, daño sin provocación/skills, dueño protegido, prioridad Seal, summon, límites y retorno sala; regresión V6 incluida. Snapshots preservan humano/inventario,clanes/rep/skills,castillo/owner/fecha,guardias;19pilotos offline80. Core/estadísticas/geo V6 unchanged. Runtime/source/cloud/continuidad38 W10/W11 sincronizados; no commit/push. Balance siege completo requiere juego. No reejecutar instaladores históricos.
Documento GIRAN-GUARDIANES-PATRULLA-V7.md; research/giran-guardians-v7 y backups/giran-guardians-v7-2026-10-11.\n'''
n=Path('K:/_CodexNexus');(n/'inbox/20261011-giran-v7.md').write_text(note,encoding='utf-8');(n/'inbox/20261011-giran-v7-in-progress.md').write_text('COMPLETADO. Ver 20261011-giran-v7.md.\n',encoding='utf-8')
with (n/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
portable=r/'CONTINUIDAD-W11/Nexus'
if portable.exists():
    (portable/'inbox').mkdir(exist_ok=True);(portable/'inbox/20261011-giran-v7.md').write_text(note,encoding='utf-8')
    with (portable/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
print('V7 native guardian/regression/persistence PASS; mirrors, docs and Nexus saved.')
