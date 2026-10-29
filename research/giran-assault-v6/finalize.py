from pathlib import Path
import hashlib,json,re,shutil
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent;b=r/'backups/giran-assault-v6-2026-10-11'
log=(r/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
match=re.search(r'GIRAN_V6_VERIFY PASS checks=(\d+);([^\r\n]+)',log)
assert match and 'GIRAN_V6_VERIFY FAILED' not in log and 'GIRAN_V6_WALK_PASS' in log and 'GIRAN_V6_RETURN_PASS' in log,'Native walk, return approach and full verification must pass'
before=json.loads((b/'before.json').read_text());after=json.loads((b/'after.json').read_text())
for key in ['human','inventory','clans','skills','castle','guards']:assert before[key]==after[key],key
assert len(after['pilots'])==19 and all(p['level']==80 and p['online']==0 for p in after['pilots'])
manifest=json.loads((s/'installed.json').read_text(encoding='utf-8-sig'));baseline=json.loads((s/'baseline.json').read_text(encoding='utf-8-sig'))
for key,sha in manifest.items():
    p=r/('server/libs/GameServer.jar' if key=='GameServer.jar' else 'server/game/data/'+key if key.startswith('geodata/') else 'server/game/data/scripts/custom/'+key)
    assert hashlib.sha256(p.read_bytes()).hexdigest().lower()==sha.lower(),key
assert manifest['GameServer.jar'].lower()==baseline['GameServer.jar'].lower()
old=(b/'23_22-before.l2j').read_bytes();new=(r/'server/game/data/geodata/23_22.l2j').read_bytes()
assert len(old)==len(new)
diff=[(i,a,c) for i,(a,c) in enumerate(zip(old,new)) if a!=c]
assert len(diff)==5 and all((a^c)&0xfc==0 for _,a,c in diff),'Exactly five E/W collision bytes only'
proof={'native_checks':int(match[1]),'native_result':match[0],'native_walk':re.search(r'GIRAN_V6_WALK_PASS[^\r\n]+',log)[0],'native_return_approach':re.search(r'GIRAN_V6_RETURN_PASS[^\r\n]+',log)[0],'core_unchanged_sha256':manifest['GameServer.jar'].lower(),'geodata_before_sha256':baseline['geodata/23_22.l2j'].lower(),'geodata_after_sha256':manifest['geodata/23_22.l2j'].lower(),'geodata_changed_bytes':diff,'limits':['Walking test isolates a cleared hall and restores pilot health; full competitive battle and balance need player trial.','Native conquest is started and aborted, never completed in verification.','Exact outer-rampart mouse stall remains pending /loc.'],'persistence':'Private before/after snapshots identical for human/inventory,clans/skills/reputation,castle/owner/date and382guards;19pilots offline80.'}
(s/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');shutil.copy2(r/'logs/game-stderr.log',b/'native-assault-pass.log')
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    for base in [r/'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab',r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab']:
        base.mkdir(parents=True,exist_ok=True);shutil.copy2(p,base/p.name)
for base in [r/'source/L2J_Mobius_CT_0_Interlude/dist/game/data/geodata',r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/geodata']:
    base.mkdir(parents=True,exist_ok=True);shutil.copy2(r/'server/game/data/geodata/23_22.l2j',base/'23_22.l2j')
doc=r/'GIRAN-ASALTO-POR-ETAPAS-V6.md';t=doc.read_text(encoding='utf-8')
t=t.replace('Instalado para prueba aislada; validación nativa pendiente. Mantener L2 cerrado hasta finalizarla.',f'Instalado y validado: **{match[1]} comprobaciones nativas PASS**, incluido recorrido desde sala hasta inicio real de Seal. Prueba finalizada y GameServer listo para Kevin.')
t=t.replace('Validación previa PASS; prueba adicional de regreso desde campamento en curso. Mantener L2 cerrado hasta terminar.',f'Instalado y validado: **{match[1]} comprobaciones nativas PASS**, incluido recorrido desde sala hasta inicio real de Seal y regreso desde campamento respetando puertas. Prueba finalizada y GameServer listo para Kevin.')
t=re.sub(r'\*\*\d+ comprobaciones nativas PASS\*\*',f'**{match[1]} comprobaciones nativas PASS**',t)
t=re.sub(r'\*\*\d+ comprobaciones\*\*',f'**{match[1]} comprobaciones**',t)
t=t.replace('Compilación PASS. Prueba nativa pendiente:',f'Compilación y prueba nativa PASS (**{match[1]} comprobaciones**):')
if 'Comparación persistente PASS:' not in t:t+='\nComparación persistente PASS: Hellkevin/inventario, clanes/reputación/skills, Giran/propietario/fecha y382guardias conservados;19pilotos offline80. Runtime/source/cloud y continuidad37 W10/W11 sincronizados.\n'
doc.write_text(t,encoding='utf-8');shutil.copy2(doc,r/'cloud-repo/docs'/doc.name)
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    dest=r/folder/'37_GIRAN_ASALTO_POR_ETAPAS_V6_2026-10-11.md';shutil.copy2(doc,dest)
    idx=r/folder/'LEER-PRIMERO.md'
    if idx.exists():
        txt=idx.read_text(encoding='utf-8-sig')
        if dest.name not in txt:idx.write_text(txt+'\n- '+dest.name+': avance por tramos, líder al artefacto, escolta/protección y escalera corregida; recorrido nativo PASS.\n',encoding='utf-8')
cloud=r/'cloud-repo/research/giran-assault-v6'
for p in s.rglob('*'):
    if p.is_file() and p.suffix in {'.java','.json','.js','.ps1','.py'} and 'classes' not in p.parts:
        q=cloud/p.relative_to(s);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
note=f'''# Giran V6 completado — 11/10/2026
E:\\l2-local. Kevin pidió escuadrones que avancen hasta conquista, líderes al artefacto y escoltas que limpien/protejan. Se instalaron etapas puerta exterior/patio/interior/sala/pasillo/artefacto; ningún objetivo secundario ausente detiene la ruta principal. Líder prioriza llegada y Seal nativo3min, escolta adquiere defensores1100 y protege canal; persecución10s/1600 desde adquisición, rival-attacker ventanas10s y retorno20s en todo castillo. Llegada final24 frente al antiguo100 y rango85 de Seal. Se corrigieron exactamente5bits E/W en5bytes de23_22, escalera norte y145064 x117528..117960; alturas/capas/otras colisiones conservadas, NPC artefacto original, sin bypass ni teleport de conquista. Original privado respaldado. {match[1]} checks nativos PASS, incluyendo líder camina desde sala por pasillo/escalera hasta inicio real deSeal (sala despejada/salud restaurada para aislar navegación); escolta ataca agresor y mantiene defensor que se aleja másde400. Regresión órdenes aliadas/puertas/HQ/buffs/Amber/guardianes PASS. Snapshots conservan Hellkevin/inventario,clanes/rep/skills,Giran/fecha/owner y382guardias;19offline80. Core/cliente unchanged. Runtime/source/cloud/continuidad37 sincronizados,sincommit/push. Siege completo bajo combate/balance y muroexterior exacto(/loc) pendientes. No reejecutar instaladores históricos.\nDocumento E:\\l2-local\\GIRAN-ASALTO-POR-ETAPAS-V6.md; pruebas research/giran-assault-v6; backups/giran-assault-v6-2026-10-11.\n'''
n=Path('K:/_CodexNexus');(n/'inbox/20261011-giran-v6.md').write_text(note,encoding='utf-8');(n/'inbox/20261011-giran-v6-in-progress.md').write_text('COMPLETADO. Ver 20261011-giran-v6.md.\n',encoding='utf-8')
with (n/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
portable=r/'CONTINUIDAD-W11/Nexus'
if portable.exists():
    (portable/'inbox').mkdir(exist_ok=True);(portable/'inbox/20261011-giran-v6.md').write_text(note,encoding='utf-8')
    with (portable/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
print('V6 finalized: native walk/protection/regression PASS, persistence preserved, five geodata bytes confirmed, mirrors/docs/Nexus saved.')
