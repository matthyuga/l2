# Tres modelos de Amber para comparar en L2

## Correccion posterior: Critical Error GetNpcTexName

El usuario mostro critical al invocar/cambiar a MMD: `Assertion failed: index < 5 [L2NetHandler.cpp:1439]`, historial `User::GetNpcTexName -> User::SetPawnResource -> PetInfoPacket`. La version inicial de ocho slots excedia el limite de cinco de esta ruta del cliente. Las39 pruebas de servidor no comprobaban este limite nativo; la validacion inicial era insuficiente para asegurar que el cliente pudiera mostrar el summon.

**Version vigente: cuatro materiales**. Cara/blanco de ojos comparten FaceTex; ojos/pelo HairTex; piel/ropa/accesorio OutfitTex; expresiones ExpressionTex. Todos los shaders anteriores de cada grupo tenian el mismo comportamiento y textura, por lo que se agrupan sin crear atlas, cambiar UV o reducir la resolucion. Cada malla y fila npcgrp usa indices0..3. Se recompilaron ambos paquetes, se releen con UModel forzadoL2 y se verifican triangulos orientados/UV/materiales, pesos,76 huesos y seis texturas pixel-identicas.52 controles de paquete/catalogoPASS. Solo cambian dos filas existentes del DAT, sin alterar las restantes.

Instalada correccion con L2 cerrado el23/10 a11:09:51 aproximadamente; backup `E:/l2-local/backups/amber-four-slots-20261023-110944`. No se reinicio GameServer ni se cambiaron scripts. Manifest vigente `research/amber-l2/exports/mmd-variants-fix4-20261023/installed.json`. El staging inicial de8slots es historico; su instalador ahora rechaza cualquier modelo con mas de5. Usar `Install-AmberFourSlotsFix.ps1`. Pendiente confirmacion visual del usuario con `.ambers 2` y `.ambers 3`; no declarar el critical resuelto en una prueba real de cliente hasta esa confirmacion.

Los apartados de ocho materiales mas abajo describen la primera integracion, sustituida por esta correccion. La prueba de39checks de servidor sigue siendo valida para la seleccion y preservacion de estado, no para el render del cliente.

## Uso

Abrir `2-JUGAR.cmd`, entrar como GM y escribir **`.ambers`**. Tambien aparece **Comparar modelos de Amber** en el menu `.amber`.

- `.ambers 1`: actual, procedente de Koikatsu, conservada.
- `.ambers 2`: MMD1.0, modelo detallado de47.378 triangulos.
- `.ambers 3`: MMD1.4 / carpetaAmber2.0, modelo de15.794 triangulos.

Si Amber ya esta invocada, cambia de aspecto inmediatamente fuera de combate. No se retira ni se crea otro actor: conserva objectId, vida, MP, efectos, shots cargados y recargas. Si no esta invocada pero existe contrato, el selector intenta la invocacion habitual (respeta su recarga). Sin contrato, selecciona el modelo para despues de firmar con Amber. Un summon a la vez. La seleccion queda en la variable `AMBER_MODEL_VARIANT`; defecto1.

Probar cada una quieta, siguiendo al personaje, disparando al mismo enemigo y usando fuego/lluvia. Para cambiar, terminar el combate y esperar a que no haya ataques ni habilidades en curso. Volver a1 conserva acceso al modelo original.

## Integracion

Paquetes nuevos `E:/l2/animations/AmberMMD10.ukx` y `AmberMMD14.ukx`. Displays59020/59021; plantillas NPC902520/902521. Son clones de la plantilla de combate902501 excepto id/displayId. Mismo `AmberServitor`, arco6619, habilidades19002/19003, colision y recursos. La clase cliente se conserva `AmberActorsV1.AmberArcher`, con sus enganches de arma. La animacion reutiliza el paquete instalado `L2AmberArcherMotion.FFighter_anim`.

Adaptacion: PMX160 huesos -> esqueleto nativo76, resolucion de huesos auxiliares a ancestro mapeado y un maximo de4 influencias normalizadas. Se conservan todos los triangulos, UV y ocho materiales separados; no se aplica decimacion ni atlas nuevo. Cara, pelo y ropa siguen2048x2048. Mapas auxiliares no potencia de2 se adaptan para UE2 (toon800->1024, expresiones1181->2048). Se preservan fuentes originales fuera del cliente.

