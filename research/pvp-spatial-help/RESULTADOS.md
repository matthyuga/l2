# Apariciones, movimiento y ayuda de salas ? 15/10/2026

Instalado y activado en GameServer27412 sin reinicio, cambios de reloj ni teleport de Hellkevin.15fuentes sincronizadas en runtime/source/overlay; respaldo indicado en installation.json. No cambios de cliente/core ni scripts de animaciones.

## Causas y cambios

- FREE/ARENA usan team0: antes todos entraban y reaparecian en map.spawns[0]. Ahora se eligen puntos separados entre los cuatro sectores, con piso de geodata, margen vertical64 y espacio local para caminar. En equipos se dispersan alrededor de la base de su equipo. Se maximiza distancia a participantes vivos; no garantiza invulnerabilidad ni ausencia absoluta de spawn camping. Los regresos guardados de jugadores conservan la regla anterior.
- Entrada, cambio de mapa y reaparicion de bots usan el selector. No se cambia aqui el sistema nativo de resurreccion de jugadores reales.
- Distancia de respuesta a amenazas para roles de rango ampliada a430; retirada considerando varios enemigos. Daggers buscan flanco; melee se separa si hay solapamiento. Paso local con alternativas de direccion, consulta de ruta nativa si falla y throttling incluso en rechazo. No atraviesa paredes ni teleporta para combatir.
- Healers en FFA/ARENA pueden usar habilidades ofensivas aprendidas; nunca curan oponentes por compartir party. En equipos conservan prioridad de apoyo. Menor prioridad a objetivos en otra altura o sin visibilidad.
- Diagnostico real: ArenaDraven sobrecargado,66.900/62.100 de peso; ArenaThalion65.900/69.690,penalizacion3. Bolsas antiguas con4.000shots yBSS,4.000flechas,60MPpotas,etc. Ahora bolsas SS/BSS1.000,flechas500,potas20,gemas120 y materiales acotados. Stock se ajusta al preparar/reaparecer; consumo nativo, sin rellenado continuo de HP/MP. Se ajustaron20reservas activas/preparadas; todas quedaron penalizacion0. Snapshot original de PvpSiegeRoster restaura cantidades al retirarlos normalmente; sigue sin recuperacion persistente ante crash. No se altero inventario del jugador.

## Ayuda

.ayuda y .macros abren el mismo catalogo, con Salas,Bots,Retirar,Duelos,Grupos,Asedio,Personaje yViajes. Controles de laboratorio visibles paraGM; acciones pasan por handlers originales y mantienen sus permisos. Parametros libres no se ejecutan: solo identificadores del catalogo. Cantidades/votos y rival individual se muestran como ejemplos manuales.

NPC existente de salas en Giran y muelle incluye Ayuda/Comandos; no se agrego otro NPC. Abrir ayuda detiene el refresco HTML de top/votos para que no pise la ventana; .salas top y .salas votar los reabren. No cierra la sala ni reinicia el contador de ronda. HTML y registros comprobados; falta revision visual por el usuario en cliente.

## Evidencia

spatial-tests.txt:12puntos distintos por escenario en3mapas x4modos. Escenarios de equipos probaron12actores en una misma base(team1), no todos los sectores individualmente. Se verifico piso, perimetro, separacion minima y18paginas HTML. Scratch actors con IDs negativos nunca registrados/spawneados/guardados; timers detenidos.

Primeros dos intentos de dispersion descartados: exigir linea recta desde la base reducia mucho el espacio de Elven. No se cambiaron controladores de produccion hasta pasar la tercera prueba. Validacion final usa transitabilidad local del punto; no afirma conectividad global de todos los sectores.

live-spatial-before-bags.txt:32segundos de observacion de10bots;7se movieron y4reaparecieron en coordenadas diferentes.
live-spatial-audit.txt:tras bolsas ligeras y ruta alternativa,9/10bots con desplazamiento real en32segundos; ambos tanques se desplazaron.3reapariciones registradas en puntos distintos. Movimiento se cuenta entre muestras vivas, excluyendo el cambio de muerte a vivo y saltos>=600. La muestra no prueba todas las maniobras ni movimiento constante; Faelith no se movio en la ultima ventana.
bags-audit/status:20reservas sin sobrepeso ni penalizacion.
help-status:aliases registrados y enlace en menu NPC activo.
startup-check:compilacion de todas las fuentes instaladas de ElvenPvpRoom.
installation-audit.json:67hashes de la cadena verificados.

## Limites

No es una IA de estrategia humana completa. Elven mantiene capas y obstaculos; aun hay rechazos de movimiento y no se certifica navegacion global. Los puntos de Primeval/Saints se verificaron con geodata, no mediante encuentros completos en esta etapa. No se repitio el benchmark de dano anterior tras cambiar bolsas/movimiento; no trasladar sus porcentajes a esta version. No se certifica carga de cuatro salas llenas.

Para volver a cerebro clasico: .salas bots cerebro clasico. Esto conserva las mejoras de aparicion y bolsas porque son infraestructura compartida. Rollback completo: retirar bots normalmente, detener GameServer, ejecutar restore.py, arrancar con lanzador normal. Manifest conserva respaldo anterior a toda esta etapa.
