from pathlib import Path
import json,hashlib,re,shutil,datetime
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent
log=(root/'logs/game-stderr.log').read_text(errors='replace')
m=re.search(r'SkillCatalogVerification SUCCESS: (\d+) checks',log)
assert m and 'SkillCatalogVerification FAILED' not in log,'Catalog checks not finished/passed'
assert 'Roster Coliseo: 19 perfiles Player preparados' in log,'Wait for all 19 rivals'
assert 'No se preparo el perfil normal' not in log
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
installed=json.loads((stage/'installed-hashes.json').read_text())
assert all(sha(Path(p))==expected for p,expected in installed.items()),'Installed client/core changed concurrently'
proof={'at':datetime.datetime.now().isoformat(),'status':'PASS','checks':int(m[1]),'roster_ready':19,
 'game_pid':int((root/'run/game.pid').read_text().strip()),'native_bypass':'FinalFunction plus exact server allowlist, independent of HTML',
 'group_layout':'6 tiles per thick named separator; fresh rows; active/passive independently',
 'next_class':'actual owned slots; verified with 1,2,3,4 classes using registered voice bypass handler',
 'gameplay':'learned skills, levels, active class and shortcuts unchanged',
 'ui_review':'Native bytecode/data/layout checks PASS; visual in-game review pending user',
 'mode':'one-shot catalog verification completed; no ongoing tests; ordinary next launcher boot uses verify=false'}
(stage/'verification.json').write_text(json.dumps(proof,indent=2))
shutil.copy2(root/'logs/game-stderr.log',root/'backups/skill-groups-v3-2026-10-10/catalog1312-roster19-pass.log')
text=f'''# Habilidades por clase: catalogo nativo V3 — 10/10/2026

Instalado en el cliente habitual `l2/system-hud` que abre `2-JUGAR.cmd`.

## Uso

Abrir Alt+K. `Todas` muestra Principal, Subclase1-3, Comunes, Amber y Especiales (solo grupos con habilidades).
Cada grupo empieza debajo de una franja dorada gruesa de una fila completa. Se rellena el final de la fila anterior para que la siguiente clase no se mezcle en ella.
Las pestanas activas/pasivas conservan la separacion y el scroll. Los iconos reales se siguen arrastrando a la barra.

`Principal`, `Sub1`, `Sub2`, `Sub3` filtran una clase; incluyen sus habilidades compartidas compatibles.
`Siguiente clase >` recorre unicamente la principal y las subclases existentes, y vuelve a la primera. En chat informa nombre y posicion (por ejemplo2/4).
Comunes y Amber tienen filtros separados; `Todas` restaura la lista completa. `Nombres / indice` abre el indice con nombres completos y recuentos.
Alternativas de chat: `.habilidades next`, `.habilidades quick -1`, `.habilidades`.

## Causas corregidas

El callback llamaba RequestBypassToServer como VirtualFunction aunque la funcion es final/nativa. Ahora usa el mismo FinalFunction/import que los callbacks originales del cliente.
El servidor exigia cache HTML a las llamadas del panel nativo. RequestBypassToServer ahora exime solo diez acciones exactas del catalogo/IA de Amber. Otros bypass conservan la validacion; quick valida ademas la clase poseida y se mantiene flood protection.
Los botones tienen texto en su propia textura, sin TextBox superpuesto sobre la superficie que recibe el clic.

## Presentacion y preservacion

Decoracion de UI19100-19141 y relleno19199 solo en SkillList, nunca concedidos ni definidos como skills del servidor. En el cliente se convierten en elementos bloqueados con ClassID/Level/ItemSubType cero, comando vacio y guardia que impide UseSkill(0). Columnas6, iconos32, gapX0 para franja continua.
Nuevo paquete aislado SkillGroupsV3.utx con70 texturas, wrapper Lineage2Ver121 con clave de nombre, checksum y decode verificados. Catalogos DAT413 agregan43 filas; todas las filas previas, incluido AmberV10, son identicas.
Interface.u cambia solo cuatro funciones: MagicSkillWnd.OnClickButton/OnClickItem/HandleSkillList y SummonedWnd.OnClickButton. XDAT cambia solo MagicSkillWnd. JAR cambia SkillList, SkillCatalogView/Model y RequestBypassToServer. El resto es identico a respaldo; no se cambian estadisticas, habilidades aprendidas, clase, accesos rapidos ni Amber/roster.

## Validacion y estado

{proof['checks']} comprobaciones PASS: wire/opcode/recuento, atributos de cada skill real, franjas y alineacion independientes activa/pasiva, filtros completos y compartidos, toggle Amber, whitelist exacta, recorrido de1-4 clases mediante handler nativo registrado y ausencia de mutaciones de juego.
Paquete recompilado y releido: saltos VM correctos, import final nativo correcto y guardia de cero validos. DAT y textura roundtrip/checksum PASS. Roster19/19 preparado.
Verificacion automatica one-shot terminada y probe offline retirado. Servidor disponible; el proximo arranque habitual lleva verify=false. Falta validar el aspecto y clics dentro del cliente con el usuario: estos checks no equivalen a una captura de Alt+K en juego.
Una primera corrida del verificador fallo al intentar construir Script fuera del cargador; se corrigio para usar el handler registrado. Segunda corrida PASS completa. La causa fue del verificador, no del filtro de produccion.

Respaldo: `backups/skill-groups-v3-2026-10-10`. Pruebas/hashes/build: `research/client-comfort/v3`. Fuente/runtime/cloud sincronizados sin commit/push. Mantener juntas las carpetas l2 y l2-local al llevar el disco.
'''
doc=root/'SKILLS-GRUPOS-NATIVOS-V3.md';doc.write_text(text,encoding='utf-8')
for folder in ('CONTINUIDAD-W10','CONTINUIDAD-W11'):
    name='28_SKILLS_GRUPOS_NATIVOS_V3_2026-10-10.md'
    shutil.copy2(doc,root/folder/name);shutil.copy2(doc,root/'cloud-repo'/folder/name)
    first=root/folder/'LEER-PRIMERO.md';addition='\n## Catalogo nativo V3 — estado actual 10/10/2026\n\nVer `'+name+'`: filtros Alt+K corregidos (llamada final nativa + whitelist exacta sin HTML), franjas gruesas por clase en activas/pasivas y Siguiente clase para1-4 clases. '+str(proof['checks'])+' checks PASS, roster19/19. Cliente habitual2-JUGAR. Reemplaza la descripcion anterior de controles V2; prueba visual dentro del juego pendiente.\n'
    if name not in first.read_text(encoding='utf-8-sig'):first.write_text(first.read_text(encoding='utf-8-sig')+addition,encoding='utf-8')
    shutil.copy2(first,root/'cloud-repo'/folder/'LEER-PRIMERO.md')
