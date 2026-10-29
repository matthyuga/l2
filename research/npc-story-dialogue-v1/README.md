Estado actual (26/10/2026): V5 instalada con selector de cuatro estilos de botones A Metal / B Papel / C Cristal / D Oro. Fondo ornamental V4, opacidad y compensación V2 conservados. Ver client-demo-button-styles-v5/README.md. Validación visual y de clics en L2 pendiente. Las notas posteriores describen las capas históricas.

Estado actual: compensaci?n local V2 instalada y confirmada por el usuario. Ver client-demo-gamma-v2/README.md. El retrato usa una LUT inversa de la gamma real capturada por REA; botones Original/Compensar, sin modificar gamma global.

# Conversación de Amber — prueba nativa V1

Instalada el 24/10/2026. Pendiente validación visual y de clics dentro de L2.

## Cómo probar

Abrir L2 y entrar al mundo. Buscar el botón naranja **AMBER**, cerca del botón de stickers, en la zona superior derecha. Al pulsarlo se muestra el retrato y el panel de conversación.

Elegir **Quiero conocer este lugar.** o **Solo pasaba a saludar.** para ver las dos ramas. **Continuar** llega al cierre. **Volver al inicio** permite repetir. La **X** cierra la ventana. Probar ambas respuestas y confirmar que el panel, texto y botones se ven completos.

## Alcance real

Prototipo local de interfaz: un retrato neutral, cuatro páginas de texto fijo y dos respuestas. No está enlazado todavía al clic del NPC del mundo, no guarda decisiones en servidor y no modifica quests, recompensas ni el lore. Las expresiones amable/seria, el texto dinámico y la conexión con el NPC serán una etapa posterior.

Se usan el panel Tooltip_Box y el botón Standard_Button_orange de Dark_UI_free_demo.zip; el archivo promocional no se usa como textura. Bordes adaptados en nueve regiones para preservar las esquinas. Botones horneados a sus tamaños nativos (normal/hover/pulsado), con texturas de potencia de dos y padding. Retrato Amber neutral generado previamente, con transparencia.

Cambios de cliente: nuevo paquete NexusAmberStoryV1.u, nueva clase AmberStoryDemoUI en Interface.u y cinco ventanas en Interface.xdat. Todos los exports previos de Interface.u y las142 ventanas previas se conservan byte a byte. No hay timers, sondeo de teclado, bypass nuevos ni cambios de servidor. El texto de las páginas se genera en build-demo-xdat.groovy; amber-demo.json es el borrador narrativo y aún no es un formato cargado en runtime.

## Verificación y límites

Compilación UCC; paquete de texturas con wrapper121, CRC y roundtrip exacto. Lectura nativa fresca de clase y funciones; cadena de campos sin ciclos; saltos VM a límites válidos. Simulación de los tokens realmente serializados: apertura, ambas respuestas, continuación, reinicio, cierre, botón desconocido y salida del mundo. Comparación de exports y ventanas ajenas. Roundtrip XDAT exacto.

client-demo/expected-layout.png es una composición prevista de referencia, NO una captura del juego. Las comprobaciones anteriores no prueban por sí mismas la apariencia, los clics ni la estabilidad dentro de L2.

## Restauración

Respaldo: E:\l2-local\backups\npc-story-dialogue-demo-v1-20261024-190025.

Cerrar L2 y ejecutar `python E:\l2-local\research\npc-story-dialogue-v1\restore-demo.py`. Compara hashes y vuelve al estado inmediatamente anterior a esta demo, con los stickers funcionando. Para restaurar también los stickers, retirar primero esta demo y después usar el rollback de stickers. Sus guardas detectarán esta capa posterior y evitarán sobrescribirla accidentalmente.

Archivos de trabajo en client-demo/: installation.json, input-hashes.json, client-verification.txt, build-verification.json y logs de compilación. build-demo.py no debe volver a ejecutarse sobre el cliente ya modificado: parte del snapshot current, con guardas contra cambios concurrentes.

Validación parcial del usuario: «se ve bien», con capturas de bienvenida y rama de conocer el lugar/Continuar. Aparición del retrato, panel y navegación de esa respuesta confirmadas. Cierre/reinicio y segunda rama no confirmados por separado. Reporta sobreiluminación global de pantalla al tener L2 abierto, incluso en VS Code, ausente en capturas: diagnóstico independiente en research/display-gamma-v1; no retocar el arte para compensarlo todavía.
