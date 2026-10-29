# L2: muelle aéreo sobre el Coliseo

14/10/2026, E:\l2-local. Kevin autorizó integrar el muelle aéreo de Gludio alto sobre el Coliseo, con llegada inicial y ambiente pertinente.

Instalación de prueba: ocho actores en 24_19.unr, suelo alrededor de Z12016, nube opaca debajo (Z7600), cielo/ciclo nativo conservados. Inicio de personajes nuevos149000,46700,12040; existentes pueden usar .muelle estando desmontados y fuera de combate/instancias; .muelle coliseo para bajar. Zona pacífica y respawn local. No se movieron masivamente personajes existentes.

Conversión real de mallas y bloques nativos de materiales Gracia37→Interlude28, geodata de colisiones añadida manteniendo capas inferiores, paquetes HGGludio aislados y respaldados. Lecturas nativas, wrappers/CRC y smoke del servidor PASS. Primera entrada visual y recorrido manual siguen pendientes: no afirmar ausencia de tierra visible en todos los ángulos ni jugabilidad exhaustiva.

Documento: E:\l2-local\MUELLE-AEREO-GLUDIO.md. Código/evidencias y manifest: research/gludio-sky. Backup backups/gludio-sky-20261014-092638; restore.py requiere cliente/GS cerrados y hashes coincidentes. No reejecutar build.py/instaladores sobre el mapa instalado. Otros mapas siguen disponibles; no es todavía cliente Academy reducido. Sin commit/push.
