from pathlib import Path
import hashlib, json, shutil, datetime
root=Path(__file__).resolve().parents[2]
stage=root/'research/client-comfort'
client=root.parent/'l2/system-hud'
backup=root/'backups/client-comfort-2026-10-10'
log=(root/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
assert 'SkillCatalogVerification SUCCESS: 471 checks' in log
assert 'SkillCatalogVerification FAILED' not in log
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
hashes={}
for name in ('user.ini','l2.ini','Interface.u','Interface.xdat'):
    assert sha(client/name)==sha(stage/name), name
    hashes[name]=sha(client/name)
assert sha(root/'server/libs/GameServer.jar')==sha(root/'build/client-comfort/GameServer.jar')
for name in ('skillgrp.dat','skillname-e.dat'):
    assert sha(client/name)==sha(backup/'client'/name), 'Concurrent DAT change: '+name
    hashes[name]=sha(client/name)
shutil.copy2(root/'logs/game-stderr.log',stage/'verification-server.log')
result={'installed_at':datetime.datetime.now().astimezone().isoformat(),'checks':471,
        'native_opcode':'0x58','database_probe_unchanged':True,'client_sha256':hashes,
        'gameserver_sha256':sha(root/'server/libs/GameServer.jar'),
        'visual_client_validation':'pending user playtest',
        'server_verification':'one-shot completed; next default startup flag false'}
(stage/'installed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
name='20_CAMARA_CATALOGO_POR_CLASE_2026-10-10.md'
for folder in ('CONTINUIDAD-W10','CONTINUIDAD-W11','cloud-repo/CONTINUIDAD-W10','cloud-repo/CONTINUIDAD-W11','cloud-repo/docs'):
    shutil.copy2(root/'CAMARA-Y-CATALOGO-POR-CLASE.md',root/folder/name)
cloud=root/'cloud-repo/research/client-comfort'
cloud.mkdir(parents=True,exist_ok=True)
for pattern in ('*.py','*.groovy','verification.json','installed.json'):
    for file in stage.glob(pattern): shutil.copy2(file,cloud/file.name)
shutil.copy2(root/'Install-ClientComfort.ps1',root/'cloud-repo/ops/windows/Install-ClientComfort.ps1')
note='''# Cámara y catálogo por clase — instalado y verificado (2026-10-10)
Proyecto E:/l2-local; cliente E:/l2/system-hud. Usuario confirmó L2 cerrado; instalación realizada con cero conexiones y hashguards. GameServer iniciado; verificación opt-in de una sola ejecución finalizada: 471 checks PASS a las14:58. No hace falta otro reinicio. El inicio habitual deja catalog.verify=false. Fin de la ventana exclusiva de esta sesión.

Cámara MaxZoomingDist250->1800. Alt+K tiene Clases / Amber; acceso alternativo .habilidades / .skills. Orden acordado principal -> sub1 -> sub2 -> sub3 -> Comunes, conservando pestañas activas/pasivas. Grupo adicional Amber y Especiales. Límite original 80 por sección ampliado a2048; 19014 Asistencia de Amber está incluido. Filtros por árboles reales y skills conocidos; no conceden skills ni alteran niveles, clase activa o shortcuts. Recuperar lista completa: .habilidades filter -1. Pendiente prueba visual del usuario.

JAR: sólo cambia SkillList.class y agrega SkillCatalogView/$Model; demás entries idénticos. Preservados Player, arena, razas y Amber. DAT actuales V9 idénticos a respaldo: no se sobrescribieron. Interface.u sólo añade callback mínimo; las demás funciones idénticas. Interface.xdat sólo cambia MagicSkillWnd; otras ventanas idénticas. l2.ini prioriza system-hud/*.u.

Backups/client-comfort-2026-10-10. Documentación CAMARA-Y-CATALOGO-POR-CLASE.md y CONTINUIDAD-W10/W11/20_CAMARA_CATALOGO_POR_CLASE_2026-10-10.md. Proof research/client-comfort/installed.json, verification.json y verification-server.log. Fuentes y documentación espejadas en cloud-repo, sin commit/push. Base del probe reservado conserva skills/subclases/shortcuts; snapshot comparado antes/después.
'''
Path('K:/_CodexNexus/inbox/20261010-lineage2-camera-skill-catalog.md').write_text(note,encoding='utf-8')
print(json.dumps(result,indent=2))
