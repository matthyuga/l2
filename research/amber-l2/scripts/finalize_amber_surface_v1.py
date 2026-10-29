from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1];STAGE=ROOT/'exports/surface-v1';CLIENT=PROJECT.parent/'l2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
installation=json.loads((STAGE/'installation.json').read_text(encoding='utf-8-sig'))
backup=Path(installation['backup']); manifest=json.loads((backup/'manifest.json').read_text(encoding='utf-8-sig'))
proof=json.loads((STAGE/'native-proof.json').read_text())
# Finish the texture-only deployment with the client's filename-bound wrapper.
# Preflight against this installation's manifest, never overwrite another session's version.
target=CLIENT/'systextures/AmberSurfaceV1.utx';source=STAGE/'AmberSurfaceV1.utx'
entry=next(e for e in installation['files'] if e['relative']=='systextures\\AmberSurfaceV1.utx')
if sha(target)!=sha(source):
    active=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id; exit 0"],text=True)
    assert not active.strip(),'Close L2 before finalizing the texture deployment'
    assert sha(target)==entry['installed_sha256'].lower(),'Texture changed concurrently'
    shutil.copy2(source,target)
entry['installed_sha256']=sha(source).upper()
next(e for e in manifest if e['relative']==entry['relative'])['installed_sha256']=entry['installed_sha256']
installation['texture_wrapper']=proof['texture_wrapper']
(STAGE/'installation.json').write_text(json.dumps(installation,ensure_ascii=False,indent=2),encoding='utf-8-sig')
(backup/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8-sig')
for entry in installation['files']:assert sha(CLIENT/entry['relative'].replace('\\','/'))==entry['installed_sha256'].lower()
reader=ROOT/'tools/umodel.exe'
for pkg in proof['packages']:
    for atlas in ['AmberBody','AmberOutfit']:
        run=subprocess.run([str(reader),'-dump','-game=l2','-path='+str(CLIENT),pkg['package']+'.ukx',atlas+'Shader'],capture_output=True,text=True,errors='replace',timeout=60)
        assert run.returncode==0 and 'Unable to load' not in run.stdout
        assert 'SelfIlluminationMask = Texture' in run.stdout and 'Specular = TexEnvMap' in run.stdout
        (STAGE/'verification'/('installed-'+pkg['package']+'-'+atlas+'.log')).write_text(run.stdout+run.stderr)
browser=json.loads((PROJECT/'research/model-catalog/amber-comparison/surface-v1/browser-proof.json').read_text())
assert len(browser['cases'])==3 and not browser['exceptions']
galleryproof=PROJECT/'research/model-catalog/verification.json';g=json.loads(galleryproof.read_text())
assert g['readable_models_and_thumbnails']==642 and g['all_asset_links_present']
g['amber_surface_v1']={'installed':True,'texture_wrapper_121':True,'browser_cases':browser['cases'],'in_game_verified':False}
galleryproof.write_text(json.dumps(g,indent=2),encoding='utf-8')
doc=f'''# Amber: integración visual V1 — 12/10/2026

Instalada en E:\\l2 para Amber NPC (902500/display59001) y summon (902501/display59002). Abrir 2-JUGAR.cmd; no necesita reinicio del GameServer. Se conservan L2AmberNPCv5.AmberNPC y L2AmberArcherV2.AmberNPC y sus bindings actuales.

La revisión reemplaza la autoiluminación completa por máscaras de datos derivadas de los materiales y celdas del atlas original: piel18%, detalles faciales14%, ojos30%, pelo8%, tela/cuero6%, metal3%. Así el entorno puede sombrear la mayor parte del color sin apagar completamente la cara. Se incorpora el TexEnvMap nativo FFighter.LowBody.TexEnvMap0, con máscara suave: metal18%, ojos6%, pelo2,5%; las demás zonas no reciben ese reflejo. Estos porcentajes son valores de las máscaras del shader UE2, no multiplicadores de estadísticas ni una promesa fotométrica.

Los dos shaders se conservan maskedAlpha128, TwoSided, ZWrite y AlphaTest; FallbackMaterial apunta al atlas original. Solo cambiaron AmberBodyShader y AmberOutfitShader en cada UKX. Geometría, huesos, pesos, transformaciones, texturas artísticas originales y dependencias de animación se conservaron byte por byte. No se repintaron los atlas ni se añadieron normal maps. El tratamiento toon original todavía existe; esta revisión aborda iluminación y materiales.

Nueva dependencia: systextures/AmberSurfaceV1.utx, cuatro máscaras RGBA8 de512² con mipmaps. Envoltorio **Lineage2Ver121**, clave del nombre exacto instalado, CRC32 y paquete descifrado idéntico al UCC verificados. El paquete UCC crudo permanece como fuente AmberSurfaceV1.raw; no instalarlo en lugar del UTX codificado. La finalización corrigió el primer despliegue crudo antes de entregar, con L2 cerrado, conservando el respaldo y actualizando el manifiesto. No hubo prueba de arranque con ese archivo intermedio.

Respaldo: {backup}. Restore.ps1 verifica hashes y cliente cerrado antes de restaurar; no sobrescribe cambios posteriores. La dependencia nueva puede quedar sin uso después de restaurar. Stage, pruebas, hashes e instalación: research/amber-l2/exports/surface-v1. Constructor build_amber_surface_v1.py, linker link_amber_surface_v1.groovy, verificador verify_amber_surface_v1.py, instalador Install-AmberSurfaceV1.ps1. No volver a ejecutar linker sobre los paquetes ya modificados como si fueran el original; usa el backup si reconstruís desde cero.

Validación: lectura nativa de los cuatro shaders y todas sus dependencias; los cuatro mapas exportados conservan exactamente RGBA y512²; PSK de ambas mallas idénticos al respaldo, y comparación de todos los exports ajenos a shaders. UTX121/clave/CRC/roundtripPASS. Los avisos xDxTex ausente de UCC no impidieron la compilación: se verificó formato RGBA8 y píxeles exportados. Galería643 registros/642miniaturas con todos los enlaces presentes. Chrome headless aislado cargó tres vistas en estudio/oscuro/difusa oscura sin excepciones, capturas en research/model-catalog/amber-comparison/surface-v1/*-verified.png. En oscuro V1 responde al ambiente y la anterior sigue completamente iluminada. La simulación glTF no reproduce los reflejos TexEnvMap ni todo el renderer UE2.

Comparador: http://127.0.0.1:32280/comparar.html, o GALERIA-MODELOS-L2.cmd. Izquierda=antes, centro=V1, derecha=NPC nativo seleccionable. Miniaturas NPC y summon actualizadas. El preview usa exactamente las máscaras nativas y mezcla de color en espacio lineal, sin simular el TexEnvMap; el resultado ingame debe valorarse con el cliente.

**Pendiente: valoración visual en L2**, con Amber NPC y summon en exterior e interior/zonas oscuras, girando la cámara para ver reflejos y transparencias. No se inició sesión con Hellkevin ni se probaron animaciones ingame en esta revisión. No se modificaron servidor, IA, stats, catálogos DAT ni interfaz. Continuidad W10/W11 y Nexus central/portable guardada. Código y documentación espejados en cloud-repo local; sin commit/push.
'''
(PROJECT/'AMBER-INTEGRACION-VISUAL-V1.md').write_text(doc,encoding='utf-8')
previous=PROJECT/'AMBER-INTEGRACION-VISUAL-COMPARATIVA.md'
with previous.open('a',encoding='utf-8') as f:f.write('\n\nActualización 12/10/2026: se instaló la integración de materiales V1; ver AMBER-INTEGRACION-VISUAL-V1.md. Este documento describe la auditoría anterior. El comparador ahora muestra antes/V1/nativo.\n')
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    filename='AMBER_INTEGRACION_VISUAL_V1_2026-10-12.md'
    (PROJECT/folder/filename).write_text(doc,encoding='utf-8')
    index=PROJECT/folder/'LEER-PRIMERO.md'
    if filename not in index.read_text(encoding='utf-8-sig'):
        with index.open('a',encoding='utf-8') as f:f.write('\n- '+filename+': materiales V1 instalados NPC/summon, máscaras por superficie, UTX121; falta valoración ingame.\n')
note='# Amber materiales V1 instalada — 12/10/2026\n\nProyecto E:\\l2-local. Usuario autorizó retoques. Reducida autoiluminación con máscaras por superficie y reflejo nativo TexEnvMap en metal/pelo/ojos. Dos UKX actuales conservan nombre y solo cambian dos shaders cada uno; malla/texturas artísticas/animaciones idénticas. Nuevo AmberSurfaceV1.utx512²×4, wrapper121/CRC/nombre/roundtrip nativoPASS. Lectura nativa y export PSK exactoPASS; preview3casos navegadorPASS. Galería actual643/642. Instalado cliente cerrado, sin restart GS/IA/stats/DAT. Falta valoración ingame; no afirmar validación visual real UE2. Doc AMBER-INTEGRACION-VISUAL-V1.md y stage research/amber-l2/exports/surface-v1, backup '+str(backup)+' con Restore.ps1 protegido. Comparador localhost32280/comparar.html antes/V1/nativo; glTF no reproduce reflejos TexEnvMap. No ejecutar finalizadores/linkers históricos sobre estado actual. Continuidad portable W10/W11, central K y cloud local (sincommitpush).\n'
for nexus in [Path('K:/_CodexNexus'),PROJECT/'CONTINUIDAD-W11/Nexus']:
    (nexus/'inbox/20261012-amber-surface-v1.md').write_text(note,encoding='utf-8')
    with (nexus/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
files=[ROOT/'Install-AmberSurfaceV1.ps1',*[ROOT/'scripts'/name for name in ['build_amber_surface_v1.py','link_amber_surface_v1.groovy','verify_amber_surface_v1.py','finalize_amber_surface_v1.py']]]
files += [PROJECT/'research/model-catalog'/name for name in ['comparar.html','comparar.js','gallery.json','verification.json','amber-comparison/variants.json','amber-comparison/prepare_surface_v1.py','amber-comparison/update_surface_page.py','amber-comparison/browser_verify.py']]
for file in files:
    relative=file.relative_to(PROJECT);dest=PROJECT/'cloud-repo'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
for name in ['AMBER-INTEGRACION-VISUAL-V1.md','AMBER-INTEGRACION-VISUAL-COMPARATIVA.md']:shutil.copy2(PROJECT/name,PROJECT/'cloud-repo/docs'/name)
print('PASS: installed encoded mask, native dependency loading, final hashes, browser comparison and gallery links; continuity/backup/cloud source saved. In-game visual test pending.')
