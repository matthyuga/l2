# Niebla V7 - actualización al dibujar

27/10/2026. Estado inicial: corrección compilada y verificada en HAL aislado; pendiente instalar con cliente cerrado y validar dentro de L2.

## Estado actual: instalada

Kevin confirmó cierre completo. install.py verificó ausencia de L2 y hashes; V7 instalada a las16:51:27. Respaldo: E:\l2-local\backups\map-fog-refresh-v7-20261027-165127. GameServer PID5460 siguió funcionando. La verificación SQL posterior conserva el progreso. Falta reabrir el cliente y confirmar revelado continuo dentro de L2; installation.json conserva ese estado pendiente.

## Problema observado

Kevin reporta que al recorrer Gludin y otras zonas la niebla deja de desaparecer. Una captura posterior muestra recorrido parcial revelado y marcador cubierto en Cruma Marshlands. Servidor sigue registrando lugares y enviando snapshots. Consulta SQL de solo lectura encontró457 celdas personales: no se perdieron las visitas.

El proxy V6 actualiza el atlas al recibir el marcador en SetTexture o en IDirect3DDevice9::Present. Tras sustituirlo dentro de la caché nativa, el motor puede conservar directamente la textura dinámica; no hay garantía de volver a pasar por el marcador ni de presentar mediante ese método del dispositivo. La causa de que falte esa ruta en el cliente concreto requiere observación adicional; no se afirma haber trazado su swap chain.

## Reproducción y cambio

refresh_test.cpp usa el código real del proxy sobre Direct3D9 HAL. Conserva el atlas ya enlazado, inyecta snapshots con tres descubrimientos y dibuja sin volver a enlazar textura ni llamar a Present. Antes de la corrección falló en el primer avance: framebuffer4e5860 sin cambio.

V7 actualiza en el límite real de dibujo, antes de las cuatro rutas DrawPrimitive/Indexed/UP. Si el snapshot no cambió, la generación del atlas es un no-op. Conserva resolución, celdas, Giran, capas personal/global, transporte, clipping y restauración de estado. El guard de hash se ajusta exactamente al NWindow HSL actualmente instalado; no se desactiva.

La misma prueba pasa los tres avances: 4e5860,3e4850 y444e56 cambian a208020; personaje nuevo continúa cubierto. Pasan30415 comprobaciones nativas y pruebas HAL MANAGED y SYSTEMMEM->DEFAULT del framebuffer final, restauración de estados y16Present.

## Instalación y revisión real

install.py rechaza instalar si L2 está abierto o los hashes base cambiaron. Reemplaza únicamente system-hud/d3d9.dll, conserva respaldo y log. No modifica base de datos, progreso, GameServer, HSL ni NWindow. restore.py revierte ese archivo con guardias de identidad y cliente cerrado.

Al reabrir, buscar START map fog V7 y UPDATED V7 exploration atlas before draw en NexusMapFog.log. Caminar a terreno nuevo con el mapa abierto debe ampliar el revelado; verificar también chico/ampliado y persistencia al reconectar. Las pruebas aisladas no sustituyen esta validación visual.

El cierre previo en UpdateAnimation permanece como investigación separada: V7 no se presenta como solución de ese crítico.
