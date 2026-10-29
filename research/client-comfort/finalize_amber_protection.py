from pathlib import Path
import json,hashlib,shutil,re
from datetime import datetime
root=Path(__file__).resolve().parents[2]
backup=root/'backups/amber-protection-2026-10-10'
log=(root/'logs/game-stderr.log').read_text(errors='replace')
match=re.search(r'AmberProtectionVerification SUCCESS: (\d+) checks',log)
assert match and int(match.group(1))==48, 'Protection verification incomplete'
assert 'AmberProtectionVerification FAILED' not in log
core=hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest()
assert core=='c2f649806ee4248e5d9cc507ea36088d2799d12c6dc4b61c20d0500111d0d888'
hashes=json.loads((backup/'original-hashes.json').read_text())
files={}
for rel in hashes:
    relative=Path(rel)
    if relative.parts[0]!='server':continue
    suffix=relative.relative_to('server/game/data/scripts')
    paths=[root/relative]+[root/base/'dist/game/data/scripts'/suffix for base in ('source/L2J_Mobius_CT_0_Interlude','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude')]
    values=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    assert len(set(values))==1, 'Mirror mismatch '+str(suffix)
    files[str(suffix)]=values[0]
shutil.copy2(root/'logs/game-stderr.log',root/'research/client-comfort/amber-protection-verification.log')
shutil.copy2(root/'logs/game-stderr.log',backup/'pass48-verification.log')
report={'verified_at':datetime.now().isoformat(),'checks':48,'status':'PASS','core_sha256':core,'files':files,'client_changed':False,'manual_visual_review':'pending next user combat'}
(root/'research/client-comfort/amber-protection-installed.json').write_text(json.dumps(report,indent=2))
doc=root/'AMBER-PROTECCION-Y-APOYOS.md'
text=doc.read_text()+'\nResultado final: **48 comprobaciones PASS**. Incluye regresión de objetivos/PvP, impacto real sobre el dueño, prioridad preventiva antes de TP, TP activo/rango/HP, cambio a curandero, las seis variantes de cura, urgencia, foco manual, toggle y caducidad. Compilación Java correcta; nueve fuentes coinciden en las tres ubicaciones.\n'
doc.write_text(text)
for target in (root/'CONTINUIDAD-W10/23_AMBER_PROTECCION_Y_APOYOS_2026-10-10.md',root/'CONTINUIDAD-W11/23_AMBER_PROTECCION_Y_APOYOS_2026-10-10.md',root/'cloud-repo/docs/AMBER-PROTECCION-Y-APOYOS.md',root/'cloud-repo/CONTINUIDAD-W10/23_AMBER_PROTECCION_Y_APOYOS_2026-10-10.md',root/'cloud-repo/CONTINUIDAD-W11/23_AMBER_PROTECCION_Y_APOYOS_2026-10-10.md'):
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(doc,target)
note='E:/l2-local: Amber proteccion del amo instalada y verificada: 48 checks PASS. Reaccion al dano real; summon del agresor preventivamente antes de Transfer Pain; porcentaje/rango/HP reales con TP activo; curas efectivas HP/CP normales/porcentaje/periodicas priorizan curandero. Critico HP amo prioriza atacante. Foco manual/toggle/party/paz/PvP conservados. Sin cliente ni JAR; V10/camara/catalogo intactos. Nueve fuentes runtime/source/cloud iguales. Backup amber-protection-2026-10-10. Docs AMBER-PROTECCION-Y-APOYOS.md y continuidad23, pruebas/report research/client-comfort/amber-protection*. Verificacion sin cambios de balance, pendiente TvT manual. Sin commit/push. Ventana de coordinacion liberada; arranque normal sin pruebas al finalizar.\n'
Path('K:/_CodexNexus/inbox/20261010-lineage2-amber-protection.md').write_text(note)
Path('K:/_CodexNexus/inbox/20261010-lineage2-amber-protection-in-progress.md').write_text('FINALIZADO. Ver 20261010-lineage2-amber-protection.md.\n')
print('PASS: 48 checks archived; hashes/mirrors/core verified; portable/cloud/Nexus documentation saved.')