Shaders en esta version: color base autoiluminado, alpha recortado128, doble cara y escritura de profundidad. No son una reproduccion completa de MToon/Genshin. Expresiones PMX, IK y fisicas originales no se transportan a L2; el movimiento usa las animaciones nativas de arquera, incluida lluvia existente. Pelo y accesorios siguen sus huesos adaptados, sin simulacion MMD independiente.

`npcgrp.dat` y `NpcName-e.dat`: solo se agregan dos registros en cada uno, preservando6523/6522 filas anteriores y sus colas. Recodificacion413 con roundtrip exacto. No se modifican skillgrp, efectos, iconos, Interface, INI ni core.

Servidor: `AmberContract` solo cambia seleccion de plantilla al invocar y agrega boton al menu. `AmberServitor` agrega metodo de cambio cosmetico. `AmberModelVariants` registra `.ambers`, bloquea estados incompatibles y reenvia DeleteObject/PetInfo/SummonInfo para refrescar la malla; `sendInfo` restaura tambien iconos de buff. XML de nuevas plantillas separado. Copias live/source-dist/cloud-overlay sincronizadas. Sin commit/push.

## Validacion y estado

- Dos compilaciones UCC: cero errores. Java contra core actual y scripts dependientes compila.
-82 comprobaciones de paquetes/catalogos: shaders, origen y rotacion nativos, enlace de animaciones, ocho slots y displays correctos.
- Exportacion de ambos paquetes con UModel forzadoL2: todos los triangulos orientados, UV por esquina, asignacion de materiales y posiciones se conservan. UCC suelda puntos coincidentes (nativos24.047 y8.145) conservando wedges/UV separados. No comparar esos puntos soldados con el conteo de vertices del PMX como si se hubieran perdido caras.
-76 huesos y jerarquia preservados. Todos los vertices nativos con pesos validos/normalizados. Las seis texturas de cada paquete vuelven pixel-identicas a los TGA preparados.
- Seis vistas Blender con PSA original de Fighter: reposo con arco, caminata y disparo para ambos modelos; sin huesos ausentes ni geometria no finita/explotada. Vistas revisadas en `research/amber-l2/exports/mmd-variants-20261023/animation-comparison.jpg`. Son comprobaciones Blender, no capturas del juego.
-19 archivos instalados coinciden con staging y nueve archivos protegidos conservan hashes: coreE84D1A7381650CFFD89EBE0A68F8CD27965F7A4B007D5CB7547D9D74FB32F099, Amber original y animacion, Interface/INI y DAT de habilidades/mensajes.

Instalado el23/10/2026 con cliente y GameServer cerrados. Backup `E:/l2-local/backups/amber-three-models-20261023-104529`. Manifest `research/amber-l2/exports/mmd-variants-20261023/installed.json`. GameServer iniciado (arranque frio291s). **Integracion PASS39 comprobaciones el23/10 a10:51:44**: mismos objectId/recursos/estadisticas/buff/shots/reuse en los tres modelos; invocacion nueva usa seleccion; bloqueo durante carga, opcion invalida y noGM. Log `research/amber-l2/reports/mmd-models-server-verification.log`. Pendiente valoracion visual del usuario dentro deL2. No se abrio cliente automaticamente.

Prueba opt-in `lab.amber.models.verify=true`: personaje reservado `AmberModelsProbe` de cuenta `ambermodeltest`, instancia privada; no usa Hellkevin. Comprueba seleccion/invocacion y preservacion de estado, permite solo GM y rechaza cambio durante carga. El flag se aplica solo al arranque de verificacion; constructor ejecuta una sola vez. Lanzador habitual no activa este flag.

Fuentes reproducibles en `research/amber-l2/scripts`: `build_amber_mmd_variants.py`, `compile_amber_mmd_variants.py`, `link_amber_mmd_variants.groovy`, `catalog_amber_model_variants.py`, `stage_amber_model_variants.py`, `verify_amber_mmd_assets.py`, `verify_amber_mmd_packages.groovy`, `preview_amber_mmd_poses.py`. Instalador `research/amber-l2/Install-AmberModelVariants.ps1` verifica hashes, cliente/servidor cerrados y respalda antes de copiar.

Modelos originales y reglas: `research/amber-l2/reference-models/amber-web-2026-10-23/COMPARACION.md`. No publicar binarios/modelos/texturas en el repositorio. No se modificaron entornos Hellgames ni Academy.
