# Sincronización del portátil con GitHub

29/10/2026, Argentina. Continuación de la entrega documental `30d6839` y de la tarea pendiente de Windows 10. Raíz operativa encontrada en Windows 11: `D:\l2-local`.

## Qué se conserva

- Overlay de fuentes de Mobius basado en `d47756357`, actualizado desde el checkout del portátil. Se incorporan también módulos Java presentes en los scripts instalados del servidor.
- Panel del laboratorio, laboratorio de ideas, código del laboratorio de animación, lanzadores y utilidades propias.
- Código de catálogo y editor de escenas, scripts de investigación y desarrollo, datos descriptivos necesarios y documentación narrativa/técnica. Las herramientas que dependen de modelos locales siguen necesitando esos recursos.
- Bitácoras actuales de la raíz, incluida la continuidad y la revisión de personajes contemporáneos de la campaña. Las propuestas narrativas no se convierten en funciones implementadas ni en canon aprobado.

La entrega documental previa permanece integrada. El inventario del disco confirmó los **23 modificados y 1.384 sin seguimiento** de cloud-repo, y los **86 modificados y 2.766 sin seguimiento** de Mobius source registrados en Windows 10. Una gran parte de los archivos de source sin seguimiento eran compilados; esos números no equivalen a cambios de código publicables.

## Criterio entre copias

`cloud-repo`, `source` y `server` tenían funciones distintas. El overlay se actualizó desde las fuentes reales; los módulos custom adicionales proceden del servidor instalado. El perfil publicado WorldContent incluye BehemothNativeRide, presente en la configuración instalada. No se sobrescribieron fuentes, configuración ni binarios del servidor operativo con la copia antigua de GitHub.

Las diferencias de formato en StartingLocation, SchemeBuffer, PetSkillData y su XSD se conservaron sin presentar cada diferencia binaria como cambio funcional. La declaración XML `encoding='utf8'` de hair-accessories se normalizó a `utf-8` en la copia publicable. La geodata difiere entre source y runtime y permanece local, junto con los assets; el repositorio no pretende reconstruir esas piezas binarias.

Se mantuvo un respaldo local previo de los 2.405 archivos reconocidos del clon, su diff binario y un bundle Git en `backups/github-sync-20261029/`. No es parte de la publicación.

Se normalizaron los finales de línea de la copia publicable y se explicitaron los formatos de fuentes en `.gitattributes`. Quince documentos de Nexus del commit documental anterior tenían finales de línea incompatibles con sus atributos; se conservó su texto al normalizarlos. El manifiesto calcula sus hashes sobre los blobs de Git, después de esa normalización.

## Validación

- Compilación aislada del núcleo con el JDK 25 y Ant portátiles: **1.625 fuentes Java**, resultado satisfactorio.
- Compilación de **134 scripts Java del overlay** contra ese núcleo y las dependencias locales, con resolución de dependencias de scripts desde el datapack compatible.
- Tests existentes: CombatPolicy **335**, GroupPolicy **291**, EnchantCatalog **2.438**, NoctisPolicy **108** y PilotPacket **4** comprobaciones; **3.176** en total. EnchantCatalog leyó las 484 rutas del datapack de fuentes compatible.
- Revisión de sintaxis JavaScript, PowerShell, JSON y XML de los archivos seleccionados; resultados detallados en el manifiesto de esta sincronización.
- Revisión de patrones de credenciales, claves privadas y tokens antes de preparar el commit.
- Comprobación del panel mediante su comando `npm run check`, también usado por GitHub Actions.

Estas comprobaciones no ejecutan instaladores históricos ni sustituyen una sesión de prueba dentro de L2. No se adjuntaron agentes a GameServer, no se restauró SQL y no se tocaron personajes.

## Exclusiones

Permanecen locales los clientes, texturas, modelos, geodata, binarios de terceros, JAR y clases compiladas, bases activas y respaldos SQL, configuración privada, perfiles del navegador, conversaciones completas, favoritos personales y capturas de runtime. Se excluyen asimismo páginas web descargadas y árboles externos de referencia que no son fuentes propias del proyecto.

Los scripts de pruebas e instaladores se conservan como herramientas e historia del desarrollo: no deben ejecutarse en bloque para restaurar el servidor. Algunos conservan rutas históricas `E:` o dependen de herramientas y assets locales. Revisar su README y adaptar la ruta antes de utilizarlos.

La sincronización de fuentes no instala propagación automática entre Lab, Hellgames y Academy. Sus bases y entornos siguen separados.
