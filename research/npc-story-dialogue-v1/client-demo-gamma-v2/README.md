# Compensación local del retrato — V2

Estado: preparada y verificada, NO instalada. El intento de instalación se detuvo porque L2 estaba abierto. El usuario pidió un efecto inverso limitado a la figura; no aplicar la configuración neutral global preparada anteriormente.

Se calculó una LUT inversa por canal de la curva real capturada por REA (display-gamma-v1/rea-runtime-user-test.json). La textura del retrato recibe esa transformación antes de que L2 aplique su gamma de salida. El canal alfa se conserva; no se agrega un rectángulo oscuro sobre el escenario. Las imágenes originales permanecen intactas.

Nuevo paquete NexusAmberGammaV2.u: retrato compensado y dos juegos de botones. En las cuatro páginas de conversación habrá **Original** y **Compensar**. Las funciones usan NWindow.UIAPI_TEXTURECTRL.SetTexture; se comprobó contra NWindow.u que recibe dos strings. Ambos botones actualizan las cuatro páginas, sin depender de estado compartido entre instancias. La charla mantiene sus respuestas y navegación originales.

La compensación queda activa inicialmente. La selección de Original/Compensar se conserva al avanzar entre páginas durante la sesión. El reinicio del cliente vuelve a la textura predeterminada compensada. No es una solución del brillo global ni altera VS Code, el escritorio, el escenario o el panel. Si se cambia la gamma del juego habrá que recalcular o desactivar la compensación.

Límite medido: la curva de L2 levanta negro a3277/65535. Los tonos por debajo de ese nivel no pueden recuperarse exactamente con esta técnica. El reescalado y la composición alfa pueden introducir pequeñas diferencias. expected-compensation.png es una simulación matemática de referencia, NO una captura de L2.

Verificado: inversión de curva y alfa preservada, texturas con wrapper121/CRC/roundtrip, lectura nativa y saltos VM, simulación de navegación y ambas funciones SetTexture, preservación de exports ajenos y143 ventanas no modificadas, XDAT exacto. Falta evaluación dentro del juego.

Instalar con L2 cerrado: `python E:\l2-local\research\npc-story-dialogue-v1\install-gamma-demo.py`. Restaurar esta capa: `python E:\l2-local\research\npc-story-dialogue-v1\restore-gamma-demo.py`. Ambas operaciones verifican hashes. Después de retirar V2 se puede retirar V1 con restore-demo.py y luego los stickers, en ese orden.
