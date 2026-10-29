# Aurelia — planos para modelo 3D, revisión 01

Actualización posterior del 14/10/2026: Kevin autorizó integrarla en L2. La conversión e instalación estacionada están documentadas en `../aurelia-integration/README.md`, con respaldos y accesos propios `.muelle aurelia`. El resto de este documento describe la entrega original de modelado; las limitaciones de arte y de transporte móvil siguen vigentes.

Diseño realizado el 14/10/2026 a pedido de Kevin, inspirado en la imagen de una aeronave resort blanca con piscina abierta y arco longitudinal. Nombre provisional. Se prepara primero el diseño 3D; Kevin indicará cuándo adaptarlo a L2.

## Abrir y revisar

- `PLANOS-AURELIA.html`: dossier local con siete renders y cuatro láminas vectoriales, imprimibles en A3 horizontal desde el navegador. No requiere conexión.
- `Aurelia-v1.blend`: modelo editable con piezas, materiales, interiores, cámaras y un corte real de la malla. Abrir con el Blender portátil de este proyecto mediante `ABRIR-MODELO.cmd`.
- `Aurelia-v1.glb`: intercambio del modelo completo, sin cámaras ni iluminación de estudio.
- `A01-planta-general.svg`: terraza, mobiliario, piscina, ejes, estaciones y dimensiones.
- `A02-perfiles.svg`: perfil, frente y tabla de semiejes para reconstruir el casco.
- `A03-interiores.svg`: dos cubiertas inferiores con camarotes modulares.
- `A04-cortes-detalles.svg`: sección, cabañas y parámetros de piezas principales.
- `design-audit.json`: conteos, medidas y posiciones de camarotes.
- `build_resort.py` y `make_plans.py`: fuentes reproducibles. Ejecutar primero con Blender y después Python, respectivamente.

## Escala y forma

Unidades en metros. Origen en el centro longitudinal del casco, Z=0 en su punto inferior. Proa hacia -X, popa hacia +X, babor +Y. Casco nominal de 120 × 52 m; envolvente nominal de 129 m de longitud, 76 m de ancho y 40 m de alto, antes de pequeños espesores y accesorios. No son medidas deducidas de la foto.

Terraza oval 102 × 38 m a Z=18. Borda a Z=23. Arco longitudinal con ápice a Z=34. Piscina 38 × 12 m, fondo Z=16,5 y agua Z=17,65. Diez cabañas de 6 × 4 m con 20 tumbonas; ocho tumbonas adicionales al aire libre. Salón de popa, barra, jardineras, escalas de piscina y dos referencias humanas de 1,8 m. Dos motores laterales y uno de popa con conductos abiertos y álabes.

Las cubiertas interiores A y B están a Z=10,5 y 5,5, con 20 camarotes en total, camas y armarios. Tabiques de 3,3 m y puertas de 1,2 m. Puente de navegación a Z=14,2 en proa. Dos escaleras entre A y terraza, con huecos de suelo; otra escalera entre B y A, con huecos en suelo y acabado de pasillo. Son elementos visuales de diseño, sin validación de circulación de personajes. La conexión específica del puente con las demás cubiertas aún no está diseñada.

## Qué está reconstruido y qué está propuesto

La referencia aporta la dirección visual: volumen ovalado, terraza abierta, piscina, ventanas oscuras, color blanco, arco y aletas. La malla se creó desde cero. Las dimensiones, la vista posterior, los detalles de motores, las piezas modulares y todos los interiores son decisiones de esta versión, no datos del objeto de la imagen. Los SVG son dibujos de diseño con las dimensiones principales de la malla; para siluetas exactas se entregan renders ortográficos desde esa malla. Los detalles de perfil de las láminas se simplifican para lectura.

## Alcance del detalle y pendientes

Este paquete es una primera versión de modelado revisable, no un asset final ni un plano de fabricación. Está detallada la composición exterior y existe una distribución interior base. Falta revisar con Kevin la fidelidad a la referencia, la escala, el aspecto del arco y las aletas y el uso de los interiores. Baños, cocinas, equipos técnicos, climatización, instalaciones y la conexión al puente no están desarrollados. El acceso de embarque depende de la decisión posterior sobre el puerto y el uso de la nave.

Los cristales son materiales opacos azules sobre el casco, sin huecos de ventana reales ni refracción. El agua es una superficie visual. Los acabados son materiales de Blender, sin texturas horneadas ni UV final. Las turbinas no están animadas. La geometría conserva objetos editables y usa modificadores; el corte de revisión duplica la malla evaluada y permanece oculto en la vista normal. Activar `09_Corte_solo_revision` y ocultar colecciones 01–07 para inspeccionarlo.

Antes de L2: preparar UV y texturas, revisar presupuesto geométrico, simplificar o generar LOD, decidir superficies transitables, colisión, escala y materiales compatibles. El transporte de pasajeros, rutas, NPCs y movimiento son una etapa posterior. No se modificaron el cliente, el servidor ni la aeronave existente.

## Comprobaciones

Generación Blender y exportación GLB completadas; siete renders producidos desde la misma escena; corte geométrico central generado; vistas revisadas visualmente; planos XML verificados. Conteos finales en `design-audit.json`. Estas verificaciones no constituyen pruebas de importación ni de navegación en L2.
