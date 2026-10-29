# Separación de entornos — 17/10/2026

Estado de la separación: VERIFIED. Ambos runtimes iniciaron, completaron las verificaciones y quedaron detenidos. Lab continuó en su proceso original.

## Verificaciones realizadas

- Bases nuevas inicializadas con esquemas nativos; cero cuentas y personajes antes del primer arranque. No se importó la base del Lab.
- Conexiones, scripts permitidos, nacimiento, nivel inicial y cliente de cada perfil: `verify_profiles.py`, resultado `static-verification.json`.
- JAR y ejecutable del cliente tienen contenido idéntico a la copia base y archivos independientes, sin hardlinks.
- Etiquetas del selector del cliente: L2 Hellgames y L2 Academy. Parser/cifrado roundtrip, conservación de filas ajenas y sufijo opaco de 743 bytes.
- Hellgames: arranque completo, registro en LoginServer y `HELLGAMES_ARRIVAL_READY`, cero spawns públicos habilitados todavía. Sin errores de carga en el arranque final.
- Academy: arranque completo, límite de una conexión y cuatro NPC de servicios cargados; `ACADEMY_WORLD_READY` y `ACADEMY_TELEMETRY_PASSIVE`.
- Límite del Coliseo: 11 casos de coordenadas/altura/instancia en prueba Java. Prueba adicional con objeto Player real, transitorio: retorno desde Giran y muelle, `ACADEMY_RETURN_TEST PASS`.
- Academy preparó los 39 perfiles de rivales en su propia base y los verificó tras recarga: `ACADEMY_ROSTER_TEST PASS`. Resultado final: cero cuentas, 46 personajes técnicos reconocidos por nombre y ninguno online. Hellgames conserva cero cuentas y cero personajes. Detalles en `runtime-verification.json` y logs verificados conservados junto a este informe.
- Los tres GameServer escucharon simultáneamente: Lab 127.0.0.1, Hellgames 127.0.0.2 y Academy 127.0.0.3, todos en 7777. Evidencia `parallel-listeners.json`. Lab conservó PID 17892.

## Correcciones durante la validación

- Corregida referencia XSD de guardianes en las copias. Hellgames no carga un XML de spawns vacío, incompatible con el esquema.
- HellgamesArrival sustituye GludioSky para no cargar la tripulación experimental adjunta a esa carpeta del Lab.
- Academy conserva telemetría de duelos, pero no programa benchmarks del Lab dependientes de sus personajes/tablas.
- `.roster preparar` accesible sin GM solo en Academy. Los rivales se preparan en su propia base; no son personajes copiados del Lab.
- Durante la generación exclusiva de perfiles técnicos se usó temporalmente `innodb_flush_log_at_trx_commit=2`. Se restauró a 1, se ejecutó `FLUSH ENGINE LOGS`, se comprobó el valor y se cerró MariaDB de forma ordenada. Ninguna configuración persistente de durabilidad cambió.

## Límites

No se comprobó visualmente el cliente nuevo en vivo. No se hicieron pruebas de capacidad o acceso desde Internet. Academy funciona con servicios locales y conserva archivos del mapa completo; el controlador limita el área jugable y puede devolver al jugador hasta 500 ms después de salir. El límite de una conexión se verificó en configuración y arranque, sin dos clientes conectados.

El selector de equipo A con SA, shops, VIP y economía de Hellgames siguen pendientes. Decisiones en `HELLGAMES-DECISIONES-INICIALES.md`.
