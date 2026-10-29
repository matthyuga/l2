from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).resolve().parent;OUT=HERE.parent;ROOT=OUT.parents[1]
audit=json.loads((HERE/'audit.json').read_text(encoding='utf-8'))
browser=json.loads((HERE/'browser-proof.json').read_text(encoding='utf-8'))
assert len(browser['cases'])==3 and all(c['loaded'] for c in browser['cases'])
for row in audit['installed_rows']:
    p=ROOT.parent/'l2/animations'/(row['mesh'].split('.')[0]+'.ukx')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['package_sha256']
assert all(row['full_self_illumination'] for row in audit['installed_rows'])
gallery=json.loads((OUT/'gallery.json').read_text(encoding='utf-8'));assert len(gallery['models'])==643
proof=json.loads((OUT/'verification.json').read_text(encoding='utf-8'));assert proof['readable_models_and_thumbnails']==642
proof['amber_comparison']={'installed_packages_unchanged':True,'installed_catalog_read_only':True,'browser_cases':browser['cases'],'simulation_only':True}
(OUT/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
for p in OUT.rglob('*'):
    relative=p.relative_to(OUT)
    if not p.is_file() or any(part.startswith('qa-') or part in {'exports','thumbs','logs','build-logs','__pycache__'} for part in relative.parts):continue
    if p.suffix not in {'.js','.py','.ps1','.json','.css','.html','.txt','.md'}:continue
    dest=ROOT/'cloud-repo/research/model-catalog'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
doc=ROOT/'AMBER-INTEGRACION-VISUAL-COMPARATIVA.md';shutil.copy2(doc,ROOT/'cloud-repo/docs'/doc.name)
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    target=ROOT/folder/'AMBER_COMPARACION_VISUAL_2026-10-12.md';shutil.copy2(doc,target)
    index=ROOT/folder/'LEER-PRIMERO.md'
    if target.name not in index.read_text(encoding='utf-8-sig'):
        with index.open('a',encoding='utf-8') as f:f.write('\n- '+target.name+': Amber en galería y comparador de iluminación; shaders actuales autoiluminados, pruebas solo simuladas.\n')
note='''# Amber: comparación visual — 12/10/2026
E:\\l2-local. Usuario nota integración visual insuficiente (texturas/shaders/luz). Se descifró npcgrp actual solo para lectura:59001=>L2AmberNPCv5.AmberNPC (servidor902500),59002=>L2AmberArcherV2.AmberNPC (servidor902501). Ambos52153tri/76huesos,2atlas2048². Dump real: cuerpo/ropa Diffuse=SelfIllumination misma textura, máscaraNone, Specular/SpecularityMaskNone, maskedAlpha128/ZWrite/TwoSided. V4 había autoiluminado ambos para corregir ropa muy oscura. No cambia paquetes del cliente ni server.
Añadidas 2 entradas Personalizados: galería643 registros/642miniaturas. Comparar en http://127.0.0.1:32280/comparar.html desde GALERIA-MODELOS-L2.cmd. Tres vistas giratorias: actual aproximado unlit, prueba difusa o mezcla20% aproximada, NPC nativo seleccionable; luz estudio/oscura. Referencia Katerina1974tri/78huesos/texturas512²×2 y256²×2. Simulación no equivalencia exacta UE2; sin cambios ingame. Próximo ajuste sugerido: reducir/máscara selfillum, diferenciar superficies, luego tonos/detalles; LoD/compresión separado. Chrome headless propio con CDP esperó carga completa: estudio/oscuro/difusa-oscura PASS y capturas *-verified.png, sin JS excepciones. Capturas previas con tiempo virtual fueron prematuras/incompletas y no sirven como prueba.
Auditoría/hashes/dumps/prototipos/capturas en research/model-catalog/amber-comparison; AMBER-INTEGRACION-VISUAL-COMPARATIVA.md. HashUKXdespués=antes;642assets/thumbs/enlacesPASS. Builder preserva custom entries y soporta texturas de UKX además de UTX. Código/metadata en cloud local, recursos y continuidad W10/W11 en portátil, Nexus central y copia portable. Sin commit/push/reinicio GameServer. No ejecutar finalizadores históricos con conteos640 como si fueran el estado actual.
'''
for nexus in [Path('K:/_CodexNexus'),ROOT/'CONTINUIDAD-W11/Nexus']:
    (nexus/'inbox/20261012-amber-visual-comparison.md').write_text(note,encoding='utf-8')
    with (nexus/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
print('Amber current model/material audit, comparison browser and unchanged client hashes PASS; mirrors and Nexus saved.')
