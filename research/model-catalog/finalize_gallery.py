from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
proof=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
assert proof['readable_models_and_thumbnails']==640 and proof['all_asset_links_present'] and not proof['uniform_thumbnail_candidates']
assert json.loads((OUT/'browser-verification.json').read_text(encoding='utf-8'))['headless_search_pass']
proof['viewer_api']={'known_model':200,'unknown_model':400,'foreign_origin':403,'native_window':'UE Viewer build1590 responding'}
proof['alpha_correction_models']=129
(OUT/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
cloud=ROOT/'cloud-repo/research/model-catalog';cloud.mkdir(parents=True,exist_ok=True)
for p in OUT.rglob('*'):
    relative=p.relative_to(OUT)
    if not p.is_file() or any(part.startswith('qa-') or part in {'exports','thumbs','logs','build-logs','__pycache__'} for part in relative.parts):continue
    if p.suffix not in {'.js','.py','.ps1','.json','.css','.html','.txt','.md'}:continue
    q=cloud/relative;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ['VER-MODELOS-L2.cmd','GALERIA-MODELOS-L2.cmd']:
    shutil.copy2(ROOT/name,ROOT/'cloud-repo/ops/windows'/name)
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    doc=ROOT/folder/'GALERIA_MODELOS_L2_2026-10-12.md';shutil.copy2(OUT/'README.md',doc)
    index=ROOT/folder/'LEER-PRIMERO.md'
    if doc.name not in index.read_text(encoding='utf-8-sig'):
        with index.open('a',encoding='utf-8') as f:f.write('\n- '+doc.name+': galería local con 640 miniaturas, vista 3D, favoritos/notas e IDs; visor reparado con SDL2.\n')
note='''# Galería L2 y visor reparado — 12/10/2026
Proyecto E:\\l2-local. Kevin pidió generar galería y corregir el menú que se cerraba. Causa reproducida: SDL2.dll ausente; UModel podía listar/exportar pero fallaba al crear ventana. Se agregó DLL x86 del repo oficial gildor2/UEViewer/libs/SDL2/x86 (hash en research/model-catalog/verification.json). Open-L2Models.ps1 ahora comprueba dependencia, registra errores y verifica inicio; CMD conserva ventana/mensajes. Ventana UE Viewer build1590 abierta y respondiendo, también mediante API de galería.
GALERIA-MODELOS-L2.cmd abre app local en 127.0.0.1:32280, Node portable y Three.js r160 incluidos. Funciones: búsqueda por nombre/ID/malla, filtros, miniaturas, WebGL giratorio, abrir malla en visor con animaciones, favoritos/notas, exportar selección JSON, elegir/copy ID de referencia. Favoritos son del navegador; exportarlos para otra PC. Sin Internet/Blender para uso, rutas portátiles ../l2. No toca GameServer, cliente, stats ni IA; no hay reinicios.
641 referencias/objetos deduplicados: 640 glTF + PNG 384x420; enlaces de bin/texturas PASS, ninguna imagen uniforme vacía. LineageMonsters.alchemic_box_m00 solo está referenciado en catálogo base y falta en cliente; recurso marcado no disponible. 72 vistas con algún material sin textura (muchas mallas sin NPC asociado); fichas lo indican. Poses base/materiales representativos, sin partículas/reflejos ni animación en WebGL. NPC de referencia no cambia colores automáticamente. Shader alpha especular corrigió 129 cuerpos que aparecían recortados. Capturas de Chrome headless aislado validan grilla, WebGL Gremlin y búsqueda ID29020=>Baium. API origen inválido403/modelo inválido400/modelo válido200. UI native helper no disponible; validación de ventana por proceso, no captura nativa.
Código y todos los recursos para usar están en research/model-catalog del disco portátil; Blender3.5.1 D:/BlenderVersions solo generó miniaturas. Cloud-repo guarda código/metadata/vendor, sin commit/push; recursos generados y SDL binario permanecen en E, no subidos. Respaldos accesos anteriores en backups/model-gallery-2026-10-12. README y continuidad W10/W11, Nexus central y portable actualizados. Usar galería para elegir próximos NPC/summons; bots Player requieren revisar capa visual/animaciones.
'''
for nexus in [Path('K:/_CodexNexus'),ROOT/'CONTINUIDAD-W11/Nexus']:
    (nexus/'inbox/20261012-l2-model-gallery.md').write_text(note,encoding='utf-8')
    with (nexus/'sessions/lineage2-local.md').open('a',encoding='utf-8') as f:f.write('\n'+note)
print('Gallery/640 thumbnails/browser/viewer PASS; docs, mirrors and Nexus saved. Generated assets stay on portable disk.')
if __name__=='__main__':pass
