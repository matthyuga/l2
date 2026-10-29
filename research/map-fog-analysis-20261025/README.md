# Mapa ampliado y niebla de exploración — 25/10/2026

## Resultado

El cliente activo tiene implementados mapa compacto y ampliado. No hace falta importar una ventana de una crónica posterior para obtener la ampliación básica.

Inspección estática de `E:\l2\system-hud\Interface.u`, `Interface.xdat` y `NWindow.u` con los parsers locales acmi/ct0, abiertos en lectura. Identidades en input-hashes.json. Salidas completas: map-bytecode.txt, map-layout.txt, map-api.txt. inspect-map.groovy permite repetir la lectura sin instalar cambios.

- `MinimapWnd.OnClickButton`, caso `ExpandButton`: marca expansión, muestra `MinimapWnd_Expand` y oculta `MinimapWnd`.
- `MinimapWnd_Expand.OnClickCollapseButton`: realiza el recorrido inverso.
- `OnShow` del ampliado centra en jugador y consulta resolución.
- `ResetMiniMapSize`: ancho de ventana = resolución, limitado a 1024; alto = resolución, limitado a 1024. Área de mapa: ancho menos 3% (o 1016 al superar 1024), alto menos 90 (o 934 al superar 1024).
- Las dos ventanas usan controles nativos MinimapCtrl. La posición proviene de `GetPlayerPosition` y se centra con `UIAPI_MINIMAPCTRL.AdjustMapView`.
- Hay API de marcadores con coordenadas (`DrawGridIcon`, `AddTarget`) y texturas UI (`SetTexture`, `SetUV`, `SetTextureWithObject`). Sus firmas no demuestran que sirvan para una máscara continua ni que permitan leer la transformación de desplazamiento/zoom.
- El layout del mapa ya incluye texturas de sombra superpuestas: indicio útil para una prueba de cobertura, sin confirmar orden de dibujo ni seguimiento del mapa durante desplazamientos.

## REA y runtime: límites reales

REA confirmó `NWindow.dll` como PE x86, SHA-256 a8bda77a97cd3e8583ce61e227380303212dbfc25ae10f8907106379fec3f292. Se abrió y cerró la sesión estática sin cambios.

El proceso L2 PID13076 fue observado por PowerShell con ventana Lineage II y Responding=true. No apareció en el inventario local de Frida. El intento de attach no devolvió sesión y se canceló la espera; no se cargó ningún script de instrumentación. No se obtuvo evidencia de memoria ni ejecución del mapa. La causa de la ausencia en Frida no está determinada.

El control nativo de ventanas falló por pipe de Computer Use no disponible. No se pulsó Enlarge Map. `inspect_with_objdump` de REA también devolvió capability_unavailable. No se atribuye a REA la decodificación Unreal realizada por los parsers locales. El cliente siguió respondiendo tras el intento de attach.

## Diseño conservado

Dos registros independientes: global del servidor y personal por personaje. Cobertura opaca donde falta revelado global; tenue si hay revelado global pero falta exploración personal; transparente cuando ambos están revelados. La condición para revelar globalmente una región (exploración o campaña/recuperación) sigue siendo una regla de diseño, no está implementada.

## Siguiente prueba técnica

En copia/staging del estado actual, añadir una cobertura estática pequeña a ambos mapas. Verificar orden de dibujo, interacción, ampliación/reducción, desplazamiento, centrado y cambios de resolución antes de elegir la máscara definitiva. No reejecutar builders históricos sobre el cliente actual. Si no se puede sincronizar la cobertura con el MinimapCtrl, considerar ventana cartográfica propia con transformación de coordenadas controlada por nosotros.

Después conectar registros servidor/cliente, comprobar dos personajes con descubrimientos diferentes y persistencia al reconectar. Ninguna niebla ni transporte de estado se ha instalado. Cliente, servidor y campañas no se modificaron.

## An?lisis nativo posterior con REA

Completado an?lisis est?tico Ghidra de NWindow.dll. Ver COMPOSICION-REA.md y rea-map-composition-evidence.json. Desplazamiento interno confirmado; agrupar controles por XDAT no basta. Propuesta: etapa de dibujo de niebla dentro de NCMinimapWnd, compartiendo transformaciones/recorte. No se instal? c?digo gr?fico.
