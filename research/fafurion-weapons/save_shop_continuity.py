from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
note='''

## Fafurion en GM Shop — 12/10/2026

Por pedido de Kevin, siete armas54130–54136 a +0 disponibles en boton Fafurion de Mirella50010/Weapons (multisell50035413, 48.800.000 Adena cada una) y //gmshop/Weapons (buylist54130, gratis como otras listas administrativas). Cuatro HTML y dos XML nuevos sincronizados runtime/source/cloud local. Parser nativo verifica productos/precios/NPC y cache HTML; listas cargadas individualmente en GS17204, sin restart ni cambios de personajes/inventario. No se compro con personajes del usuario. No cambiar DAT/cliente. Backup backups/fafurion-shop-20261012-204201; research/fafurion-weapons/shop-installation.json y shop-verification.txt PASS. No reejecutar add_shop.py ni agente de carga. Documentacion FAFURION-ARMAS-INTEGRACION.md actualizada. Sin commit/push.
'''
for rel in ['CAMBIO-DE-PC-CONTINUIDAD.md','CONTINUIDAD-W10/FAFURION_ARMAS_2026-10-12.md','CONTINUIDAD-W11/FAFURION_ARMAS_2026-10-12.md']:
    with (root/rel).open('a',encoding='utf-8') as out:out.write(note)
cloud=root/'cloud-repo'
shutil.copy2(root/'FAFURION-ARMAS-INTEGRACION.md',cloud/'docs/FAFURION-ARMAS-INTEGRACION.md')
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
    shutil.copy2(root/folder/'FAFURION_ARMAS_2026-10-12.md',cloud/folder/'FAFURION_ARMAS_2026-10-12.md')
for name in ['README.md','add_shop.py','FafurionShopLoad.java','shop-verification.txt','shop-installation.json']:
    shutil.copy2(root/'research/fafurion-weapons'/name,cloud/'research/fafurion-weapons'/name)
for inbox in [Path('K:/_CodexNexus/inbox'),root/'CONTINUIDAD-W11/Nexus/inbox']:
    if inbox.is_dir():(inbox/'20261012-lineage2-fafurion-shop.md').write_text(note.strip()+'\n',encoding='utf-8')
print('Docs y continuidad actualizados.')
