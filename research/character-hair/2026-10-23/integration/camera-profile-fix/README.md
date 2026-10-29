# Corrección del perfil usado en juego

23/10/2026. El usuario mostró la tienda Cabellos vacía. Se comprobó mediante Win32_Process que L2.exe PID19140 ejecuta `E:/l2/system-camera-online/L2.exe`. La primera instalación había actualizado únicamente system-hud, perfil de 2-JUGAR.cmd.

Los catálogos de system-camera-online no tenían ninguno de los IDs28000–28012. Su L2.ini sí incluye las rutas compartidas ../Animations/*.ukx y ../SysTextures/*.utx, y los veinte recursos compartidos conservan sus hashes correctos.

Se añadieron únicamente los trece registros faltantes a armorgrp.dat y itemname-e.dat del perfil camera-online. Conservados los bytes de los 1263 y 9765 registros anteriores, respectivamente. Desensamblado, cifrado413 y roundtrip comprobados. Los resultados coinciden con los catálogos de system-hud, puesto que las dos bases anteriores eran iguales.

Aplicado al disco mediante reemplazo atómico con respaldo en `E:/l2-local/backups/hair-camera-profile-20261023-233125`. Evidencia y hashes: installation.json. No se cerró ni reinició el cliente o servidor. El cliente que ya estaba abierto conserva sus catálogos cargados: necesita cierre completo y nueva apertura para leer la corrección; volver a seleccionar personaje no basta para garantizarlo.

Pendiente confirmación visual del usuario al reabrir el juego. No presentar esta reparación como prueba de que todos los cabellos ya se renderizan correctamente. El verificador y rollback generales de integration incluyen también estos dos archivos; rollback requiere cliente y servidor cerrados y hashes sin cambios posteriores.
