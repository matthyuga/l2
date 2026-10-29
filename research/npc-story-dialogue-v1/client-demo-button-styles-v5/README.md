# Cuatro estilos de botones — V5

Instalados el 26/10/2026 con L2 cerrado. Validación visual parcial recibida: las capturas de Kevin muestran D Oro activo en bienvenida y rama de saludo con Continuar. Kevin eligió Oro. Los otros estilos y estados hover/pulsado no se confirmaron por separado.

## Cómo probar

Abrir L2 normalmente, entrar al mundo y pulsar AMBER. Encima del panel aparece la fila **Botones:**

- **A Metal:** carbón y bronce grabado.
- **B Papel:** pergamino claro y herrajes.
- **C Cristal:** violeta, plata y gemas.
- **D Oro:** hojas y marco dorado orgánico.

El indicador **Actual: A/B/C/D** identifica el seleccionado. El cambio se aplica a respuestas, Continuar/Volver al inicio, X, Original/Compensar y Opaco/Semi/Transparente de las cuatro páginas. Los cuatro selectores conservan sus propios estilos para identificarlos.

Pasar el cursor y pulsar para comprobar normal/hover/pulsado. Recorrer ambas respuestas y volver a abrir el diálogo. La selección está preparada para conservarse durante la sesión; al reiniciar el cliente vuelve a A, fondo Semi y retrato compensado. No se guarda una preferencia permanente todavía.

## Implementación

Nuevo paquete NexusAmberButtonsV5.u: 136 texturas. Cuatro familias × diez tipos de botón × tres estados, más doce texturas para selectores y cuatro indicadores. Las letras se dibujan a resolución nativa después de adaptar el arte, en vez de reducir los textos de la lámina conceptual. Para papel se usan letras oscuras.

Los originales de ImageGen están en sources/A.png a D.png, con transparencia real. Se recortan por celdas y se adaptan preservando extremos; los controles compactos y X tienen piezas propias. Las respuestas crecen de 34 a 42 píxeles de alto para dar espacio al detalle. Los fondos y el marco ornamental V4 se reutilizan sin modificación.

Nueva clase AmberButtonStylesUI: 17 funciones, 15 rutas de botón. Las funciones de estilo usan UIScript.GetHandle, conversión a ButtonHandle y SetTexture con tres strings. Se verificaron las firmas en NWindow.u. Cada selección cambia 29 botones existentes en las cuatro páginas y los cuatro indicadores; no solicita handles de controles inexistentes. No hay sondeo, temporizadores ni nuevas llamadas de red.

Interface.u conserva todos los exports anteriores. Interface.xdat mantiene las 147 ventanas: cuatro páginas y el enlace de script del lanzador se actualizan; las otras 142 ventanas quedan byte a byte iguales. El lanzador AMBER conserva su apariencia anterior. Ningún cambio de servidor, quests o gamma global.

## Comprobaciones

- UCC, CRC y roundtrip exacto del paquete de texturas; inventario completo de nombres de 136 texturas.
- Lectura fresca de clase y bytecode, cadena de campos sin ciclos, destinos de saltos y tamaños de Context correctos.
- Simulación de cuatro estilos × tres fondos × dos modos de retrato, con navegación de las ramas, continuación, reinicio, cierre, reapertura, botón desconocido y salida del mundo.
- Los 45 paths de botones (29 afectados y 16 selectores) existen en el XDAT; controles dentro de ventana y sin superposición entre botones.
- Conservación de exports y ventanas ajenas; roundtrip XDAT exacto; hashes de entrada y de instalación y respaldo.

Las comprobaciones de VM y las previsualizaciones NO reemplazan validar el renderizado y los eventos nativos dentro de L2. Previsualizaciones revisadas a 1024×640 y 1280×720, no capturas del juego.

## Recursos

- [Comparación en el panel](comparacion-en-panel.jpg).
- [Botones al tamaño nativo](botones-tamano-nativo.png).
- preview-A-1024.png a preview-D-1024.png; preview-D-1280.png.
- [Prompts de las cuatro llamadas a ImageGen](PROMPTS.md).
- verify-button-styles.log, build-button-styles-xdat.log, build-verification.json, input-hashes.json, output-hashes.json, installation.json.

## Restauración

Respaldo: `E:\l2-local\backups\npc-story-button-styles-v5-20261026-143650`.

Con L2 cerrado:

`python E:\l2-local\research\npc-story-dialogue-v1\install-button-styles.py --restore`

Para comprobar sin modificar, agregar `--check`. Devuelve a la interfaz angular con fondo ornamental V4 y botones anteriores. Hay una capa posterior instalada: stickers dorados V7 modifica el XDAT compartido, por lo que debe retirarse antes de restaurar V5. Después retirar V5 antes de V4 y V3. No reejecutar constructores históricos sobre la capa instalada.
