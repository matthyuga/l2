# Revision de referencias RPG - 2026-10-24

Origen: `C:\Users\KEVIN\Desktop\diseño paneles rpg`.

## Cobertura

1490 archivos: 1484 imagenes abiertas sin errores, 3 PSD, 2 PPTX y 1 EXE. 1476 imagenes unicas por SHA-256; 8 copias duplicadas exactas. Se revisaron visualmente las 16 laminas de miniaturas y se amplio una seleccion. No se inspeccionaron individualmente todas las imagenes a resolucion completa; PSD/PPTX solo inventariados, EXE no ejecutado.

Inventario con rutas, dimensiones, canal alfa y hashes: [inventory.json](inventory.json). [Seleccion visual](seleccion-dialogos.jpg).

## Dialogo de Amber

Estado recuperado de research/npc-story-dialogue-v1: demo nativa ya instalada y validacion visual parcial del usuario; texto fijo, retrato neutral y ramas de demostracion. La presente revision no modifica cliente ni servidor y no sustituye decisiones de diseno previas.

Propuesta: usar 0283 como referencia de distribucion, 1209 como referencia de marco sencillo y 1249 solo para acentos dorados. Conservar retrato lateral, texto editable separado de la textura, nombre diferenciado, dos elecciones legibles y cierre visible. Evaluar en 1024x640 y 1280x720. Los estilos de pergamino, neon y tarjetas de combate son alternativas, no una sola mezcla.

## Seleccion con rutas exactas

### 0283 - Dialogo: personaje lateral y caja independiente

Archivo: [649853615_122177833178941842_8613034589114984667_n.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/649853615_122177833178941842_8613034589114984667_n.jpg)

2048 x 1340; modo RGB; canal alfa: False.

Composicion mas directa para Amber. Placa de nombre sobre el texto; retrato fuera del area de lectura.

### 0950 - Dialogo: retrato y pergamino

Archivo: [Nueva carpeta (2)\Dk1CUA8UUAAj61v.jfif](C:/Users/KEVIN/Desktop/diseño paneles rpg/Nueva carpeta (2)/Dk1CUA8UUAAj61v.jfif)

482 x 737; modo RGB; canal alfa: False.

Referencia para lectura narrativa; evitar trasladar texto incrustado y una caja demasiado pequena.

### 0772 - Kit de paneles de pergamino

Archivo: [interfaces\0a6939b70c61c7fb57fed6fd824e18dd.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/interfaces/0a6939b70c61c7fb57fed6fd824e18dd.jpg)

1200 x 1390; modo RGB; canal alfa: False.

Referencia de paneles, separadores, listas y botones; reconstruir piezas a resolucion de uso.

### 0782 - Kit RPG de pergaminos e inventario

Archivo: [interfaces\302583fffda2da9462002c155feec881.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/interfaces/302583fffda2da9462002c155feec881.jpg)

563 x 1061; modo RGB; canal alfa: False.

Util para contratos, misiones, diario y recompensas. Imagen pequena: no tratar como atlas final.

### 0786 - Placas magicas ornamentales

Archivo: [interfaces\6ceb8845bafafef50b6f90e02829f1d6.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/interfaces/6ceb8845bafafef50b6f90e02829f1d6.jpg)

736 x 1222; modo RGB; canal alfa: False.

Nombres, rarezas o elecciones especiales; ornamentacion mas luminosa que el dialogo base.

### 0788 - Paneles neon

Archivo: [interfaces\7e003a02f88e9e1e5b6b8ecee78ef764.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/interfaces/7e003a02f88e9e1e5b6b8ecee78ef764.jpg)

510 x 907; modo RGB; canal alfa: False.

Reservar para interfaz tecnologica o modos especiales, sin mezclar por defecto con pergamino.

### 1209 - Marco horizontal sobrio

Archivo: [pinteres3\570ef226bf3427a91c73e30e455fd468.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/pinteres3/570ef226bf3427a91c73e30e455fd468.jpg)

736 x 357; modo RGB; canal alfa: False.

Buen candidato visual para caja de dialogo; preservar esquinas y ampliar zona central.

### 1249 - Separadores dorados

Archivo: [pinteres3\bb281f7667e79700c930196f745ae374.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/pinteres3/bb281f7667e79700c930196f745ae374.jpg)

735 x 736; modo RGB; canal alfa: False.

Utiles para titulos o nombre del interlocutor; usar ornamentacion fuera del texto.

### 1265 - Retrato circular y placa gotica

Archivo: [pinteres3\f2833fc8d1f78678cc3a3cc6a2063ab6.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/pinteres3/f2833fc8d1f78678cc3a3cc6a2063ab6.jpg)

599 x 417; modo RGB; canal alfa: False.

Adecuado para cabecera compacta o NPC de faccion; demasiado detalle para botones pequenos.

### 1288 - Marco angular dorado

Archivo: [pinteres4\1d5089361e4e9be8ee98975478249903.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/pinteres4/1d5089361e4e9be8ee98975478249903.jpg)

1200 x 675; modo RGB; canal alfa: False.

Referencia de bordes discretos y jerarquia; composicion completa con fondo y texto ya integrados.

### 0271 - Lista de conversaciones con retratos

Archivo: [649270007_2449228142178058_8476435292193096984_n.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/649270007_2449228142178058_8476435292193096984_n.jpg)

960 x 556; modo RGB; canal alfa: False.

Referencia para historial de conversaciones y entradas por personaje.

### 0709 - Carta de pergamino

Archivo: [gui\671279873_122147801960413034_1853370903765580591_n.jpg](C:/Users/KEVIN/Desktop/diseño paneles rpg/gui/671279873_122147801960413034_1853370903765580591_n.jpg)

1920 x 1080; modo RGB; canal alfa: False.

Referencia para mensajes, contratos y misiones escritas.

## Otras familias utiles

- interfaces, pinteres3 y pinteres4: marcos, placas, botones, emblemas y jerarquias de menu. Mezcla de hojas de componentes y capturas de referencia.
- barras y corazon: secuencias de estados de vida/energia; pueden inspirar un indicador por relleno o estados discretos.
- raiz y Nueva carpeta (2)-(5): menus de personajes, inventario, combate, resultados y dialogos dispersos.
- gui: predominan piezas promocionales y listas; algunas cartas y pergaminos de interes narrativo.
- panel de puntos stat: paneles de atributos y categorias, utiles para una pantalla distinta del dialogo.
- mqap: escenarios/mapas; menor prioridad para este trabajo.

## Adaptacion al cliente

Muchas referencias elegidas son JPG/JFIF, sin transparencia y con fondo/texto incrustado; no asumir capas, estados hover/pulsado ni licencia de paquete por la mera imagen. Para un panel final: separar fondo, marco, placa y botones; mantener esquinas con nueve regiones, preparar estados del boton, texto nativo y exportar texturas compatibles con el flujo ya probado de la demo. No estirar una captura completa para convertirla en ventana.

## Editables inventariados

- barras/barras.psd
- dados del juego/bandados.psd
- dados del juego/d1.psd
- ark.pptx
- Nueva carpeta/shogun2.pptx

## Pendientes conservados

Conexion fisica Rune-Pagan y acceso cercano a Ketra quedan pendientes por indicacion del usuario. No se realizaron cambios para esos accesos.
