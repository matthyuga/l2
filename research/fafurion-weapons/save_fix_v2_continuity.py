from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
note='''

## Fafurion V2: shop y tooltip — 12/10/2026

Kevin mostró capturas: Avenger comprado/equipado e inventario281/132 correcto; multisell mostraba null/0/vacíos y tooltip arrastraba SA ajena. Corregidos alias visuales24130–24136 (campo short de MultiSellList salía negativo para54130–54136) y terminador NUL faltante en descripciones. DAT mantiene entradas altas y añade7alias; originales ajenos1313/9208 intactos. Templates54130–54136 ahora displayId24130–24136 en runtime/source/cloud; solo campo displayId cambiado en objetos de GS17204, sin reemplazar templates ni DB/inventarios/armas compradas/stats/precios. Itemnames14 Fafurion terminados; descripción simple Arma de grado S. No hay SA real nueva.

L2 se observó cerrado e instalación hecha. Verificación incluye paquete multisell real antes/después: signedshort negativo reproducido,7IDs positivos después; costes e IDs persistentes de productos conservados. verify_installation.py PASS actualizado aV2. Confirmación visual tras reabrir pendiente. Backup backups/fafurion-client-fix-v2-20261012-205047, manifiestos originales archivados; stage y pruebas research/fafurion-weapons/client-fix-v2. No reejecutar instaladores/agentes. Conservar cliente alias+XMLdisplayId juntos en otra PC. Rootdoc/README/continuidad/cloud actualizados, sin commit/push.
'''
for rel in ['CAMBIO-DE-PC-CONTINUIDAD.md','CONTINUIDAD-W10/FAFURION_ARMAS_2026-10-12.md','CONTINUIDAD-W11/FAFURION_ARMAS_2026-10-12.md']:
    with (root/rel).open('a',encoding='utf-8') as out:out.write(note)
cloud=root/'cloud-repo'
shutil.copy2(root/'FAFURION-ARMAS-INTEGRACION.md',cloud/'docs/FAFURION-ARMAS-INTEGRACION.md')
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    shutil.copy2(root/folder/'FAFURION_ARMAS_2026-10-12.md',cloud/folder/'FAFURION_ARMAS_2026-10-12.md')
for name in ['README.md','build_integration.py','fix_client_v2.py','FafurionDisplayFixV2.java','verify_installation.py','manifest.json','verification.json']:
    shutil.copy2(root/'research/fafurion-weapons'/name,cloud/'research/fafurion-weapons'/name)
target=cloud/'research/fafurion-weapons/client-fix-v2';target.mkdir(exist_ok=True)
for name in ['manifest.json','runtime-verification.txt']:
    shutil.copy2(root/'research/fafurion-weapons/client-fix-v2'/name,target/name)
for inbox in [Path('K:/_CodexNexus/inbox'),root/'CONTINUIDAD-W11/Nexus/inbox']:
    if inbox.is_dir():(inbox/'20261012-lineage2-fafurion-client-v2.md').write_text(note.strip()+'\n',encoding='utf-8')
print('Continuidad V2 y cloud local actualizados.')
