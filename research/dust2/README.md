> Actualización 14/10/2026: incorporado a L2 como exploración. Ver ../dust2-integration/README.md; los resultados de esta revisión inicial se conservan debajo.

# Dust2 CS 1.6 — revisión y prueba de conversión, 14/10/2026

## Resultado

**Conversión a Blender realizada; conversión nativa para L2 comprobada como recurso. No instalado en el juego ni servidor.** No se modificaron CS, Koikatsu ni L2 durante esta revisión.

Kevin dejó pendiente la aeronave de diseño propio y pidió revisar Dust2 de CS1.6. También contó que un compañero lo había llevado a Chara Studio. Se encontraron las dos fuentes locales:

- CS1.6: `D:/juegos/cs1.6/cstrike/maps/de_dust2.bsp`, BSP30, 2057288 bytes. SHA y entidades en `bsp-audit.json`. Se trabaja sobre una copia en source/. «Original» en nombres de trabajo significa archivo procedente de la instalación local, no certificación de versión oficial inalterada.
- Koikatsu: `E:/koi10/mods/deadsharkKK_de_dust2_1.6_v1.0.zipmod`, además duplicado en mods/MyMods. Manifest autor deadshark, de_dust2 1.6 v1.0. Bundle `abdata/studio/deadshark/dedust2.unity3d`: una malla, 13717 vértices, 34 submeshes/materiales y 34 imágenes. Se leyó con UnityPy1.25.0. OBJ bruto `dust2-unity.obj` es para inspección: no incluye transformaciones de jerarquía ni asignación de materiales; no tratarlo como exportación final.

## Blender

- Usado [GoldImporter](https://github.com/Stalker2106/GoldImporter), fuente fijada al commit 40f773e846e53c103a57cb205e1721f3a46d42b5, sin instalar el addon globalmente. Código de referencia en reference/; importación mediante función Python en Blender5.0.1 portátil ya disponible.
- Se recuperaron las **44 texturas referenciadas**: quince del propio BSP y las demás de WAD3 en la instalación CS. Cero faltantes. `texture-audit.json` conserva procedencia de cada imagen. Están disponibles también las seis imágenes Des*.tga del cielo de CS, aún no integradas a la vista de prueba.
- Se omitieron superficies de herramientas invisibles (sky, clip, aaatrigger, etc.); volúmenes de bombsite/buyzone se ocultan para la vista. Se conservan entidades como propiedades/empties, incluidas posiciones de veinte jugadores por equipo.
- Geometría visible: **39 meshes, 9932 triángulos**. La malla de Chara Studio también exporta 9932 triángulos: coincide el conteo, no constituye comparación exhaustiva de topología/texturas.
- Archivo editable: `Dust2-CS16-original.blend`, imágenes empaquetadas. Intercambio: `Dust2-CS16.obj` y .mtl. El MTL exportado tiene rutas genéricas C:/ para imágenes; usar textures/ para resolverlas al abrir OBJ fuera del BLEND. El BLEND sí tiene imágenes empaquetadas.
- Vistas inspeccionadas: `dust2-aerial.png` y vista superior `dust2-top.png`. La primera muestra muros, cajas, túneles y la distribución reconocible. El cielo y luces de la vista son una configuración de inspección; no se importó iluminación precalculada/lightmaps original.

## Prueba de recurso nativo L2

`probe_l2.py` convierte el OBJ por materiales a LWO2, adapta tamaños de imágenes a potencias de dos, y compila `l2-probe/compiler/HGDust2Probe.u` con UCC instalado. El paquete queda en investigación, no en E:/l2.

- **37 meshes y 34 texturas** usadas por superficies visibles.
- Compila con salida 0; resumen UCC 0 errores y 0 advertencias. En el log aparecen avisos de falta de xDxTex.exe; el importador conserva texturas sin compresión, que UModel sí carga.
- Se vuelve a cargar/exportar el paquete y se comprueba que conserva 9932 triángulos.
- UModel en modo L2 lee **71 recursos** (37 meshes +34 imágenes) sin error. Evidencia `l2-probe/proof.json`, logs compile/roundtrip y native-load/.
- Primera prueba mostró un diálogo porque una imagen medía96x32; se detuvo ese proceso UCC de prueba y se adaptaron todas las imágenes necesarias a potencias de dos sobre copias. La siguiente prueba terminó sin diálogo. Texturas originales preservadas.

## Para volverlo una arena jugable

1. Elegir escala con personaje y cámara L2; la escala .03125 usada para importar GoldSrc a Blender es una convención de trabajo, no una decisión final de tamaño L2.
2. Seleccionar parcela o instancia separada, con límites y entradas/salidas apropiados. Dividir por materiales/sectores para render y colisión.
3. Reconstruir geodata de pisos, escaleras/rampas, cajas y túneles con varias alturas. Las superficies clip de CS y los brush func_illusionary tienen significado de colisión propio que no se debe sustituir sin revisar por «todo sólido».
4. Probar desplazamiento, línea de visión de skills, cámara en pasillos y techos. Revisar accesos que dependan de saltar/agacharse en CS y adaptar si es necesario.
5. Configurar spawns/equipos/reglas de evento. La presencia de cuarenta puntos de inicio no define por sí sola la capacidad final ni importa la lógica de CS.

La extracción visual es viable y el recurso nativo compila. No hay prueba de navegación, línea de visión, colisión o render dentro del cliente L2; esos controles requieren la fase de integración.
