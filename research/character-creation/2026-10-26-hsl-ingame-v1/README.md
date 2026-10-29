# HSL integrado en el creador — instalado, revisión visual pendiente

Trabajo autorizado: panel dentro del viewport de Lineage II, al costado derecho del creador; modos Clásico A–D y Libre HSL. No es una ventana externa de Windows.

Estado: instalado en `E:\l2\system-hud` (2-JUGAR) y `E:\l2\system-camera-online`, con cuatro clases de paquetes actualizadas en el GameServer activo sin reiniciar. Falta la confirmación visual del usuario sobre el panel, la previsualización y un personaje creado con color libre.

## Uso

En el creador, abrir el panel superior derecho «Color del cabello». Clásico A–D conserva el selector izquierdo. Libre HSL habilita el plano de tono/saturación y la barra de luminosidad; arrastrar para cambiar. El panel muestra H/S/L y HEX. Restablecer recupera el tono inicial del selector libre. Cambiar a Clásico recupera el A–D retenido. Create Character envía el color elegido junto con el personaje.

No es una ventana independiente ni un accesorio de inventario. El motor aplica el color a materiales propios de la instancia del personaje. Si no puede preparar una máscara segura para un material, conserva ese material original en vez de teñir todo el atlas.

## Componentes

- `hair_ingame.cpp`: dibujo sobre UTexture nativa, entrada del ratón en el viewport, modo Clásico/Libre y tintado por instancia de los slots de cabello 4/5. Clona los modificadores del material; conserva el alfa y usa diferencias A–D como máscara de tinte. Si no puede demostrar la máscara conserva el material original.
- `color_core.h`: HSL, codificación de color, BC1/BC2/BC3 y máscaras. Pruebas: 20506 verificaciones nativas, incluidas DLL/exportaciones.
- `prepare_client.py`: añade importaciones a NWindow/engine partiendo exactamente de v14, encadenando sus hooks existentes de apariencias. `verify_client.py` comprueba preservación de bytes/imports y ejecuta los saltos de entrada en Unicorn (30 comprobaciones).
- `server-source/.../HairColorHsl.java`: mantiene `characters.haircolor` en 0..3, guarda RGB en `character_variables` bajo NEXUS_HAIR_RGB_V1 y lo transmite en el int de haircolor con una marca explícita. El cliente debe normalizarlo antes de acceder a tablas nativas. Esto requiere el cliente modificado en todos los receptores.
- `prepare_server.py`, `build-server.py`: preparan cambios solo en readImpl/runImpl de CharacterCreate y writeImpl de CharInfo/UserInfo/CharSelectionInfo, preservando los demás métodos del JAR actual. 16394 pruebas de protocolo. No se cambia el esquema ni los personajes existentes.
- `HslReloadAgent.java`: recarga atómica aplicada a cuatro clases con captura de rollback. El JAR conserva todos los demás métodos y entradas anteriores.

## Perfil aislado

`E:\l2\system-hsl-check-20261026`. Configuración mutable copiada y archivos binarios compartidos mediante hardlinks; no escribir sobre los hardlinks. NWindow.dll, engine.dll, d3d9.dll y NexusHairHslGame.dll son copias independientes. Para comprobar el contrato se usa únicamente en este perfil `NexusHairHslQA.ini`, sección Test, NativePreflight=1 y QuitAfterPreflight=1. La preprueba genera registro y un bitmap diagnóstico del panel; ese bitmap no es una captura del juego.

La automatización Computer Use está indisponible por error de conexión al native pipe. Se usa el registro del propio cliente de prueba, sin afirmar una inspección visual interactiva. La preprueba automática ya pasó: textura RGBA 1024×512, 100493 píxeles de cabello y 423795 protegidos, alpha conservado, clonación de modificadores, UTexture nativa del panel y estabilidad de recursos GDI tras el calentamiento de fuentes. `native-panel-diagnostic.bmp` permite revisar el diseño; no es una captura del panel sobre la escena de L2.

## Verificación y rollback

`persistence-proof.txt`: siete comprobaciones en el servidor real con el personaje reservado y offline BodySexProbe, sin aparecer en el mundo: persistencia RGB independiente, lectura SQL para selección, carga nueva de variables, conservación del color clásico y limpieza exacta del dato de prueba. Esto prueba el recorrido servidor; no sustituye una creación/relog visual en el cliente.

`installation.json` registra todos los archivos, hashes y copias anteriores. Respaldo: `E:\l2-local\backups\hair-hsl-ingame-v1-20261026-230921`. Para volver atrás con el cliente cerrado: ejecutar `python research/character-creation/2026-10-26-hsl-ingame-v1/rollback.py`. Comprueba hashes y restaura archivos y definiciones del servidor de esta sesión. Si el servidor ya reinició, el script exige una restauración controlada con reinicio para evitar usar definiciones runtime antiguas.

Se actualizó únicamente la huella de NWindow que acepta el módulo de niebla del mapa de system-hud para conservar su compatibilidad. Sus reglas, renderizador y configuración no cambiaron. La retirada de las caras problemáticas del orco y los recursos de los peinados v14 se conservan.

Los colores personalizados requieren estos clientes modificados: el int de haircolor lleva una marca y RGB; los accesos de recursos se normalizan al A–D clásico antes de entrar a las tablas. No distribuir el dato a clientes antiguos sin este soporte.
