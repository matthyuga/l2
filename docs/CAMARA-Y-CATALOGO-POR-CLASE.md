# Cámara y catálogo por clase — 2026-10-10

## Uso

- Entrar por `2-JUGAR.cmd` (cliente `../l2/system-hud`). La rueda permite alejar más la cámara: `MaxZoomingDist` pasa de 250 a 1800.
- Abrir habilidades con **Alt+K** y pulsar **Clases / Amber**. También se puede escribir `.habilidades` o `.skills`, o crear una macro con `.habilidades`.
- **Todas agrupadas** ordena principal, subclase 1, subclase 2, subclase 3, Comunes, Amber y Especiales; dentro de cada grupo, por nombre. Se mantienen las pestañas nativas de activas y pasivas.
- Elegir una clase filtra los iconos de Alt+K. Allí se pueden seguir arrastrando a la barra. Las compartidas aparecen en cada clase compatible; en Todas aparecen una sola vez, en Comunes.
- **Contrato Amber** permite encontrar **Asistencia de Amber**, el activable de IA. Requiere contrato vigente. El filtro no concede el contrato ni sus habilidades.
- Para recuperar toda la lista: **Todas agrupadas** o `.habilidades filter -1`. **Actualizar** relee las habilidades conocidas. El orden opcional «Activa primero» da prioridad a la clase actualmente seleccionada.

## Implementación

La ventana nativa `MagicSkillWnd` tenía `maxItemNum=80` tanto en activas como en pasivas. Ahora admite 2048 por sección. Conserva rejillas, pestañas, desplazamiento e iconos arrastrables. Se añade un botón mediante `Interface.xdat` y un callback mínimo en `Interface.u`: `RequestBypassToServer("voice .habilidades")`. Los exports anteriores de funciones y todas las demás ventanas se verifican idénticos.

La copia de `l2.ini` del cliente HUD prioriza `../system-hud/*.u` antes del fallback `../System/*.u`, para cargar su Interface. Las INI se modifican en bytes, preservando comentarios y codificación; ambas pasan encode413/decode con igualdad exacta.

El módulo `custom/SkillCatalog` construye el índice a partir de `baseClass`, los slots reales de subclase y `SkillTreeData.getCompleteClassSkillTree`. La pertenencia indica compatibilidad con el árbol; no reconstruye la historia de aprendizaje de un skill compartido. Sólo enumera skills actualmente conocidos. `SkillList` ordena y filtra la presentación sin alterar niveles, skills, clase activa, recursos ni accesos rápidos. Preferencias en variables `LAB_SKILL_CATALOG_FILTER` y `LAB_SKILL_CATALOG_ORDER`; los filtros inválidos vuelven a Todas.

Se modifica únicamente `SkillList.class` en el JAR existente y se agregan `SkillCatalogView.class` y `$Model.class`. Todos los demás entries se comparan byte a byte con el respaldo. No se recompila ni reemplaza Player ni los módulos de Amber, arena o razas. Los DAT y efectos V9 de la otra sesión se preservan.

## Verificación y respaldo

- Respaldo: `backups/client-comfort-2026-10-10/` (cuatro archivos cliente, JAR, fuente SkillList, launcher y logs previos).
- Staging, scripts reproducibles y pruebas: `research/client-comfort/`; JAR en `build/client-comfort/`.
- `verification.json`: diferencias mínimas de JAR, hashes originales y roundtrip de INI.
- `Install-ClientComfort.ps1`: exige cliente cerrado y cero conexiones de jugadores; rechaza cambios concurrentes por hash y verifica la identidad del GameServer antes de detenerlo.
- Prueba opcional: `Start-L2Local.ps1 -VerifySkillCatalog`. Sólo usa el personaje de laboratorio reservado y desconectado `AmberOwnerProbe`, sin guardar grants. Comprueba filtros de cuatro clases, compartidas, más de 80 activas, cinco skills de Amber, estructura binaria de SkillList y ausencia de cambios de skills, niveles, clase o shortcuts. `probe_snapshot.py` compara skills/subclases/shortcuts de la base antes y después.
- La prueba visual final de distancia, botón y rejilla corresponde al cliente; no se da por observada sólo por superar las validaciones de archivos.

Instalado y verificado: **471 comprobaciones PASS** el 10/10/2026 a las 14:58. También coincide el snapshot de base de datos del personaje reservado (skills, subclases y shortcuts). Resultado y hashes en `research/client-comfort/installed.json` y `research/client-comfort/verification-server.log`. La prueba se ejecutó una sola vez durante este inicio; no se repite mientras siga funcionando. Los próximos arranques habituales no activan el flag de verificación.

Dos iteraciones previas corrigieron el propio arnés: opcode esperado de Interlude `0x58` y `WriteBuffer.mark()` antes de exportar su contenido. La implementación del paquete no cambió durante esas correcciones. La tercera ejecución terminó correctamente.
