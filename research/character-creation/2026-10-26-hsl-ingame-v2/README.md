# HSL v2 — destello y rendimiento

Instalada en ambos perfiles el 26/10/2026. Cambia únicamente NexusHairHslGame.dll; los hooks NWindow/engine, las texturas originales, el servidor y el protocolo se mantienen. Revisión visual del usuario pendiente.

## Diagnóstico con REA

El usuario confirmó el panel y el cambio de color de v1, pero observó un destello del original y pérdida de fluidez al arrastrar.

- `rea-v1.json`, evidencia ev_82275068965de0025de56060ab126e7ed2340b38c2268e6bc635ea4867d57ef9: NexusHairTexture ejecutaba una consulta GetPrivateProfileIntW sobre NexusHairHslQA.ini por cada dibujo de textura. Era un control de diagnóstico innecesario en el recorrido frecuente.
- `rea-root-cause.json`, evidencia ev_55bd0256d4fcf3268e33b7d81e011b7778c9fe9f7bafe327b08afa80cff50f55: la actualización del panel llamaba al setter nativo de Hair Color cada 40 ms durante el arrastre. Ese setter vuelve a asignar recursos de apariencia y el tinte se reaplicaba después desde el polling, dejando una ventana en la que podía dibujarse el material original.

Esto demuestra los recorridos del binario; no es una medición de FPS del juego.

## Corrección

- Diagnóstico de configuración solo una vez, fuera del recorrido de cada textura.
- Los cambios RGB actualizan el material temporal ya asignado, sin llamar al setter de apariencia cuando el personaje de previsualización está registrado. El setter queda como respaldo de inicialización si aún falta ese registro.
- Seguimiento explícito del personaje del creador y filtrado por modelo elegido. Reaplicación inmediata después de cambios de apariencia; no se espera al polling cuando el material ya está disponible.
- Tabla de 256 niveles de luminancia para conservar el detalle del cabello. Evita convertir HSL por cada píxel del atlas. Conserva exactamente alpha y píxeles protegidos.
- Plano tono/saturación almacenado y reutilizado mientras no cambia la luminosidad.

## Pruebas

20506 comprobaciones nativas existentes; 183 transiciones ejecutando la función real de actualización sobre estructuras aisladas, sin ningún recurso nativo de recarga disponible: instancia de material conservada durante 180 cambios, restauración Clásico/Libre y filtro de modelo.

Benchmark local sobre 524288 píxeles, ocho cambios por implementación: v1 75,619 ms por tinte; v2 2,850 ms, aproximadamente 26,5 veces más rápida esa operación. Diferencia máxima RGB observada: 1/255; alpha y zonas protegidas exactos. No equivale a una mejora de FPS de 26,5 veces.

Preflight de motor real volvió a pasar en el perfil aislado automático: lectura, máscara, textura dinámica, transparencia, clon de material, panel UTexture y recursos GDI estables. No sustituye la revisión visual del destello y fluidez en el creador real.

## Copia y retorno

`installation.json` incluye hashes y respaldo de v1, además de actualizar el manifiesto v1 para que su rollback completo siga siendo utilizable. Respaldo: `E:\l2-local\backups\hair-hsl-ingame-v2-20261026-232116`.

Con L2 cerrado: `python research/character-creation/2026-10-26-hsl-ingame-v2/rollback.py` vuelve a v1. Para retirar todo HSL, el rollback v1 conserva las copias anteriores a la integración; comprueba hashes antes de escribir.
