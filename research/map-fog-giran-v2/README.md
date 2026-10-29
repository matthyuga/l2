# Niebla del continente y Giran despejada V2 — 25/10/2026

Instalada con el cliente cerrado tras confirmación de Kevin. Sustituye el rectángulo diagnóstico por una cobertura de todo el visor del mapa, dejando transparente el perímetro de Giran Castle Town. Falta inspección visual dentro de L2. No modifica campañas, servidores, progreso de .explora ni geografía.

## Uso

Abrir L2 normalmente y el mapa en Giran. Por defecto modo2: niebla opaca fuera de la ciudad. Sus nubes tienen color gris azulado, variación de textura y borde irregular/difuminado alrededor del área despejada. El marcador propio sigue dibujándose por encima. NIEBLA-3-APAGAR.cmd permite comparar; NIEBLA-2-OPACA.cmd restaura la cobertura completa. NIEBLA-1-PARCIAL.cmd deja semitransparente el resto del mapa como control diagnóstico. NIEBLA-4-CENTRAR ya no mueve nada y explica que Giran tiene una ubicación fija.

## Región y representación

Fuente de la ciudad: server/game/data/zones/custom_town.xml, zona Giran Castle Town. Polígono y hash registrados en assets.json. Todos los píxeles interiores son transparentes. Fuera de la ciudad se añade una transición suave de aproximadamente350 a1750 unidades de mundo, perturbada por ruido; el límite municipal no aparece como un rectángulo. La cobertura se genera mediante código determinista, sin descargar imágenes externas.

Texturas CloudTile y GiranClear512x512 en NexusMapFogV2.u. UCC dejó mensajes sobre xDxTex.exe ausente, pero guardó texturas BGRA8 sin compresión: se comprobó que el export contiene EXACTAMENTE todos los píxeles BGRA originales, incluido alfa. No se confunde la salida del compilador con una validación de transparencia in-game. Importación ALPHATEXTURE, roundtrip del wrapper121 y CRC comprobados.

GiranClear corresponde al rectángulo de mundo72000,136000..96000,160000. Su exterior es opaco y su interior contiene el claro del polígono. No es un parche opaco rectangular sobre Giran: el canal alfa deja ver la ciudad y sus bordes graduales. El visor se divide en hasta cuatro franjas exteriores y el parche recortado, evitando tapar primero el área que debe permanecer transparente.

Para situarlo se llama la conversión nativa mundo→mapa RVA187c10 con el mapa activo. Se usa tanto para continente como para plano de ciudad. Se restan offsets internos de desplazamiento y se recorta contra el visor. La textura de nubes usa coordenadas globales para mantener continuidad entre franjas/parche y al arrastrar. La escala continental recuperada del ensamblado es0.0050048828125; ciudades emplean su conversión nativa. La proyección de ciudad aún debe confirmarse visualmente.

## Instalación y recuperación

installation.json y backups/map-fog-giran-v2-20261025-221355 registran SHA256 y archivos anteriores. Se reemplazaron solo el proxy d3d9.dll y NexusMapFog.ini propios de V1, se añadió NexusMapFogV2.u y se adaptó el mensaje del control Centrar. NWindow.dll e Interface.u/XDAT permanecen intactos. No se detuvo/inició GameServer.

Cerrar L2 y ejecutar `python research/map-fog-giran-v2/restore.py` para volver a V1 con sus archivos anteriores. Después, si se desea retirar todo, usar restore.py de map-fog-native-v1. Cada restaurador verifica destinos/hashes. Apagar la cobertura no requiere cerrar.

## Validación

- MSVC2019 x86 y harness de trampolines/convenciones de llamada: PASS.
- Proxy Direct3D9: factory/dispositivo HAL oculto/16 Present: PASS.
- Polígono municipal transparente, límites del parche opacos y alfa intermedio: PASS.
- Paquete UCC, identidad de los dos exports, BGRA exacto, flag alfa, wrapper/CRC: PASS.
- Inspección de preview con tablero representando el mapa: realizada; no es captura del juego.
- Pendiente: dibujo in-game, claro correctamente alineado en Giran, mapa ampliado/pequeño, plano urbano y recorte al arrastrar. Revisar NexusMapFog.log si no se ve el claro.

Esta entrega aplica una regla visual fija elegida por el usuario: solo Giran despejada. No implementa aún transiciones temporales, otros descubrimientos, marcadores ocultos por región ni sincronización de .explora. La ausencia de cobertura en el borde de la ciudad es una gradación espacial de alfa, no animación.
