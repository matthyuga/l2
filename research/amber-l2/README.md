# Amber para Lineage II Interlude — laboratorio

Fecha: 2026-10-09. Estado: version visual v4 instalada y aprobada visualmente por el usuario dentro de L2 ("esta buena ahora"). Conservar como base; esta aprobacion no valida todas las animaciones, combate o rendimiento.

## Como probar

1. Abrir `E:\l2-local\2-JUGAR.cmd` (cliente habitual) o `13-PROBAR-AMBER.cmd` (perfil de laboratorio).
2. Entrar con un personaje GM.
3. Si el Game Server ya estaba abierto durante la instalacion, ejecutar `//reload npc`.
4. Ejecutar `//spawn 902500` cerca del personaje.

El NPC no tiene spawn automatico. El acceso habitual `2-JUGAR.cmd` sigue apuntando a `system-hud`.
Amber v4 esta integrada tanto en `system-hud` como en `system-amber`: ambos tienen su fila en `npcgrp.dat` y `NpcName-e.dat`.
Cerrar el cliente anterior antes de abrir el acceso: los catalogos se cargan al iniciar L2.

## Integracion en el acceso habitual

El usuario detecto que `2-JUGAR.cmd` mostraba un conejo porque `system-hud` aun tenia los catalogos originales.
Se comprobo igualdad binaria entre esos catalogos descifrados y la base original usada para construir Amber.
Se actualizaron solamente `system-hud/npcgrp.dat` y `system-hud/NpcName-e.dat`, conservando las 6.519 filas originales y agregando la de Amber. No se cambio el launcher; los recursos del modelo y animacion ya estaban en la carpeta compartida `animations`.
Los archivos estaticos `Interface.u` y `Interface.xdat` conservaron sus hashes. Se verifico el descifrado de ambos catalogos instalados.
Instalacion reproducible: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File research\amber-l2\Install-AmberMain.ps1`.
El instalador comprueba primero que no haya cambios ajenos a Amber y guarda una copia de los dos catalogos. Informe y ruta de copia en `reports/main-client-installation.json`.
Falta confirmar la vista dentro de L2 abierto especificamente por `2-JUGAR.cmd` tras reiniciar el cliente.

## Correccion tras la primera captura

La captura del usuario confirma el nombre y titulo de Amber sobre un conejo. Esto no valida la carga de la malla personalizada.
Se sustituyo `class_name=SkeletalMesh` por `LineageNPC.a_traderB_FHuman`, la clase real de la comerciante usada como plantilla.
Se comprobo que existe como export `Core.Class` en `system-amber/LineageNPC.u`.
Se agrego tambien el display 59001 a `NpcName-e.dat` (Amber / Prueba Koikatsu).
Ambos catalogos conservan todas las filas originales y pasan cifrado/descifrado con igualdad binaria.
La causa exacta del conejo aun no esta confirmada; tambien falta confirmar con que acceso se abrio aquella prueba.
Los catalogos previos se guardaron en `backups/before-npc-class-fix/`.

## Revision visual v3

La segunda captura confirma la importacion del personaje. Se corrigieron los siguientes puntos:

- El paquete anterior generaba cuatro niveles de detalle, cuyo ultimo nivel conservaba solo 3.154 triangulos. La revision conserva un solo nivel completo con 52.153 triangulos; UModel confirma `LodCount = 1`.
- El cuerpo y la ropa usaban pesos distintos, lo que producia interpenetraciones al adaptar la anatomia. La ropa ajustada ahora comparte el campo de deformacion del cuerpo; pelo y accesorio de cabeza conservan su vinculacion original.
- Se retiraron 9.406 caras internas de piel del torso y las piernas inferiores, cubiertas por la ropa fija, antes de reducir moderadamente la malla.
- La reduccion de geometria en Blender paso a 0,85 en ambas mallas. Los pesos nativos estan normalizados y tienen como maximo cuatro influencias por vertice.
- Se exportaron las secuencias originales de la comerciante y se adaptaron los nombres a `Wait_Hand`, `walk_hand`, `Run_Hand`, `AtkWait_Hand`, etc. Los nombres genericos anteriores no coincidian con esta clase.
- Los atlas ahora tienen bordes extendidos y UV coherentes con ese margen. Se comprobo igualdad de todos los pixeles RGBA entre las texturas de entrada y las exportadas del paquete compilado.
- La cara/piel mantiene iluminacion propia; la ropa y el pelo usan el material difuso. Ambos shaders escriben profundidad y recortan alpha con umbral 128.

Se revisaron reposo y caminata en Blender. El usuario luego mostro v3 dentro de L2: mejoro la forma, pero el traje y el pelo quedaron muy oscuros frente a la cara autoiluminada. La captura fija no permite validar todas las animaciones.
Para volver a v2: cerrar L2, ejecutar `Restore-AmberV2.ps1` y abrir de nuevo el perfil. Los catalogos v2 estan en `backups/before-visual-v3/`.

## Revision de materiales v4

Se aplica `SelfIllumination` a los dos atlas, conservando los colores toon ya incluidos en las texturas del personaje. En v3 solo el cuerpo/cara tenia ese tratamiento; el traje y el pelo recibian un sombreado muy oscuro en la arena.
V4 conserva byte por byte la malla exportada, sus pesos y el paquete de animaciones de v3. No modifica texturas ni geometria; mantiene profundidad, recorte alpha y el unico nivel de detalle completo. El usuario mostro luego v4 dentro de L2 y aprobo su aspecto y color. La captura fija no valida el movimiento ni el combate.
La revision usa `L2AmberNPCv4.ukx` y reutiliza `L2AmberMotionv3.ukx`. El catalogo del perfil aislado ya apunta al nuevo paquete.
Para volver a v3: cerrar L2, ejecutar `Restore-AmberV3.ps1` y abrir el perfil. Catalogos anteriores en `backups/before-material-v4/`.

## Archivos instalados

- `E:\l2\system-amber`: copia aislada de `system-hud` con `npcgrp.dat` propio.
- `E:\l2\animations\L2AmberNPCv4.ukx`: modelo, dos atlas y dos shaders.
- `E:\l2\animations\L2AmberMotionv3.ukx`: copia del paquete original Fighter, con nombres de secuencias de la humana adaptados a la comerciante (`Wait_Hand`, `walk_hand`, `Run_Hand`, etc.). Los datos nativos de animacion se conservan.
- `E:\l2-local\server\game\data\stats\npcs\custom\amber_lab.xml`.
- Copia de ese XML en `source\L2J_Mobius_CT_0_Interlude\dist\game\data\stats\npcs\custom`.

NPC del servidor: **902500**. Display del cliente: **59001**. Ropa fija, NPC amistoso e inmortal.

## Preparacion y comprobaciones

Fuente: `D:\codex periferico\VSeeFace\CodexAvatars\amber_MVP_001_auto.vrm`, generado anteriormente desde Koikatsu.
El original conserva 847 huesos. El prototipo usa los 76 huesos de la humana de Fighter.ukx,
22 correspondencias humanoides, 52.153 triangulos y dos atlas RGBA de 2048 x 2048.
Se retiraron variantes de ropa, lagrimas y ojos de expresiones adicionales.

La importacion de animaciones PSA mediante UCC genera datos incompatibles con UModel en este editor.
La ruta que paso las comprobaciones reutiliza las animaciones nativas: se agrega una referencia importada
en el campo nativo Animation de SkeletalMesh. El script identifica de manera unica la estructura completa
del esqueleto antes de modificar ese campo. Nunca modifica Fighter.ukx original.

Comprobaciones realizadas:

- UCC compila la malla y las texturas; UModel vuelve a leerlas y exportarlas.
- El paquete instalado resuelve `L2AmberMotionv3.FFighter_anim`.
- Ambos shaders se leen con `SelfIllumination`, `OB_Masked`, `TwoSided=true`, `ZWrite=true`, `AlphaTest=true` y `AlphaRef=128`.
- La geometria conserva caras, materiales y huesos en el recorrido PSK -> paquete -> PSK.
  El importador nativo une vertices duplicados; v3 conserva las posiciones sin desplazamientos.
- Todos los vertices tienen pesos validos; error maximo de normalizacion inferior a 0,000001.
- `npcgrp.dat` se cifra y descifra con igualdad binaria. Sus 6.519 filas originales permanecen intactas; se agrega una.
- El XML valida contra el esquema npcs.xsd del servidor.
- Se renderizaron reposo y caminata en Blender con las animaciones originales, sin advertencias de correspondencia de huesos.

El editor no trae `xDxTex.exe`. Las texturas quedan sin compresion DXT y el paquete de Amber mide aproximadamente 50 MB.
La copia de movimiento contiene tambien recursos originales que se pueden reducir mas adelante.

## Limites pendientes

- **V4 tiene aprobacion visual del usuario dentro de L2. Queda comprobar encaje (altura, pies y etiquetas), movimiento, secuencias automaticas y combate antes de ampliar su uso.**
- La transferencia inicial colapsa los dedos al hueso de la mano; falta refinarlos para agarrar un arco.
- Falta ajustar piel, cara, cuello, sombras y zonas de la ropa. Es un primer prototipo, no una skin terminada.
- No hay fisicas independientes de pelo/ropa, equipo intercambiable ni apariencia jugable.
- `L2AmberMotionv3.ukx` es una copia del recurso del cliente, para el laboratorio local.

## Reproducibilidad

Scripts en `scripts/`: adquisicion de herramientas, inspeccion, construccion Blender, compilacion UCC,
vinculacion de animaciones y shaders, parche del catalogo, previews y validacion.
Fuentes y hashes de herramientas en `reports/tool-sources.json`.
Pruebas y hashes de recursos instalados en `reports/validation.json`.
Comprobacion de nivel de detalle, pixeles, shaders y nombres nativos de animacion en `reports/v3-native-validation.json`.
Comprobacion de materiales v4, igualdad binaria de malla/pesos, texturas y dependencia de animaciones en `reports/v4-native-validation.json`.
`Install-AmberLab.ps1` reinstala solamente el perfil y los archivos identificados de este laboratorio.

Previews:

- `reports/amber-source-preview.png`.
- `reports/amber-l2-idle-preview.png`.
- `reports/amber-l2-walk-preview.png`.

Herramientas: https://github.com/gildor2/UModel ; https://github.com/DarklightGames/io_scene_psk_psa ;
https://maxcheaters.com/topic/248415-l2editor-mxc-encdec-light-and-clean/ ;
https://github.com/MobiusDevelopment/l2clientdat .
