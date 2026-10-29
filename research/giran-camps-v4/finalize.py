from pathlib import Path
import hashlib,json,re,shutil
r=Path(__file__).resolve().parents[2];stage=Path(__file__).resolve().parent
log=(r/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
match=re.search(r'GIRAN_V4_VERIFY PASS checks=(\d+);([^\r\n]+)',log)
assert match and 'GIRAN_V4_VERIFY FAILED' not in log,'Native V4 verification must pass first'
manifest=json.loads((stage/'installed.json').read_text())
for key,expected in manifest.items():
 p=r/('server/libs/GameServer.jar' if key=='GameServer.jar' else 'server/game/data/scripts/custom/'+key)
 assert hashlib.sha256(p.read_bytes()).hexdigest().lower()==expected.lower(),key
baseline=json.loads((stage/'baseline.json').read_text())
assert manifest['GameServer.jar'].lower()==baseline['GameServer.jar'].lower(),'Core unchanged'
proof={'native_checks':int(match[1]),'native_result':match[0],'core_unchanged_sha256':manifest['GameServer.jar'].lower(),'limits':['Full siege balance and complete travel to conquest still need player trial.','HQ retry test clears cooldown only in verification; production respects native30min.','Guardian60s timer accelerated in test.'],'persistent_snapshot':'backups/giran-camps-v4-2026-10-11/before.json and after.json;human/inventory,clans/reputation/blood/skills,castle/schedule,guards identical;19pilots offline80.'}
(stage/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
shutil.copy2(r/'logs/game-stderr.log',r/'backups/giran-camps-v4-2026-10-11/native-camps-pass.log')
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
 for dest in [r/'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab',r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/GiranSiegeLab']:
  dest.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest/p.name)
doc=r/'GIRAN-CAMPAMENTOS-V4.md';t=doc.read_text(encoding='utf-8')
t=t.replace('Pendiente de registrar el resultado final de la prueba aislada.',f'Compilación y prueba nativa aislada: **{match[1]} checks PASS**. Las cuatro bases se construyeron con Build Headquarters real, gastando 300 Gemstone C por intento; se comprobaron separación, recorridos nativos hacia la aproximación, elección de bandera viva para respawn, rebuff tras muerte y vuelta a objetivos del castillo después de una escaramuza real. La comparación persistente conserva personaje/inventario, clanes, castillo/fecha y guardias; los 19 pilotos quedaron offline nivel 80.')
doc.write_text(t,encoding='utf-8');shutil.copy2(doc,r/'cloud-repo/docs'/doc.name)
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
 dest=r/folder/'35_GIRAN_CAMPAMENTOS_V4_2026-10-11.md';shutil.copy2(doc,dest)
 index=r/folder/'LEER-PRIMERO.md'
 if index.exists():
  entry='\n- 35_GIRAN_CAMPAMENTOS_V4_2026-10-11.md: bases separadas, avance y resurrección; prueba nativa PASS.\n'
  text=index.read_text(encoding='utf-8-sig')
  if dest.name not in text:index.write_text(text+entry,encoding='utf-8')
cloud=r/'cloud-repo/research/giran-camps-v4'
for p in stage.rglob('*'):
 if p.is_file() and p.suffix in {'.java','.json','.js','.ps1','.py'} and 'classes' not in p.parts:
  q=cloud/p.relative_to(stage);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
note=f'''# Giran V4 completado — 11/10/2026
Proyecto E:\\l2-local. Se instalaron bases HQ separadas Holly110000/142000, Fury111200/144100, Sacred110000/146200, Waves111700/147500 con geodata y rutas comprobadas. Salidas escalonadas5s. Escaramuzas entre atacantes en entrada/patio10s y retorno al avance20s; defensores/engravers prioritarios, PvP nativo. Respawn30s en HQ vivo/base de respaldo; rebuff después de resurrección externa. Construcción comprueba bandera real/reintenta respetando reutilización nativa30min. {match[1]} checks nativos PASS: cuatro HQ construidos, ruta, selección respawn, revivalbuff, vuelta a puerta tras agresor; pruebas Amber/guardianes/Seal mantenidas. Humano/inventario,clanes/rep/blood/skills,Giran/fecha y382guardias idénticos;19pilotos offline80; Hellsing conservaGiran. Core/cliente sin cambios. Runtime/source/cloud y continuidad35 sincronizados; sin commit/push. GS libre y siege inactivo. Prueba completa de defensa/balance pendiente de Kevin. No reejecutar generadores V3 ni instaladores históricos.
Documento: E:\\l2-local\\GIRAN-CAMPAMENTOS-V4.md. Prueba/backups: research/giran-camps-v4, backups/giran-camps-v4-2026-10-11.
'''
nexus=Path('K:/_CodexNexus')
(nexus/'inbox/20261011-giran-v4.md').write_text(note,encoding='utf-8')
(nexus/'inbox/20261011-giran-v4-in-progress.md').write_text('COMPLETADO. GameServer libre; ver 20261011-giran-v4.md.\n',encoding='utf-8')
summary=nexus/'sessions/lineage2-local.md'
if summary.exists():
 with summary.open('a',encoding='utf-8') as f:f.write('\n'+note)
print('V4 finalized: native PASS, mirrors/docs/Nexus/proof saved; core unchanged.')
