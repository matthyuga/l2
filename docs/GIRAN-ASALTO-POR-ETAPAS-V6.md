# Giran: avance por etapas y protección del conquistador — 11/10/2026

Instalado y validado: **543 comprobaciones nativas PASS**, incluido recorrido desde sala hasta inicio real de Seal. Prueba finalizada y GameServer listo para Kevin.

Los atacantes tienen una ruta principal explícita: puerta exterior → patio → puerta interior → sala del trono → pasillo y escalera → artefacto. Los cuatro clanes conservan su propio líder, equipo, campamento y salida escalonada. No forman una alianza entre sí.

El líder tiene prioridad para llegar al punto de conquista y usar Seal of Ruler real. Al llegar, sus compañeros mantienen sus habilidades de curación/resurrección, despejan defensores próximos y atacan a quien amenace al conquistador o esté casteando una conquista rival. El casteo dura los tres minutos nativos y puede interrumpirse; no se completa por script.

Los defensores se adquieren de forma proactiva hasta 1.100 unidades visibles y legales. La escolta puede mantener un objetivo que se aleja del círculo anterior de 400 unidades durante una persecución limitada de diez segundos y 1.600 unidades desde su punto de adquisición. La legalidad, la visión y la vida del blanco se vuelven a comprobar. Las peleas entre clanes atacantes conservan ventanas de diez segundos y pausas de avance de veinte segundos también dentro del castillo. Los defensores y conquistadores rivales siguen teniendo prioridad.

Se corrige la tolerancia final de movimiento: el líder se aproxima a 24 unidades del punto elegido, en lugar de detenerse a 100 cuando el skill requiere estar a 85 del artefacto. Las etapas no esperan a que aparezcan cristales o torres ausentes. Las rutas de respawn se reconstruyen desde la posición actual hacia la etapa que alcanzó el equipo.

## Acceso final al artefacto

La prueba del terreno encontró cinco conexiones este/oeste bloqueadas sobre la escalera norte existente, en la fila y=145064, x=117528..117960. Se restauran solamente esos cinco bits en cinco bytes del archivo 23_22.l2j. Se conservan todas las alturas, las capas, el formato, las demás direcciones de colisión y el resto de las celdas; no se modifica ninguna puerta ni la geometría exterior del castillo. El líder atraviesa la escalera mediante puntos intermedios sobre su superficie real. El NPC artefacto conserva sus coordenadas originales.

El original queda respaldado en backups/giran-assault-v6-2026-10-11/23_22-before.l2j. La alternativa de geodata del [proyecto L2J](https://gitlab.com/l2j/l2j-geodata) se examinó y se descartó porque tampoco resolvía el acceso; no se instala. La corrección parte del archivo ya usado por el servidor y se valida con el parser y movimiento nativos.

El atasco de Kevin en el muro exterior continúa pendiente de `/loc`: esta corrección del pedestal no lo demuestra resuelto. `.giran diagnostico` conserva el registro de coordenadas y estados IA.

## Prueba y alcance

Compilación y prueba nativa PASS (**543 comprobaciones**): recorrido real desde sala, pasando por pasillo y escalera, inicio de Seal nativo sin teletrasladar al líder durante el recorrido, escolta que detecta un agresor del conquistador y mantiene un defensor que escapa más allá del círculo antiguo. La prueba aísla la navegación con la sala despejada y restaura la vida del piloto para evitar que el balance del combate impida estudiar el movimiento. El casteo se aborta antes de completar una conquista. Se conservan las regresiones de órdenes aliadas, daño físico/mágico a puertas, HQ, resurrección/buffs, Amber y guardianes. La defensa competitiva completa bajo combate y su balance requieren prueba de Kevin.

Snapshots privados antes/después: Hellkevin e inventario, clanes/skills/reputación, propietario/fecha de Giran y guardias. No se carga al personaje humano. El core y el cliente permanecen sin cambios.

Fuentes: research/giran-assault-v6. Respaldo: backups/giran-assault-v6-2026-10-11. No ejecutar instaladores o generadores históricos.

Comparación persistente PASS: Hellkevin/inventario, clanes/reputación/skills, Giran/propietario/fecha y382guardias conservados;19pilotos offline80. Runtime/source/cloud y continuidad37 W10/W11 sincronizados.
