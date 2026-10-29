# Estructuras aéreas de Gracia — 12/10/2026

## Estado más reciente: escenarios y Superion

Ya disponibles: muelle de Gludio (8 actores), arquitectura de Keucereus (224), zona aérea 13_25 (134), Superion ensamblado (643 actores de Helios) y 164 componentes de Superion (106 exteriores, 58 interiores). Todos tienen miniaturas y vistas 3D; las piezas Superion también abren en UModel. Catálogo: 841 registros y 840 miniaturas. Buscar «Estructuras aéreas» reúne las 198 vistas de este trabajo, incluidas las preparadas anteriormente.

Detalle y enlaces directos en [Escenarios y Superion](ESCENARIOS-Y-SUPERION.md). Los apartados siguientes son el historial de preparación; sus cantidades anteriores y «Superion no descargado» han sido superados. Chaos' Air Fortress sigue pendiente.

## Selección adicional de estructuras

Diez vistas añadidas después del montaje: Glacia_destruction_Tower, Glacia_destruction_DeadTower, Glacia_destruction_FlyMini, immortal_landmark_top, immortal_landmark_head, matrix_out, G_Field_kserthgateway, G_Field_Astone01, E_F_tower_01 y E_F_bridge_01. Hoja visual otras-estructuras.jpg. No son diez mapas completos: son piezas de escenarios; Infinity top/head tienen shaders no soportados TexCoordSource/VertexColor y materiales parciales. Usos posibles (propuestas, no implementados): puerta de expedición, torre de asedio, arena aérea, expedición oscura. Total actualizado: 30 vistas de Gracia, 673 registros y 672 miniaturas.

## Corrección posterior del montaje

El usuario detectó piezas aparentemente ausentes. Causa comprobada: 17 materiales de las piezas estáticas tenían alpha MASK con corte .35, aunque sus shaders UE2 indicaban Opacity=None, OB_Normal y AlphaRef=0; la transparencia del visor borraba superficies de casco, tubos y soportes. Se corrigieron solo esos materiales y quedó auditoría en material-fix-audit.json. El efecto de algunos shaders de reflexión sigue aproximado.

Se recuperaron cuatro archivos adicionales (18 en total): bereth_T.utx, LineageVehicles.ukx, LineageVehicle.u y VehiclePartsGrp.dat. El DAT se decodificó con el codec local, y su receta real consta en vehicle-parts-decoded.json: casco estático body002, velamen animado body004, cola animada body003 y mando. Cola offset X=-498; mando X=363, Z=102. La exportación skeletal requiere girar 180° alrededor de Z para coincidir con las variantes estáticas (RotOrigin Yaw=32768); después se aplican offsets cm→m. El nuevo montaje hornea pose base y reúne la geometría en una malla. No añade el cañón: no aparece en la receta de este SmallAirShip. Ya no se usa el montaje inicial de cinco piezas sin offsets. Sigue pendiente contraste visual ingame, efectos y movimiento.

Hay 20 vistas de Gracia (piezas estáticas/animadas y montaje), 663 registros y 662 miniaturas en total. La entrada ensamblada conserva su enlace. El texto histórico que sigue describe la primera preparación.

Montaje añadido: «Gracia · Nave aérea ensamblada», cinco piezas agrupadas en un objeto conservando coordenadas fuente. Disponible en http://127.0.0.1:32280/?model=airship_assembled_gracia&view=3d . Archivo editable GraciaAirship-preview.blend y glTF en ../model-catalog/exports/assembled-gracia/airship.gltf. Es un montaje para inspección, sin efectos y pendiente de contrastar con el cliente Gracia. No se fusionaron muelles y base con la nave. Ahora hay 16 vistas de Gracia (15 piezas y este montaje), 659 registros y 658 miniaturas en total. El montaje se ve en WebGL; sus piezas originales siguen disponibles en UModel.

Descargados 14 paquetes de mallas/texturas desde el manifest público del actualizador de L2 Pride (Gracia Final): https://l2pride.us/downloads . Cada archivo se descomprimió y comprobó contra tamaño y SHA-256 del manifest. Lista y hashes: download-manifest.json. Sin ejecutar su launcher, instalar su cliente ni modificar E:/l2 o el servidor.

En nuestra galería hay 15 vistas nuevas (buscar «Gracia»), incluyendo casco, velas, mástil, mecanismos, plataformas, muelles, puente y rocas. Acceso: http://127.0.0.1:32280/?q=Gracia . Casco en 3D: http://127.0.0.1:32280/?model=airship_fly_boat_body002&view=3d . Los botones del visor nativo abren estos paquetes desde gracia-assets; sus nombres coinciden con algunos del cliente Interlude, pero permanecen aislados.

Piezas especialmente útiles para comparar las capturas antiguas:
- Glacia_kserth_S.G_kserth_port_gard: plataforma alargada semejante a casco, con barandillas y grúa; posible parte del muelle.
- Glacia_kserth_S.G_kserth_start_walk1FF: gran plataforma con roca y adornos.
- Glacia_kserth_S.G_kserth_port_gr_link: pasarela.
- L2_Ship_L01_S.fly_boat_body002: casco de nave aérea. body004 contiene velas; body001 mástil/ornamento; body003 mecanismos.
- G_kserth_port_ship_obj resultó ser postes/cables del muelle, no una nave completa.

La coincidencia exacta de las capturas todavía no está confirmada. Algunos materiales complejos se ven incompletos (efectos, reflejos o shaders); la ficha señala materiales sin textura. Los assets originales Gracia no son una adaptación comprobada a Interlude. UModel reconoce y exporta las piezas; esto no prueba funcionamiento de colisiones, mapas ni transporte dentro del juego. Superion no descargado.

La fuente alternativa lineage2.org.uk permite acceso parcial al ZIP, pero su índice no incluía los paquetes Glacia buscados. Se descargó únicamente MAPS/14_25.unr (5,2 MB) y el índice para investigar; el archivo completo no se descargó. remote_zip.py documenta este método.

Scripts: download_assets.py recupera/verifica recursos; prepare_gallery.py añade vistas conservando un respaldo inicial; render_previews.py crea miniaturas con Blender local; verify_previews.py comprueba búsqueda y canvas WebGL con Chrome aislado.
