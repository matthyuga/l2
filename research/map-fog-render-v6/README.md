# Corrección del revelado gráfico V6 — 26/10/2026

## Validación final en L2

Usuario confirmó primero Giran despejada, y después AMBAS pruebas: Goddard ya
visitada se ve y caminar por terreno nuevo amplía el revelado. Logreal confirma
WIRED V6 exploration atlas into verified native fog texture cache. La conexión
por recurso nativo quedó validada visualmente. El guardalpha no emitió DRAW en
esa sesión: no atribuir la solución observada al cambio de blend, que sólo se
validó en HAL aislado. La primeraV6 (sólo identificar) no funcionaba.

Progreso personal persistido comprobado con SQLread-only. No se borraron visitas.
installation.json: verified-in-game-by-user. Pendientes históricos de las secciones
siguientes corresponden a los intentos anteriores, no al estado final.

## Segunda corrección y estado de prueba

Primera instalación V6: el juego real SÍ confirmó INSTALLED y MATCHED V6 native
UTexture identity (GPU16x16,formato21,pool1), pero el usuario siguió viendo todo
opaco incluso en Giran. No dar esa primera instalación por funcional.

Lectura SQL de sólo lectura mediante ReadFogState.java confirma80 celdas personales
persistidas; Giran y Goddard están visitadas. No es una pérdida de guardado. No
se imprimen credenciales. La prueba HAL anterior leía alpha del atlas pero no el
framebuffer final: insuficiente para validar presentación.

Se añadió wireAtlas que cambia únicamente la referenciaGPU+38 del recurso nativo
identificado por UTexture, con AddRef/Release simétricos. Así la caché del motor
entrega el atlas directamente aunque conserve o reutilice sus enlaces. Además,
las cuatro rutas DrawPrimitive/Indexed/UP fuerzan alpha del atlas sólo cuando
está enlazado en stage0, y restauran estado tras dibujar. No altera otras texturas.

proxy_test ahora dibuja y lee el FRAMEBUFFER final bajo un material inicialmente
opaco: Giran conserva fondo verde, desconocido lo cubre; valida restauración de
estado y referencia nativa. DLLV4 falla23 en este escenario; versión nueva pasa
MANAGED y SYSTEMMEM->DEFAULT. Instalada con cliente cerrado sin reinicio servidor;
backup adicional backups/map-fog-render-v6-20261026-010644.
Pendiente segunda prueba REAL del usuario. Logs a buscar: WIRED V6..., DRAW V6...
y recepción de snapshots. No afirmar todavía éxito visual dentro de L2.

El usuario reportó mapa completamente cubierto tras V5. Servidor registra Ketra,
Garden of Beasts, posiciones nuevas y actualiza global.base64. Cliente recibe
snapshots completos. En la sesión NO aparece MATCHED V4 overlay: nunca se enlazó
el atlas dinámico. No atribuir el fallo a los nombres nativos ni borrar el progreso.

V4 sólo reconocía la textura leyendo ocho DWORD exactos al enlazar una textura
GPU16x16/A8R8G8B8. Se reprodujo un fallo en HAL real con subida SYSTEMMEM->DEFAULT:
DLLV4 falla exit12; V6 pasa. Este caso demuestra una limitación V4, no prueba por
sí mismo que sea la ruta usada en esta sesión de L2.

REA/Ghidra D3DDrv.dll original SHA256
2b496d235cca529b6180588a987ca0059600a2323193d96e87b90014105be0c2:
FD3DTexture::Cache RVA32ac0 permite enlazar la textura por identidad nativa:
FBaseTexture vtable+14 => FTexture; vtable+50 => UTexture; cache+38 => GPU2D.
REA confirma prólogo PUSH EBP;LEA EBP,[ESP-70h] (5bytes sin relativos), RET8.
Se verifican SHA256 y bytes exactos antes de instalar hook en memoria. El archivo
D3DDrv.dll permanece intacto. Evidencia completa proyectada en rea-render-evidence.json.
La función es demasiado grande para la respuesta MCP completa; inspect_analysis_view
retuvo y devolvió los35872caracteres de pseudocódigo, cobertura exhaustiva de esa
faceta; el pcode general tiene límites reportados. No presentar pseudocódigo como
código original ni como prueba visual del juego.

V6 añade selección por identidad de UTexture, conserva reconocimiento por firma,
soporta subidas de texturas y actualiza atlas también en Present si el motor no
repite SetTexture. Mantiene opacidad independiente del foco, clipping, mapa chico/
grande y transporte fragmentado. Sin cambios de reglas, fuentes Java o datos.

Pruebas:30476 checks con fixtureJava, mocks de vtables/offsetGPU, nuevo prólogo y
10000llamadas con RET8, más hooks anteriores. HAL real MANAGED y SYSTEMMEM->DEFAULT,
Giran despejada y desconocido opaco. Estas pruebas NO validan el hook con L2.

Instalado con L2 cerrado sin reiniciar servidor. Backup
backups/map-fog-render-v6-20261026-005508. installation.json y manifiestoV4 mantienen
hash/restore. Pendiente usuario abre mapa. Verificar INSTALLED V6 native texture
identity hook y MATCHED V6 native UTexture identity en NexusMapFog.log; si no hay
MATCHED, investigar el empaquetado de texturas UI antes de afirmar que se arregló.
