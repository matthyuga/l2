# V4.1 — recepción de la exploración, 25/10/2026

La prueba real del usuario falló: Goddard seguía tapada. El log del servidor
registró su descubrimiento para objectId=268473899 a las 23:10:22 y guardó
global.base64. El cliente imprimió repetidamente REJECTED malformed fog snapshot.
Esto localiza el fallo en el transporte/parseo, no en la detección de movimiento.
El límite exacto del texto nativo no se midió: el proceso elevado denegó la
lectura de memoria (OpenProcess error5). No afirmar un límite exacto demostrado.

El envío anterior usaba un único texto UTF16 de hasta5500 caracteres. Ahora
FogGrid.packets divide ese mismo snapshot en fragmentos de64 caracteres con
cabecera #NXFC4|jugador|secuencia|indice|cantidad|contenido. Los paquetes completos
quedan bajo128 caracteres para el ID real y la prueba de un mapa lleno.
El cliente reúne hasta86 fragmentos, valida límites/identidad/Base64 y sólo
entonces sustituye el estado gráfico. Admite repetidos y orden inverso; un
fragmento ausente no aplica un mapa incompleto. La recepción expira en5segundos.
Los datos persistidos y la máscara de Giran se conservan. Un cliente viejo no
debe utilizarse contra los scripts nuevos: actualizar ambas partes con L2 cerrado.

Pruebas: compilación contra bibliotecas del servidor actual;95 comprobaciones
Java;20467 comprobaciones nativas incluyendo los fragmentos generados por Java;
prueba D3D9 HAL real con reemplazo del marcador y máscara Giran/terreno desconocido.
La recepción y representación dentro de L2 siguen pendientes de prueba real.

Instalación: install-chunk-fix.py comprueba L2 cerrado y ausencia de jugadores,
valida hashes instalados, respalda los cinco archivos y actualiza el manifiesto
original para que restore.py mantenga su comprobación y restauración a V3.
Después hay que reiniciar sólo GameServer. No borrar variables FOG4 ni el mapa global.

Éxito observable: NexusMapFog.log incluye RECEIVED complete chunked personal/global
exploration snapshot. Abrir mapa y Current Loc. en Goddard debe mostrar su entorno;
caminar debe ampliar el área y reconectar conservarla. El título ya se registró
una vez y no se repite por instalar esta corrección.
