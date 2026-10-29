# Vigilia del Dragón — primera maqueta 3D

Actualización posterior del 14/10/2026: Kevin autorizó la integración. Ya está instalada como nave estacionada con accesos `.muelle dragon` y `.muelle dragon proa`; conversión, respaldo y pruebas PASS del servidor documentados en `../vigilia-integration/README.md`. La revisión visual/física en el cliente sigue pendiente. Los apartados siguientes describen el estado original de la maqueta antes de esa instalación.

Kevin pidió volver a la aeronave y rediseñarla o crear una similar más épica, usando como referencia la imagen adjunta de un barco aéreo oscuro con globo rojo, proa de dragón y faroles. Se creó **una variante nueva desde cero con geometría procedural en Blender**, inspirada en esos rasgos. No es una extracción del barco de la imagen ni una copia de su geometría. Se inspeccionó la nave anterior como contexto, pero no se incorporó su mesh al modelo nuevo.

## Entrega

- `Vigilia-del-Dragon-v1.blend`: modelo editable en Blender5.0.1, con cámaras, materiales y luces.
- `vista-principal.png`: perspectiva general.
- `vista-cubierta.png`: acercamiento a la cubierta y proa.
- `vista-lateral.png`: perfil de la aeronave.
- `ABRIR-VIGILIA-DEL-DRAGON.cmd`: abre la maqueta con el Blender5 portátil del proyecto. No se ejecutó automáticamente.
- `build_epic.py`: fuente reproducible de la geometría y las vistas.
- `design-audit.json`: conteos y estado de integración.

Diseño: casco oscuro de listones con cuadernas de bronce; gran globo carmesí panelado con cinchas y sello de dragón; proa con cabeza de dragón, cuernos y ojos de cristal; cabina de capitán con ventanas cálidas y timón elevado; bancos laterales; cubierta central despejada; jarcias, faroles, aletas y dos motores con hélices. Nombre provisional; no representa una decisión de lore definitiva.

El modelo tiene491 objetos/piezas y40.699 triángulos evaluados con sus modificadores en esta versión. Colección `01_AERONAVE_EXPORT` separa geometría de `02_ESTUDIO_NO_EXPORTAR`(cámara/luces). Se conservaron piezas y materiales editables en vez de fusionar todo antes de revisar el diseño.

## Estado y próximos pasos técnicos

**Es una maqueta 3D renderizada, no una aeronave nueva instalada en L2.** La aeronave actual, muelle, Dust2, geodata y servidor no se modificaron durante este diseño.

Para Interlude falta revisar escala con personaje/cámara, holguras, acceso de escaleras, pasarelas y embarque; decidir las superficies transitables reales; hornear materiales de madera/lona a texturas; preparar mallas de exportación/UV y materiales de doble cara para paños; reducir detalles si el rendimiento lo requiere; compilar recursos y crear colisión/geodata nativa. Las luces/emisiones del render no se transfieren automáticamente como luces dinámicas de L2.

Las escaleras, cubierta y barandas forman parte del diseño visual y no tienen aún validación de navegación. El timón es decorativo y las hélices no tienen animación. No hay NPCs ni capacidad máxima de pasajeros definida. El transporte móvil con pasajeros, rutas aéreas, embarque/desembarque y reconexión sigue siendo un sistema separado pendiente; mover una malla no transporta automáticamente la colisión/geodata ni a sus ocupantes.

La referencia tiene una atmósfera pictórica y materiales envejecidos; esta primera maqueta usa una presentación estilizada de estudio. El objetivo de las vistas es revisar silueta, distribución, color y detalles antes del trabajo de integración. Sin commit ni push.
