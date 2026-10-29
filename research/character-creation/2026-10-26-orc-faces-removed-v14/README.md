# Caras nuevas de orco retiradas ? v14

Por petici?n del usuario tras repetir el critical error v13, se retiran D/E/F del selector del orco guerrero masculino. Las tres compart?an la cabeza problem?tica; permanecen A/B/C. No se intenta una nueva cabeza custom.

El motor utiliza cabeza y textura A nativas para cualquier ?ndice D/E/F ya guardado en ese modelo. As? se evita cargar las cabezas v12/v13 aunque un personaje conserve su ?ndice. No se modific? ninguna fila de personaje ni el servidor. Las opciones de cabello, colores y caras de otros modelos se conservan.

Se actualizaron engine.dll y NWindow.dll en ambos perfiles, con backups. Los paquetes ?nicos v12/v13 se conservan inactivos para diagn?stico; no hay ninguna ruta hacia ellos en los nuevos engines. La reversi?n global de Tanda 2 tambi?n conserva la retirada de estas caras. Las revisiones anteriores y sus rollback est?n protegidos por hashes y no deben forzarse.

Pruebas: 2303 casos de recursos/ABI/selector; 15486 casos de Tanda 2, incluido mantener tres caras s?lo en Orc Fighter masculino; 5824 casos de conteo y 112 replays de materiales. Hashes instalados, backups y manifiesto global de rollback verificados. No se valid? visualmente el selector dentro del juego.
