# Summons y geodata del Coliseo — 2026-10-09

## Problema y cambios

Con PathFinding=2, SummonAI rechazaba seguir/atacar cuando findPath devolvia
null. Esto incluye regiones sin geodata: no es una prueba de obstaculo.
Elven ya tenia 21_19.l2j; Coliseo no tenia 24_19.l2j.

SummonAI ahora exige ruta solamente cuando ambos extremos tienen geodata.
Acepta movimiento directo valido sin exigir A*, incluso dentro de una celda.
Rechaza targets de otra instancia. El movimiento real conserva los chequeos
normales del motor: no se desactiva pathfinding ni se teletransporta al summon
para resolver ordenes de combate. Sin geodata no se pueden reconocer paredes.

Se instala 24_19.l2j, formato L2J leido por el GeoEngine actual, manteniendo
21_19.l2j intacta. Piso del centro y zona de espera: -3408; los spawns -3400
estan 8 unidades encima. Diez puestos antiguos y=45350/45150 quedaban sobre
gradas/paredes; se reubican a y=45750/45900 en XML y SoloArenaGauntlet.
No se modifican stats, clases, buffs, equipo ni reglas raciales.

## Procedencia y reproduccion

Fuente externa: [L2JOrion Interlude, archivo 24_19.l2j](https://github.com/naustagic/L2JOrion_Interlude/blob/98e351766c569504210a24d96a9f39262f19b397/L2jOrion_Geodata/geodata/24_19.l2j).

- Revision: 98e351766c569504210a24d96a9f39262f19b397.
- Tamano: 3335543 bytes.
- SHA256: E64898F18E4D8691C83D3901BB4DDB8F9C9FACA95E7DFBCF7BC7741B6D1F4454.
- SHA256 Elven conservado: 16544B334DD1D0280480832FDE22A9F6DADAA3AD90D4E3E1250F23E156B7E820.

El binario no se incorpora al repo; ops/windows/Install-ColiseumGeodata.ps1
descarga una revision fijada, valida hash y no sobrescribe otro archivo.
Su disponibilidad publica no acredita permisos de redistribucion.

## Verificacion

Compilacion core completa sobre el codigo local vigente; scripts compilados.
Autoprueba opt-in: -Dlab.ai.smoke=true -Dlab.geo.verify=true.
Revisa suelo y ruta directa de los 19 puestos al centro, cobertura Elven y
bloqueo de la frontera elevada norte. Luego prueba las diez acciones originales
y dos nuevas: seguimiento real del Nightshade hasta 180 unidades del dueno,
y aproximacion/ataque con reduccion real de HP+CP del rival. Instancia privada;
limpieza de pilotos y restauracion de hojas de comparacion al terminar.
Los teleports en esos dos casos solo colocan los actores de prueba inicialmente;
la distancia restante debe recorrerse por la IA normal.

La primera autoprueba dentro del servidor paso geodata y seguimiento, pero
fallo la etapa de dano: el Player rival de prueba quedaba decayed/teleporting
porque no tiene cliente que confirme llegada. El montaje ahora llama
onTeleported despues del teleport de cada Player headless y fija explicitamente
su instancia privada. Esta correccion pertenece solo a la autoprueba, no a las
reglas de dano ni a los atributos de combate.

No equivale a auditar cada pared/puerta del mapa. No corrige inmovilizaciones
legitimas por root/stun/UD, ni prueba automaticamente el summon de Hellkevin.
La primera exploracion offline de A* intento inicializar fences sin DB/World
y produjo warnings; no es evidencia de rutas validadas. La prueba completa debe
hacerse dentro del servidor inicializado.

Backup: E:\l2-local\backups\summon-geodata-2026-10-09.
Sin commit/push automatico.

Resultado final 19:25:49: GEO_SMOKE PASS y AI_SMOKE SUCCESS 12/12,
incluyendo seguimiento y dano real del Nightshade. Regresion: 335 checks de
politica general, 108 de Noctis y 4 variantes de paquetes PASS.
Log conservado: backups/summon-geodata-2026-10-09/smoke-success.log.
