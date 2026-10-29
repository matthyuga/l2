# L2 Hellgames: primeras decisiones

17/10/2026. Decisiones de Kevin para la versión destinada a jugadores. L2 Lab sigue siendo el entorno de experimentación; L2 Academy es la versión local limitada al Coliseo.

## Ingreso y equipo

- Nivel inicial 1.
- Todas las clases disponibles según el sistema que venimos desarrollando; conservar la separación actual entre raza/origen, clase activa y subclases. No convertir automáticamente nivel 1 en nivel máximo.
- Cuenta la raza inicial. La apariencia racial y el origen de STR/DEX/CON/INT/WIT/MEN se conservan independientemente de la clase.
- El servicio VIP permitirá cambiar apariencia, origen de atributos o ambos de manera independiente. La implementación GM ya existe; acceso público, precio y cobro todavía pendientes.
- Set inicial A, joyería A completa y un arma A.
- Kevin aprobó expresamente arma con SA. Base propuesta para implementar: +0; Tallum Heavy, Majestic Light o Dark Crystal Robe; joyería Majestic. La respuesta «sí con SA» confirma la SA; los modelos concretos de set siguen siendo la propuesta de partida, no una elección individual expresa.
- El muelle será la llegada compartida y pacífica. Ya está construido y configurado en Lab; la copia base de Hellgames conserva ese nacimiento.
- Evitar duplicar equipo al repetir/reconectar. Diseñar entrega persistente y auditada antes de habilitarla.
- Resolver uso de A a nivel 1: la configuración copiada aún tiene ExpertisePenalty=True. No declarar equipo inicial funcional hasta probar esa compatibilidad.

## Progresión de equipo

- Shop de armas: solo S comunes. Catálogo exacto y precios pendientes.
- Armaduras y armas custom: categorías de diseño SS y SSS.
- Interlude/core actual solo tienen grados nativos hasta S. SS/SSS requieren definir presentación y reglas; no basta agregar letras al enum del servidor. No inventar estadísticas o poderes por falta de datos.

## Moneda propuesta por Kevin

- Nombre: Hellcoin / Hellcoins.
- 1 Hellcoin = 1 Goldenbar.
- 1 Goldenbar = 1.000.000.000 Adena (1kkk).
- Tarifas propuestas: 1 USD por Hellcoin o 1.000 ARS por Hellcoin.

Estado: propuesta económica documentada; no se habilitaron pagos, donaciones, banco ni canjes. No se fijó la equivalencia USD/ARS como un tipo de cambio real. Las dos tarifas requerirán mantenimiento si se publican.

Pendientes prácticos:

- Calibrar 1kkk con ingresos reales de Adena y precios. El número aislado no define dificultad ni valor.
- Decidir direcciones de conversión: si Adena también compra Hellcoins, los jugadores podrán obtener la moneda mediante juego. No implica devolución en dinero real.
- Usar enteros y comprobar límites de inventario/cantidades; nunca calcular monedas con coma flotante.
- Evitar arbitrajes por compras/ventas de NPC y duplicación. Gold Bar nativo ID3470 tiene precio ordinario; no convertirlo en un vale de 1kkk sin revisar todas sus fuentes y usos.
- Precio y ventajas VIP pendientes; no abrir automáticamente el comando GM racial al público.

La separación de entornos se priorizó antes de implementar el selector o modificar la economía. No se entregó equipo ni se alteraron personajes del Lab.
