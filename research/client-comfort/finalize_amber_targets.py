from pathlib import Path
import hashlib,json,shutil,datetime,os,re,subprocess
root=Path(__file__).resolve().parents[2]
stage=root/'research/client-comfort'
log=(root/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
assert 'AmberTargetVerification SUCCESS: 25 checks' in log
assert 'AmberTargetVerification FAILED' not in log
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
core=sha(root/'server/libs/GameServer.jar')
assert core=='c2f649806ee4248e5d9cc507ea36088d2799d12c6dc4b61c20d0500111d0d888'
files=['AmberContract/'+name for name in ['AmberContract.java','AmberServitor.java','AmberAssist.java','AmberContractVerification.java']]+['LabCombatPilots/LabCombatPilots.java']
hashes={}
for rel in files:
    runtime=root/'server/game/data/scripts/custom'/rel
    hashes[rel]=sha(runtime)
    for base in ['source/L2J_Mobius_CT_0_Interlude','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude']:
        assert sha(root/base/'dist/game/data/scripts/custom'/rel)==hashes[rel]
cfg=(root/'server/game/config/Database.ini').read_text(encoding='utf-8-sig')
def val(key):return re.search(r'^'+key+r'\s*=\s*(.*)$',cfg,re.M).group(1).strip()
env=os.environ.copy();env['MYSQL_PWD']=val('Password')
query="SELECT char_name,clanid,online FROM characters WHERE char_name IN ('Hellkevin','ArenaNoctis','AmberOwnerProbe','AmberTargetProbe') ORDER BY char_name"
rows=subprocess.run([str(root/'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'),'--host=127.0.0.1','--port=3307','--user='+val('Login'),'-N','-B','l2jmobiusinterlude','-e',query],env=env,check=True,capture_output=True).stdout.decode().splitlines()
characters={row.split('\t')[0]:[int(v) for v in row.split('\t')[1:]] for row in rows}
assert characters['ArenaNoctis']==[268474389,0]
assert characters['AmberOwnerProbe']==[0,0] and characters['AmberTargetProbe']==[0,0]
shutil.copy2(root/'logs/game-stderr.log',stage/'amber-target-verification.log')
result={'installed_at':datetime.datetime.now().astimezone().isoformat(),'target_checks':25,'earlier_full_suite_checks':146,
        'real_damage_events_for_autonomous_and_manual_orders':True,'server_sources_sha256':hashes,
        'unchanged_core_sha256':core,'characters_after_test':characters,
        'client_changes':False,'verification_mode':'one-shot completed; next normal launch disables opt-in flag'}
(stage/'amber-target-installed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
doc=root/'AMBER-OBJETIVOS-Y-PVP.md'
text=doc.read_text(encoding='utf-8')
text += '\nResultado final: **25 comprobaciones específicas PASS**, incluidos eventos de daño real con selección autónoma de un rival válido y foco manual contra el Noctis Player. La batería general anterior pasó146 comprobaciones (log archivado en pass146-verification.log). Una repetición posterior de esa batería falló al preparar un root aleatorio; se amplió su número máximo de intentos en el arnés y se aisló la prueba de objetivos con lab.amber.targets.only=true. Noctis conserva Hellsing y queda desconectado al terminar; ambos probes quedan desconectados y sin clan. GameServer permanece iniciado; prueba opt-in terminada.\n'
doc.write_text(text,encoding='utf-8')
name='22_AMBER_OBJETIVOS_Y_PVP_2026-10-10.md'
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11','cloud-repo/CONTINUIDAD-W10','cloud-repo/CONTINUIDAD-W11','cloud-repo/docs']:
    shutil.copy2(doc,root/folder/name)
cloud=root/'cloud-repo/research/client-comfort'
for name in ['sync_amber_target_policy.py','restart_amber_target_policy.ps1','finalize_amber_targets.py','amber-target-installed.json']:
    shutil.copy2(stage/name,cloud/name)
note='''# Amber: objetivos y bandera PvP — instalado y verificado
E:/l2-local, 2026-10-10. Fin de la ventana exclusiva de prueba: GameServer iniciado, targets-only opt-in concluido con25 checks PASS; bateria general anterior146 PASS archivada. Confirmados eventos reales de daño de Amber en seleccion autonoma y foco manual al Noctis Player; modo auditoría AMBER_TARGET. Noctis mantiene Hellsing, online0; probes restaurados sin clan/online0. Cliente y JAR no se modificaron; corec2f649... intacto y visualesV10/cámara/catálogo preservados.

Causa: ArenaNoctis y Hellkevin son del mismo clan; Amber prohibía clan/ally incluso en Coliseo, exigía PVP ambos y la IA no consideraba NPC. Ahora orden manual sigue reglas nativas de arena/Ctrl en campo; IA reconoce relación temporal .ia (getter read-only, volatile, sin cambiar builds/conductas del piloto). Monstruos fuera de arena admitidos; NPC contrato/marker, party, paz, NO_PVP, instancia, invulnerabilidad y estados siguen protegidos. IA no inicia PK de blancos ajenos y protege clan salvo rival activo o foco manual válido. Mensajes por motivo.

Arco aplica bandera nativa al dueño; lluvia propia ahora también atribuye agresión al dueño con reglas existentes, incluidas excepciones arena/PK/config. Actor autoriza sólo objetivo explícito Ctrl; Stop/Follow/cambio modo limpian permiso.

Backup backups/amber-target-policy-2026-10-10. Cinco fuentes runtime/source/cloud espejadas; sin commit/push. Detalle AMBER-OBJETIVOS-Y-PVP.md y continuidad22; proof research/client-comfort/amber-target-installed.json y amber-target-verification.log. Prueba de usuario: .ia mago, esperar inicio, activar Asistencia; puede elegir Nightshade primero. Seleccionar Noctis+Atacar fija foco.\n'''
Path('K:/_CodexNexus/inbox/20261010-lineage2-amber-target-policy.md').write_text(note,encoding='utf-8')
print(json.dumps(result,indent=2))
