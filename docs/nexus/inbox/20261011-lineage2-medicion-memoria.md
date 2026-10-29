# Lineage2: medición preliminar de memoria por unidad

Proyecto real E:\l2-local. Usuario pidió mediciones más certeras para tantear capacidad. Informe: reports/memory-capacity-2026-10-11/INFORME.md, summary.json, process.csv y owned/units.csv.

Se midieron objetos reales con Instrumentation.getObjectSize y recorrido acotado de referencias locales, excluyendo templates/skills, castillos/zonas, world, clan/party, actores vecinos y red. No es retained heap exacto ni costo incremental total. Primera variante contaba el castillo dentro de guardianes; resultado final owned excluye esa referencia compartida. Sin cortes ni campos inaccesibles en corrida final.

Muestras:30 templates de monstruos,5NPC simples,2guardianes,5 perfiles técnicos (Darius,Nerys,Darion,Zareth,Arden) cargados sin spawn y luego descargados. Ningún humano cargado ni clases del core redefinidas, GC forzado o combate iniciado. No había clientes/bots activos/summons; no se hizo prueba de carga activa. Roster20/20 offline/equipo PASS posterior.

Promedios de huella local: monstruos13,83KiB, NPCsimple10,48KiB, guardianes10,35KiB, Playerbot82,01KiB (rango76,28–84,04). ×100bots≈8,01MiB únicamente de grafo local medido, NO RAM total del escenario ni garantía de100 bots fluidos. Census35617monstruos en World; no implica35617 combatiendo.

Muestreo60,85s del proceso25748 en idle: RSS1,32–1,40GiB; pico desde arranque3,07GiB. CPU promedio0,032% y pico0,679% del total16procesadores lógicos; incluye trabajo del observador. PC i9-11900K8cores/16threads,31,86GiBRAM, heap8GiB. No usar CPU idle para estimar límite en siege.

Para determinar capacidad práctica faltan escalones controlados50/75/100 Players con movimiento y combate, colas/pathfinding/GC/timing y cliente. No calcular máximo dividiendo RAM libre por82KB. Se entregaron mediciones preliminares, no certificación de capacidad activa.
