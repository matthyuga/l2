from pathlib import Path
import json,re,hashlib,shutil
from datetime import datetime
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent;backup=root/'backups/amber-ui-rain-2026-10-10'
log=(root/'logs/game-stderr.log').read_text(errors='replace')
match=re.search(r'AmberUiRainVerification SUCCESS: (\d+) checks',log)
assert match and int(match.group(1))==66,'UI/rain verification incomplete'
assert 'AmberUiRainVerification FAILED' not in log
original=json.loads((backup/'original-hashes.json').read_text())
core=hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest();assert core==original[str(root/'server/libs/GameServer.jar')]
client=root.parent/'l2/system-hud'
assert (root.parent/'l2/systextures/AmberAssistIconsV1.utx').read_bytes()[:28].decode('utf-16le')=='Lineage2Ver121','Texture wrapper missing; raw UCC packages are rejected by L2.'
installed=json.loads((stage/'installed-client.json').read_text())
for name,sha in installed.items():
    target=(root.parent/'l2/systextures' if name.endswith('.utx') else client)/name
    assert hashlib.sha256(target.read_bytes()).hexdigest()==sha
assert hashlib.sha256((client/'actionname-e.dat').read_bytes()).hexdigest()==original[str(client/'actionname-e.dat')]
mirrors=json.loads((backup/'mirror-state.json').read_text())
for rel,sha in mirrors.items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==sha
shutil.copy2(root/'logs/game-stderr.log',stage/'verification-server.log');shutil.copy2(root/'logs/game-stderr.log',backup/'pass66-verification.log')
report={'verified_at':datetime.now().isoformat(),'checks':66,'status':'PASS','client':installed,'core_sha256':core,'mirror_files':len(mirrors),'ui_visual_review':'pending user playtest','native_controls':'separate direct group filters and AI buttons; existing skill drag and tabs preserved'}
(stage/'installed.json').write_text(json.dumps(report,indent=2))
doc=root/'AMBER-UI-Y-LLUVIA-V2.md';doc.write_text(doc.read_text()+'\nResultado final: **66 comprobaciones PASS** con daño mágico nativo real, reacción/TP/curanderos, acceso IA ON/OFF, filtros sin mutación de clase, potencia de lluvia, UD, bloqueo perfecto, tres impactos reales, consumo de recursos y pérdidas de CP/HP. Compilación Java y verificación de paquetes/DAT/texture correctas.\n')
for rel in ('CONTINUIDAD-W10/24_AMBER_UI_Y_LLUVIA_V2_2026-10-10.md','CONTINUIDAD-W11/24_AMBER_UI_Y_LLUVIA_V2_2026-10-10.md','cloud-repo/docs/AMBER-UI-Y-LLUVIA-V2.md','cloud-repo/CONTINUIDAD-W10/24_AMBER_UI_Y_LLUVIA_V2_2026-10-10.md','cloud-repo/CONTINUIDAD-W11/24_AMBER_UI_Y_LLUVIA_V2_2026-10-10.md'):
    target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(doc,target)
note='E:/l2-local: UI Amber/skills V2 instalada offline, 66 checks PASS. Alt+K botones directos Principal/Sub1-3/Comunes/Amber/Todas + indice nombres, sin dialogo extra por filtro. Icono propio IA en skill19014, Alt+K y SummonedWnd; bypass .amber toggle usa efecto nativo y deja icono buff ON. Package nuevo AmberAssistIconsV1.utx, pixels1024 export iguales; DAT solo fila19014. Lluvia skill fisico potencia3000, snapshot PAtk/elemento y resumen CP/HP; conserva 3.5s/3impactos/radio200/120MP/3shots/45s, UD y perfectblock1. Core c2f649... sin cambio, V10/camara intactos. Pelea usuario run30 sin activacion AI; lluvia203.86 y rivalUD. Fuentes/XML runtime/source/cloud coinciden, backup amber-ui-rain-2026-10-10 y continuidad24/AMBER-UI-Y-LLUVIA-V2.md. Pendiente revision visual/clics reales usuario; pruebas validan protocolo, callbacksVM y comportamiento servidor. Ventana coordinacion liberada; arranque final normal sin verificadores. Sin commit/push.\n'
Path('K:/_CodexNexus/inbox/20261010-lineage2-amber-ui-rain.md').write_text(note)
Path('K:/_CodexNexus/inbox/20261010-lineage2-amber-ui-rain-in-progress.md').write_text('FINALIZADO. Ver 20261010-lineage2-amber-ui-rain.md.\n')
for name in ('build_ui.groovy','build_callbacks.groovy','verify_callbacks.groovy','build_icon.groovy','patch_catalogs.py','sync_sources.py','install_client.py','restart_server.ps1','finalize.py','catalog-verification.json','installed.json'):
    target=root/'cloud-repo/research/client-comfort/v2'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stage/name,target)
print('PASS: 66 server checks, installed client, unchanged core/native action catalogs, mirrored sources and portable/Nexus continuity archived.')
