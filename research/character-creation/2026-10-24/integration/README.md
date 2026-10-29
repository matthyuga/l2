# Ampliación del creador de personajes — 24/10/2026

Instalado en `E:\l2\system-hud` (2-JUGAR) y `E:\l2\system-camera-online` (14-ABRIR-OBSERVADOR).

- Dos peinados adicionales por modelo, identificados como **Nuevo 1** y **Nuevo 2**, después de los originales. Cuatro colores para cada uno.
- Tres caras adicionales por modelo: **Type D, E y F**. Son texturas nuevas sobre la geometría original de cada raza.
- Cubiertos los 14 modelos Interlude: humanos guerreros/místicos, elfos, elfos oscuros, enanos y orcos guerreros/místicos, ambos sexos. Total: 28 cabellos y 42 caras.
- Opciones originales conservadas. No son accesorios equipables. Los cosméticos Baium anteriores son independientes.

El cliente tiene un paquete propio `NexusAppearanceV1.u` y cambios limitados a `engine.dll`, `NWindow.dll` y las dos etiquetas añadidas a `sysstring-e.dat`. Los cambios nativos se aplican únicamente a las versiones con los hashes documentados en `native-manifest.json`; no reutilizar DLLs de este parche en otros clientes sin adaptación.

Los modelos se recompilaron a formato UE2 versión 123 con el editor local. Se adaptaron al esqueleto nativo de cada raza, conservando geometría y pesos de huesos compatibles. Los huesos exclusivos de crónicas modernas se vincularon a la cabeza: esos cabellos no conservan su animación secundaria original.

Servidor: `CharacterCreate` acepta caras 0–5, cabellos masculinos 0–6, femeninos 0–8 y orca guerrera 0–6; conserva colores 0–3. Cambiados el código fuente, el overlay cloud y las entradas correspondientes en los JAR de runtime/dist. Clase actualizada en el GameServer en ejecución, sin reiniciarlo ni modificar personajes, inventarios o base de datos. El overlay se guarda localmente; no se publicó.

Verificado: 2.179 escenarios x86 de recursos/selección/ABI, incluida carga reubicada del motor; 13.608 escenarios del bytecode compilado de validación del servidor; carga/exportación de los 28 modelos y 154 texturas, coincidencia de geometrías, compatibilidad de huesos y colores. Paquetes cifrados con ida/vuelta comprobada. Puerto 7777 activo después de recargar.

**Pendiente:** comprobación visual en el cliente real, movimiento y posibles cruces con cascos/accesorios; no se ha creado un personaje real durante estas pruebas. Las pruebas de emulación y carga de recursos no sustituyen esa comprobación. Los otros clientes que se usen en este servidor también necesitarán esta ampliación para mostrar estas apariencias.

Uso: cerrar cualquier cliente anterior, abrir **2-JUGAR** y avanzar a creación de personaje; recorrer Hairstyle hasta Nuevo 1/Nuevo 2 y Face hasta D/E/F.

Respaldo completo y hashes: `installation.json`, con copia en `E:\l2-local\backups\character-appearance-20261024-005140`. Restauración, con el cliente cerrado y sin jugadores conectados:

```powershell
python E:\l2-local\research\character-creation\2026-10-24\integration\rollback.py
```

El restaurador comprueba hashes y se detiene si detecta cambios posteriores, para evitar sobrescribirlos. No ejecutarlo salvo que se quiera retirar esta integración.
