# NPC temporal de animación — 15/10/2026

Pedido explícito del usuario: crear un NPC para observar el movimiento sin cambiar/crear personaje.

Cliente de laboratorio actualizado con display59080: class LineageNPC.a_traderB_FHuman, mesh Dust2DemoNPC.DemoMesh, textura plana azul DemoClay. Cuerpo completo compuesto de piezas nativas Fighter mujer sobre76huesos, PSK y compilación UCC. No se alteró cliente habitual. Catálogo npcgrp del lab6523registros anteriores conservados byte por byte +1nuevo; cifrado413 roundtripPASS.

Paquete Dust2DemoMotion: secuencia wait_Hand con151fotogramas/30fps del movimiento combinado agachado/manos. Malla compilada enlazada con import explícito a Dust2DemoMotion.Dust2Motion. UModel -game=l2 carga malla/animación/texture y confirma76huesos/LOD1. Forzar -game=l2 para este paquete mesh123/0: autodetección UE2 genérica interpreta mal TRoughArray de animación Lineage123/30. No confundir ese error del visor con evidencia de fallo nativo de cliente.

Agente Java Dust2AnimationNpc compilado contra JAR activo, cargado en GS25176. No redefine clases/core, no registra scripts ni escribe DB/templates. Crea NpcTemplate privado id902680/display59080 y NPC transitorio cuando Hellkevin esté online, máximo espera10min. Spawnea100u al lado en misma instancia y suelo GeoEngine; diferencia de altura>80 vuelve al punto del personaje. Invulnerable, no agresivo, sin randomwalk/randomanimation. Eliminación programada20min tras spawn, hilo daemon termina. Guardas impiden duplicado en mismo classloader o ID ya activo. No reejecutar agente mientras sigue esperando/activo.

Estado real ver npc-runtime.txt: READY, SPAWNED, FAIL o REMOVED. Identidad/posición se registran ahí. No se tocó el personaje (solo mensaje informativo), su apariencia/raza/progreso ni scripts de salas PvP. La interacción del NPC es solo demostración; no incorpora bomba/kit/casteo.

El usuario cerró L2 antes de copiar recursos y solicitamos abrir el lab actualizado. Falta revisión visual en cliente y confirmación de animación continua. Si muestra reposo errado, investigar nombres exactos WaitAnimName antes de modificar. No afirmar render ingame validado.

Archivos reproducibles export_mesh.py, build_mesh.py, link_mesh.py, prepare_catalog.py, Dust2AnimationNpc.java, build_agent.py. client-installation.json registra hashes. NPC solo está en memoria y desaparece al reiniciar; catálogos/assets solo lab.

Corrección en vivo15/10: primer agente falló al crear Npc por getSkills null antes de spawn. AgenteV2 con template.setSkills(Map.of()) compilado/cargado sin redefinir clases. Confirmado SPAWNED object268436178, npc902680/display59080, xyz83525,148585,-3401, instancia0 junto aHellkevin. Estado vigente npc-runtime-v2.txt. Temporizador20min. No reejecutarV1/V2 mientras activo. Visual pendiente del usuario.

## Cierre cliente y arreglo V2
Usuario aportó critical15/10 12:11:50: SkeletalMesh Serial size mismatch Got-134 Expected200301. Retirado NPCV2 y scheduler detenido mediante RemoveDust2Demo.jar. Error probablemente causado por reubicar payload malla: offsets absolutos lazyarray seguían apuntando original. link_mesh.py ahora modifica EN SU OFFSET ORIGINAL7969, tamaño200301 intacto, solo1byte Animation ref en offsetrel8785. Todos los exports mantienen offsets/tamaños originales; otros payloads exactos. mesh-fix-v2.json; paquete nuevo SHA f5922b132832d5d5d3dcb2ae0128b5529bb3a4bdb223ebb727f363b22c1e5238. Original fallido conservado Dust2DemoNPC.failed-v1.ukx. Cliente cerrado observado al copiar; solo lab actualizado, manifiesto registra hash vigente y anterior.
NPCV3 espera login y volverá a crear demo temporal. Estado npc-runtime-v3.txt vigente, noV2. Se reabrió cliente lab. IMPORTANTE: arreglo aún NO verificado en cliente real; no afirmar corregido definitivo por UModelPASS. Si repite crash retirarV3 antes de más login.

Usuario pide delante/cerca sin mover camara. Localizado Hellkevin268473899 en83425,148585,-3401 heading0 instancia0. V3 habiaEXPIRED sin conectado. AgenteV4 calcula frente por heading a85u; estado vigente npc-runtime-v4.txt. Camara cliente no observada, heading personaje no asegura orientacion exacta camara. Sin mover personaje ni camara.

CONFIRMACION VISUAL DEL USUARIO: ve al NPC y dice 'quedo perfecto'. Malla y movimiento de demo corregida aceptados en cliente L2. Esta confirmacion no implica mecanica bomba ni todas razas. Siguiente pedido: incorporar modelo C4 de CS local; trabajo separado research/dust2-c4.
