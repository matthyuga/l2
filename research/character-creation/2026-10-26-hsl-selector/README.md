# Selector libre HSL — vista previa funcional

Estado: panel local de prueba, terminado y verificado en navegador. **Todavía no está integrado en el creador de Lineage II ni en el servidor.** Los colores exportados y los favoritos sólo afectan a esta vista previa. No hay guardado de colores HSL en personajes ni transmisión a otros jugadores.

Abrir index.html en Chrome, Edge u otro navegador con WebGL. No necesita servidor HTTP, conexión a Internet, librerías externas ni instalar dependencias: modelos y texturas están embebidos en models.js. También se dejó un enlace en las dos galerías anteriores.

Incluye los siete peinados seleccionados de Tanda 2 con modelos reales, cabezas originales y máscaras de tinte. Se puede girar el modelo con el ratón o flechas, ampliar con la rueda, elegir tono/saturación/luminosidad, introducir HEX, comparar con el original, guardar hasta doce favoritos locales y exportar una elección JSON. Las gafas, máscaras, piel y otros detalles protegidos quedan fuera del tinte al activar la opción correspondiente. Las máscaras manuales existentes pueden necesitar ajustes según el modelo; no hay soporte general todavía para todos los peinados Original y Tanda 1.

Pruebas: 4096 conversiones RGB→HSL→RGB exactas y diez casos HEX; sintaxis de los tres archivos JavaScript; veinte comprobaciones reales mediante Chrome headless con WebGL SwiftShader, incluidos siete modelos, campos inválidos, favoritos persistentes, alternancia original/color y distribución móvil sin desbordamiento horizontal. Se revisaron visualmente selector-preview.png, qa-FOrc-J.png y qa-mobile.png. El renderer web no reproduce exactamente la iluminación, los materiales ni el búfer de profundidad del motor de L2; no usarlo como prueba de una integración nativa.

## Investigación de la integración nativa

PlayerAppearance mantiene hairColor en byte y CharacterCreate valida 0..3; carga de Player utiliza getByte de la BD. CharInfo, UserInfo y CharSelectionInfo envían el color mediante un campo int de 32 bits. Esto abre la posibilidad de conservar A-D como compatibilidad y agregar un valor de color separado, pero no basta con enviar un RGB en el campo existente: el cliente lo interpreta como índice y podría acceder a tablas fuera de rango.

REA inspeccionó los materiales nativos del engine: UColorModifier existe y UConstantColor::GetColor lee un FColor de 32 bits en +0x578. Evidencia ev_5e843e43e7a2a0195de6ace877e005a89ef5f67e92647bcc4f3ae57b56d42c72 en rea-color-materials.txt. El hecho de que el motor tenga un material de color no demuestra que pueda sustituirse automáticamente por HSL ni que conserve por sí solo las zonas sin tinte.

Trabajo pendiente para cumplir la integración solicitada: construir/probar una ruta de material nativo que preserve alfa y la máscara de tinte; añadir el control HSL al creador y actualizar la previsualización; definir un valor separado persistente con color A-D de reserva; conectar la recepción y transmisión en creación, selección, UserInfo y CharInfo; comprobar reconexión y vista de otro cliente. Hay que ampliar también el soporte de modelos/máscaras a Original y Tanda 1 si se aplica a todos los peinados actuales. No desplegar sólo el cambio de protocolo antes de que exista la ruta cliente que lo interpreta.

No se modificaron archivos activos del cliente/servidor, cuentas ni personajes durante esta fase. La versión v14 que retira las caras problemáticas del orco sigue activa. El prototipo es el primer resultado revisable para esta ampliación, no una afirmación de que el selector HSL ya funcione dentro del juego.
