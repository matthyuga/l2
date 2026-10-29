# Rueda de stickers: adaptación de D Oro

26/10/2026. Kevin eligió el estilo D Oro de la comparación de botones y preguntó cómo adaptarlo al menú de stickers. Se generó una propuesta visual sobre su captura. No se instalaron cambios ni se abrió/cerró el juego.

[Propuesta visual](propuesta-rueda-oro.png) · [Prompt](PROMPT.md).

Dirección propuesta: rueda de ocho medallones con bordes de hojas doradas, anillo exterior dorado y separadores finos, fondo oscuro con motivo floral tenue, placas legibles para los nombres y botón central CERRAR con el mismo material. Cabecera integrada STICKERS en lugar de la barra azul; resalte suave al pasar el cursor. Mantener orden, imágenes y acciones originales al implementar.

La imagen es una interpretación de ImageGen, no una captura nativa ni un atlas instalable. Las ilustraciones, letras y geometría recreadas por el modelo no sustituyen los recursos originales del juego. Antes de implementar se necesitan piezas sin texto, máscaras/alfa, estados normal/hover/pulsado, adaptación exacta al diámetro/hitboxes actuales y comprobar los campos de chrome de la ventana para retirar la barra azul sin alterar otras ventanas.

El selector D se ve correctamente en las capturas aportadas: bienvenida y rama de saludo con Continuar. Eso constituye validación visual parcial de la capa V5 de diálogo, no confirma por separado hover/pulsado de las cuatro familias.
