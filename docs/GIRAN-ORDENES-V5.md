# Giran: órdenes a aliados y ataque a puertas — 11/10/2026

Instalado y validado con L2 cerrado: **389 checks nativos PASS**. GameServer disponible; prueba aislada finalizada y pilotos descargados.

El botón anterior «Reagrupar conmigo» cambiaba el modo de todos los escuadrones. Era un error durante la defensa competitiva: los rivales podían abandonar sus objetivos y seguir a Hellkevin. Ahora se comprueba el bando actual para cada orden: clan propio, alianza propia o defensores aliados del castillo. Los otros atacantes conservan sus agendas de asalto y conquista. Si cambia el propietario, se vuelve a evaluar la relación.

| Botón / macro de chat | Alcance |
| --- | --- |
| Aliados: seguirme — `.giran seguir` | Pilotos aliados; siguen y asisten a su líder humano |
| Traer aliados vivos aquí — `.giran traer` | Teletraslada únicamente pilotos aliados vivos, a una celda transitable y conectada a la posición del amo en su mismo piso |
| Aliados: objetivos del siege — `.giran asalto` | Aliados vuelven a defender el artefacto o a objetivos de ataque según su bando |
| Aliados: retirada — `.giran retirada` | Aliados vuelven a su sala de resurrección, HQ vivo o base de respaldo |
| Diagnóstico posición e IA — `.giran diagnostico` | Registra posición servidor/cliente y estado de cada piloto para estudiar atascos |

Traer no resucita muertos, no mueve humanos rivales y no mueve Ares/Nyx. Los muertos conservan el mecanismo de resurrección ya instalado. Los comandos son del laboratorio GM y requieren preparar la prueba. «Reunir escuadrones», iniciar y finalizar siguen siendo controles globales de preparación/ciclo del laboratorio; no son órdenes de cooperación.

## Puertas

Había dos problemas concretos: la formación respecto del capitán podía retirar un melee ya colocado contra una puerta, y se excluían todos los skills cuando el blanco era una puerta, incluso los nukes de los magos. Se permite mantener la ruptura de una puerta legal y visible aunque el capitán esté a más de 650 unidades; los magos usan sus ataques mágicos nativos. Se prioriza la puerta necesaria para entrar antes que perseguir a un guardia de la muralla. Los defensores jugadores/agresores y las necesidades de curación/resurrección mantienen su papel. No se agrega daño artificial ni se permite atacar la puerta propia o un muro sin arma de siege.

## Memoria

El registro del bloqueo anterior confirma `OutOfMemoryError: Java heap space`, con un heap limitado a 2 GB. El histograma registró 468 NodeBuffer y unos 900 MB en arrays de búsqueda de caminos. La reserva por hilo retenía muchos buffers. V2 la reemplazó por una reserva global limitada a 32 buffers y 68.513.792 bytes de arrays (unos 65 MiB). El máximo de Java de esta PC es actualmente 4 GB; en la medición durante la pelea de Kevin usaba 1.244 MiB, capacidad 1.444 MiB y máximo 4.096 MiB. Esto corresponde al servidor; no al cliente L2 ni al total de RAM de Windows. Esta versión no cambia ese core.

## Muro sobre la puerta exterior

Kevin reporta atasco al moverse con clic. Se examinaron las capas de geodata del frente de Giran: suelo inferior, pasarela superior y techo tienen alturas diferentes. Aún falta identificar el punto exacto de la incidencia con `/loc` o el diagnóstico. No se aplica un cambio especulativo que abra la colisión de la puerta. La prueba aislada incluye movimiento nativo sobre las dos superficies superiores y colocación de aliados sin caer al piso inferior; eso no sustituye reproducir el clic específico del jugador.

## Validación y continuidad

Compilación PASS. Prueba nativa aislada **389 checks PASS**; incluye exclusión de los cuatro clanes rivales de seguir/trasladar, aliados en el mismo piso, daño físico y mágico real a la puerta, y regresión de HQ, revival, Amber y guardianes. Se utiliza `Start-L2Local.ps1 -VerifyGiranDefense` solo para la prueba, con humanos desconectados. Los snapshots privados se toman después de cerrar L2 para preservar el estado real del personaje y resultado del siege.

Fuentes: `research/giran-orders-v5`. Respaldo: `backups/giran-orders-v5-2026-10-11`. No ejecutar instaladores/generadores antiguos para recrear esta versión.

Comparación persistente PASS: Hellkevin y su inventario, clanes/reputación/skills, propietario y fecha de Giran, y 382 guardias conservados. Los 19 pilotos quedaron offline nivel 80. Runtime, source/dist, overlay cloud y continuidad W10/W11 sincronizados; core y cliente sin cambios.
