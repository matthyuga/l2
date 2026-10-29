# Muelle: revisión de acceso y registro de actores

14/10/2026, E:\l2-local. Kevin aclaró que `.muelle` lo mostraba en Giran, sin haber visto el muelle. No tratarlo como simple queja visual de la arquitectura.

Handler real probado con Player transitorio, sin DB: Giran -> muelle149000,46700,12021 -> onTeleported -> Coliseo. PASS. Posición guardada de Hellkevin coincidía con muelle; no acredita lo que dibujaba su cliente.

Corregidos nueve actores con cabecera de estado RF_HasStack y propiedades de filtro/visibilidad conforme a nativos y acmi/L2smr. Publicados seis exports de material AcademyCloud que antes no tenían flag Public. Solo cambiaron mapa24_19 y HGGludioSky_T del cliente. Backup adicional backups/gludio-actor-registration-20261014-095028; manifest original actualizado sin perder restauración de base.

Añadido `.muelle estado`, logs de viaje y instancia0/offsetfalse explícitos. Recarga de métodos solo de GludioSky, sin restart ni cambios de personajes. Carga de recursos y pruebas estructurales PASS. UI Windows no disponible (native pipe ausente incluso tras reset): entrada visual y causa final del Giran observado todavía pendientes. Documento MUELLE-AEREO-GLUDIO.md, research/gludio-sky/{actor-registration-v2.json,travel-probe.txt,reload-proof.txt}. Sin commit/push.
