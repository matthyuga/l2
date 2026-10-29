# Fafurion Weapons

Integración inicial instalada el 12/10/2026. Siete armas nuevas, IDs 54130–54136, base grado S. Sockets todavía en diseño.

- [Integración, stats y comandos GM](../../FAFURION-ARMAS-INTEGRACION.md).
- [Propuesta de sockets y activaciones](../../FAFURION-SOCKETS-PROPUESTA.md).
- `manifest.json`: origen, IDs, estadísticas y hashes de catálogos.
- `installation.json`: respaldo y destinos instalados.
- `verification.json`: comprobación del cliente y archivos instalados.
- `runtime-verification.txt`: parser y registro real en GameServer.
- `System_Fafurion_Weapons`: extracción original del archivo recibido.
- `stage`: entradas añadidas, XML, catálogos combinados y exportaciones de referencias.
- `preview`: exportación de las seis mallas/materiales mediante UModel; no es una prueba visual dentro del juego.

`build_integration.py` e `install.py` son herramientas de primera instalación: no volver a correr sobre esta instalación. `verify_installation.py` verifica el estado sin cambiar cliente/servidor, usando codec y UModel locales. `FafurionLoad.java` y su JAR se usaron una sola vez para registrar los nuevos datos en el servidor abierto sin reemplazar templates existentes. En el próximo arranque normal el XML se carga desde disco.

Las siete armas están en el botón Fafurion de Mirella (48.800.000 Adena) y de //gmshop (gratis). Listas y HTML cargados y verificados en el GameServer abierto; ver `shop-verification.txt` y `shop-installation.json`. `add_shop.py` y el agente FafurionShopLoad son herramientas de primera instalación, no actualizadores. No se agregaron drops/recompensas ni objetos a inventarios existentes. No hay skills custom de Fafurion activas. La lanza conserva únicamente el ataque múltiple nativo de su tipo.

V2 instalada tras capturas de Kevin: alias visuales24130–24136 corrigen el campo short de multisell para los objetos originales54130–54136; descripciones NUL corrigen concatenación de SA ajena. Sin cambiar objetos comprados ni stats. Ver `client-fix-v2/manifest.json` y `runtime-verification.txt`; verificador principal PASS incluye paquete serializado real. Confirmación visual tras reabrir pendiente. No reejecutar fix_client_v2/agente como actualizadores.