shutil.copy2(doc,root/'cloud-repo/docs'/doc.name)
mirror=root/'cloud-repo/research/client-comfort/v3';shutil.copy2(stage/'verification.json',mirror/'verification.json')
note='FINALIZADO catalogo nativoV3; ventana GameServer libre. '+str(proof['checks'])+' checks PASS, roster19/19. Alt+K filtra via FinalFunction correcto y whitelist exacta de acciones sin HTML. Franjas por grupo/filas separadas activo-pasivo; Next recorre solo clases poseidas1-4. Nuevo SkillGroupsV3.utx121 validado +43 DAT decorativas preservando todas filas previas. No skills aprendidas/estadisticas/shortcuts modificadas; Amber/roster intactos. Cambios core limitados a SkillList, SkillCatalogView/Model y RequestBypassToServer (10 acciones exactas). Backup skill-groups-v3-2026-10-10; continuidad28 y SKILLS-GRUPOS-NATIVOS-V3.md. Fuentes/cloud sincronizados, sin commit/push. Visual y clics in-game pendientes del usuario.\n'
Path('K:/_CodexNexus/inbox/20261010-lineage2-skill-groups-v3.md').write_text(note,encoding='utf-8')
Path('K:/_CodexNexus/inbox/20261010-lineage2-skill-groups-v3-in-progress.md').write_text('FINALIZADO, ventana liberada. Ver 20261010-lineage2-skill-groups-v3.md.\n',encoding='utf-8')
session=Path('K:/_CodexNexus/sessions/lineage2-local.md');addition='\n10/10/2026: catalogo nativoV3: franjas gruesas por clase en Alt+K, filtros corregidos en cliente/servidor y Siguiente clase solo slots poseidos. '+str(proof['checks'])+' checks PASS, roster19/19. Continuidad28; inbox/20261010-lineage2-skill-groups-v3.md. Visual/clics in-game pendientes.\n'
if '20261010-lineage2-skill-groups-v3.md' not in session.read_text(encoding='utf-8-sig'):session.write_text(session.read_text(encoding='utf-8-sig')+addition,encoding='utf-8')
print(json.dumps(proof,indent=2))
