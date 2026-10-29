# Primera prueba de niebla del mapa

Actualizado a V2: abrí L2 como siempre y luego el mapa. El continente debe quedar cubierto de niebla y la ciudad de Giran despejada, con un borde suave e irregular.

1. Arrastrá el mapa: Giran debe seguir despejada en su ubicación real.
2. Pulsá Enlarge Map: el claro debe conservar su ubicación en el terreno.
3. Probá NIEBLA-2-OPACA.cmd y NIEBLA-1-PARCIAL.cmd en esta carpeta.
4. NIEBLA-3-APAGAR.cmd quita la cobertura sin cerrar el juego.
5. Centrar ya no es necesario: la ciudad tiene una ubicación fija.

Esta cobertura aplica por ahora una regla fija: solo Giran despejada. Todavía no está conectada a .explora. No hace falta reiniciar el servidor.

Si no aparece o algo se ve mal, conservar E:\l2\system-hud\NexusMapFog.log para diagnóstico. Para volver a la prueba del rectángulo, cerrar el juego y ejecutar `python research/map-fog-giran-v2/restore.py` desde esta carpeta. Después se puede retirar V1 con su propio restaurador.
