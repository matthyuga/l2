# C4 de Counter-Strike 1.6 para L2 — 15/10/2026

Pedido: después de aprobar visualmente NPC agachado, Kevin solicita modelo de bomba C4 de Counter para L2. Salas PvP siguen otra sesión y no se tocan.

## Resultado preparado
Extraídos dos MDL IDSTv10 locales de D:/juegos/cs1.6/cstrike/models: w_c4 y p_c4, con geometría, bind transforms y tres imágenes embebidas. Son los archivos de la instalación local; no certificación de versión Valve inalterada. Originales read-only. Extractor, copia, hashes, manifest y previews en extract/README.md. Fuentes primarias del formato registradas allí.

Elegido w_c4:64vértices/116triángulos, bloque verde con temporizador rojo y cables. Las previews confirmaron que no es una mochila. Texturas c4base204x56,c4timer76x64,c4wires48x23; adaptadas a potencias de dos para UCC manteniendo UV normalizados y diseño. No hay reloj animado ni electrónica real.

Prototipo combinado con NPC Fighter mujer76huesos previamente aprobado. C4 entre manos, escala0.58 y ligera inclinación25grados para mostrar panel. Posición ajustable; usuario recibió consulta manos/suelo, aún sin respuesta registrada al preparar. Si elige suelo, cambiar placement.json a mode=ground y reconstruir bajo nombre de paquete nuevo para no pisar compilación ya existente.

- build/Dust2C4Demo.blend y -QA.blend: edición/QA.
- build/Dust2C4Demo-preview-first.png: vista previa revisada.
- build/Dust2C4Demo.psk, Dust2C4Demo.ukx: cuerpo y C4.
- build/Dust2DemoMotion.ukx: misma secuencia demo existente, import wait_Hand.
- build/validation.json:2233caras total (=2117NPC+116C4),76huesos,4materiales. UModel recarga/exporta mesh ytexturas, píxeles idénticos a TGA adaptados. Todos offsets/tamaños export mantienen original; solo1byte payload mesh cambiado para Animation, evitando critical previo por reubicar malla. Esto es prueba de recurso, aún NO render L2.

## Instalación pendiente de cerrar cliente
Cliente lab vigente E:/l2-local/research/dust2-animation-study/client-lab/system/L2.exe sigue abiertoPID12952. Se pidió cerrarlo vía pregunta asíncrona. No sobrescribir catálogo o recurso mientras abierto.

Cuando usuario confirme y procesoL2 ausente:
1. python build/install_lab.py: añade display59081 a npcgrp SOLO laboratorio, preserva6524filas anteriores byte porbyte, backup npcgrp.before.dat,413roundtrip; nuevo Dust2C4Demo.ukx. Guardas proceso/manifest/IDs. Dependencia Dust2DemoMotion debe ser exacta ya instalada.
2. Agente build/c4-agent.jar ya compilado, claseDust2C4DemoAgent. Cargar usando AttachElven de research/dust2-animation-study/npc/classes al GameServer VIGENTE (verificarPID; durante preparación25176). Argument directory=esta carpeta/build.
3. Agente retira viejo NPCV4 temporal y detiene su scheduler; crea902681/display59081 Demo C4 al conectarseHellkevin,85u delante/sameinstance. No modifica DB/template registry/core/clases/scripts. Espera10min; limpia20min. No reejecutar mientras activo. Log build/c4-runtime.txt.
4. Abrir laboratorio, usuario entra. Confirmar visualmente C4/postura/materiales. Perfil habitual no tiene catálogo y no debe ver esteNPC de prueba.

No bomba funcional, cuenta atrás, explosion, objetos inventario, kit ni integración en salas. Movimiento manos sigue borrador, no simulación exacta de dedos sobre botones; C4 fijado al root de demo para presentación, no objeto independiente ni recogible. Lógica plantar/desactivar siguiente etapa separada.

## Reproducción
build/build_scene.py crea escena desde animación de Studio adaptada; build/compile_package.py genera paquete UCC único Dust2C4Demo; build/link_mesh.py enlaza animación conservando offset absoluto. La ejecución UCC mantiene texturas sinDXT (xDxTex ausente) y comprobación pixelroundtripPASS. No reejecutar compilador sobre paquete existente creyendo que reconstruyó: usar nuevo nombre/limpiar únicamente salida de laboratorio con hash verificado. No tocar instaladores históricos.

# Actualización: TT y CT separados, instalados
Usuario aclaró: TT tiene C4 entre manos al plantar y CT lo desactiva sin levantarlo del suelo. Confirmó cliente cerrado.

Implementadas dos demostraciones, NO lógica de bomba:
- TT:151frames30fps/5s, preparación2s en manos, descenso2s y suelo1s; al repetir demo vuelve al comienzo. Movimiento de manos y torso adaptado a transición. Este reset es solo demo; no secuencia final de evento.
- CT:151frames30fps, postura más inclinada y brazos con solución analítica para llegar al panel. Error máximo de objetivos de mano0.0201u. C4 fijo sobre suelo en todos los fotogramas; pose base sigue de Studio con modificación de torso/brazos.
- Nuevo hueso C4_Anchor77 permite controlar objeto independientemente del cuerpo. CT anula movimiento del padre para mantener bomba fija. Es recurso combinado del NPC, no ítem independiente todavía.

build/build_actions.py produce C4TT/C4CT.blend,PSK,PSA,metrics. Materiales y preview C4CT-preview-first.png y C4TT-preview*.png. Paquetes únicos Dust2C4TT.ukx/C4MotionTT.ukx y Dust2C4CT.ukx/C4MotionCT.ukx. UCC compila0; UModel vuelve a cargar/exportar2233caras77huesos151frames,transformaciones idénticas0.0error y píxeles de4texturas exactos para ambos. actions-validation.json. No reemplazar con paquete inicial76huesos.

Instalados SOLO lab cerrado: display59081TT y59082CT,6524registros anteriores conservados byteporbyte +2, cifrado413roundtripPASS, backupactions-npcgrp.before.dat, hashesactions-installation.json. install_actions.py ya ejecutado, no repetir. install_lab.py inicial nunca ejecutado y queda histórico, NO ejecutarlo ahora.

Agente C4ComparisonDemo de compare.jar cargado enGS25176. Retira anterior demoV4, no redefine clases/core ni registra scripts/DB. EsperaHellkevin10min, crea dosNPC902681/902682 a90u delante con separación64u, misma instancia/geodata, nombres TT-ColocarC4 y CT-DesactivarC4. Limpia20min tras aparición. Estado build/comparison-runtime.txt es vigente. c4-agent.jar inicial NO cargado y no debe ejecutarse encima. Si expira, revisar estado antes de volver a desplegar; no duplicar.

Se está abriendo cliente lab. Validación visual de estas dos nuevas demos pendiente. Confirmación anterior 'perfecto' corresponde a NPCagachado sinC4, no certificar nuevas poses aún. Mecánicas kit, tiempo real de plantar/desarmar, roles, sitios A/B, propiedad bomba, explosión e interrupciones siguen pendientes y no tocamos salasPvP.
