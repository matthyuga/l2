# L2: revelado de niebla intermitente - V7 preparada

27/10/2026. Kevin reporta que la niebla dejó de revelar recorrido fuera de Giran. Captura en Ruins of Despair y otra ampliada en Cruma Marshlands con recorrido parcialmente revelado. SQL de solo lectura confirma avance de457 a534 celdas; las visitas siguen registrándose y los snapshots llegan al cliente.

Trabajo: E:\l2-local\research\map-fog-refresh-v7-20261027 . V6 puede dejar el atlas sin refrescar cuando el motor conserva la textura sustituida y no vuelve por SetTexture(marker)/Device::Present. Se reprodujo en HAL sin rebind/Present: framebuffer no cambia tras snapshot. V7 refresca en las cuatro rutas de dibujo, únicamente si está enlazado el atlas de niebla.

Prueba corregida pasa tres descubrimientos sucesivos y aislamiento entre personajes. Pasan30415 checks nativos y HAL MANAGED/SYSTEMMEM->DEFAULT. Conserva progreso, reglas, servidor y HSL; guard de hash NWindow actualizado exactamente a la versión actual. No afirmar que la ruta swapchain concreta se observó en vivo ni que esto corrige el Critical Error de animaciones.

Estado: instalador install.py y rollback restore.py preparados; cliente seguía abierto. Se pidió salir y cerrar L2 antes de reemplazar únicamente system-hud/d3d9.dll. Esperar respuesta y comprobar proceso ausente; después instalar y validar START V7 / UPDATED V7 en NexusMapFog.log y visualmente al recorrer. No reiniciar GameServer ni borrar visitas.

Actualización: Kevin confirmó cierre completo. Instalado V7 con guardias el27/10 a las16:51:27, backup E:\l2-local\backups\map-fog-refresh-v7-20261027-165127. SHA256 del proxy058bf46ce269ec56b7de1fe370dd7b59d35552540fd175acbe5ed75ed7b68aa6. GameServer sigue en PID5460. No se modificó HSL, NWindow ni progreso. Pendiente usuario reabre cliente y confirma visualmente revelado al avanzar; comprobar logs V7 en esa sesión.
