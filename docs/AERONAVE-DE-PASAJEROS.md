# Aeronave de pasajeros — dirección de diseño, 14/10/2026

## Intención de Kevin

La prioridad es una aeronave funcional, con tripulación/NPCs y pasajeros. Debe viajar entre lugares, poder descender al puerto de Giran, permitir embarque/desembarque y volver a elevarse hasta desaparecer en el cielo. Más adelante, añadir otras aeronaves decorativas que circulen alrededor. El puerto de Giran es un ejemplo propuesto, no una ruta definitiva ya aprobada.

Pendiente decidir si la nave es autónoma o pilotable por jugadores, su capacidad, duración/frecuencia, destinos y papel de los NPCs. No asumir pilotaje libre por la palabra «tripulación».

## Comprobación del proyecto local

- `server/game/data/scripts/vehicles/BoatGiranTalking.java` ya implementa una ruta marítima con puerto de Giran, tiempos, anuncios y transporte.
- `source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/entity/actor/Vehicle.java` maneja rutas con puntos XYZ y pasajeros. La colección de pasajeros es de Player; transportar NPCs con posición/orientación relativas necesita tratamiento adicional.
- `VehicleDeparture.java` transmite al cliente destino XYZ y velocidades. Esto es base para investigar, **no prueba de vuelo vertical ni de cubierta caminable en movimiento**.
- Existe modelo de nave Gracia preparado en `research/airships/GraciaAirship-preview.blend`. Sus recursos y ensamblaje están documentados en `research/airships/README.md`; no hay transporte aéreo funcional verificado en Interlude.

## Propuesta técnica pendiente de prototipo

Primero validar una ruta automática corta: atracada -> embarque -> avance con ascenso -> regreso -> desembarque. Usar modelo sencillo antes de invertir en acabado. Comprobar en cliente real movimiento vertical, cubierta, giros, posiciones relativas y sincronización con más de un pasajero. Luego añadir tripulantes NPC e interacciones y extender a Giran y al muelle aéreo si se confirma ese recorrido.

La cubierta móvil requiere coordenadas relativas/soporte del vehículo; no se resuelve trasladando una malla y dejando geodata fija en el mapa. Los NPCs no deben quedar flotando en coordenadas mundiales al partir la nave.

«Desaparecer en el cielo»: propuesta visual de alejarse/entrar en nubes; no retirar el vehículo dejando pasajeros sin destino. Definir continuidad hacia la siguiente zona o llegada antes de implementarlo. Revisar desconexión/reconexión y recuperación del viaje.

Estado: intención registrada e inspección del código local. Sin cambios al servidor ni cliente; viabilidad completa pendiente de prueba.

## Avance posterior del 14/10/2026

Se integr? una primera versi?n estacionada del modelo gratuito para revisar aspecto, escala y cubierta desde `.muelle nave`. Instalaci?n y pruebas reales de acceso/suelo/regreso documentadas en `research/airship-integration/README.md`. Esto supera el estado de solo intenci?n del apartado anterior, pero NO implementa todav?a vuelo, pasajeros en movimiento, ruta a Giran ni tripulaci?n NPC.

## Aurelia — integración adicional del 14/10/2026

Kevin aportó una referencia de aeronave resort blanca con piscina abierta y pidió planos para modelado 3D. Se creó `research/airship-resort-v1` (Blender, GLB, planos SVG y dossier). Después autorizó expresamente integrarla a L2. La nueva nave se instaló estacionada en una parcela separada de `24_19`, con accesos `.muelle aurelia`, `.muelle aurelia a`, `.muelle aurelia b` y `.muelle aurelia puente`, soporte nativo y geodata. Se preservan la nave anterior, el muelle y Dust2. Memoria, límites, manifest, respaldo y estado de pruebas en `research/aurelia-integration/README.md`. No se implementó vuelo ni transporte móvil; la validación visual/física ingame sigue pendiente.
