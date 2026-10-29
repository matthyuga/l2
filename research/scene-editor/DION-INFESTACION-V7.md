# Dion V7 · raíces y expansión de corrupción

26/10/2026. Kevin pidió raíces para las variaciones de espinas y suelo de color similar para mostrar expansión de infestación. Nueva variante separada: http://127.0.0.1:32290/?project=dion-hecatombe-v7.json; ABRIR-DION-HECATOMBE-V7.cmd. Selector Dion · Hecatombe V7 · Infestación. Abre en cámara8 (espina grande con raíces),7 muestra calle,9/10 combinadas. V6 conservado.

108ramas nuevas en seis puntos:36raíces principales y72bifurcaciones. Raíces gruesas nacen contra los collares de las espinas y se afinan hacia la tierra; apoyadas mediante heightfield nativo. Acompañan las seis colocacionesV6; las ocho coloniasV5 conservan sus raíces previas. Geometría estática, sin simulación de crecimiento ni partículas nuevas.

Suelo: material V7 suma áreas granate/púrpura oscuro en torno a14centros (seis variantes y ocho colonias), distorsión por ruido, borde difuso/necrosado, manchas/vetas y grano de la textura de tierra existente. La fila de la calle tiene áreas que se conectan. Sin emisión ni franjas planas. Se calcula sobre el terreno real, no con planos superpuestos.

build-dion-roots-v7.py reutiliza funciones geométricas mediante AST sin ejecutar el constructorV5. Semilla271031; exportación model-catalog/exports/dion-infestation-v7/roots.glb y root-audit.json. infested-terrain.js envuelve applyPlagueTerrainV4 solo para asset custom_dion_infestation_v7_core, conservando variantes previas. app.js reconoce nuevo terreno y raíces; estas reutilizan material orgánicoV5. Los sombreadores son del Taller y no se hornean para otros visores.

register-dion-infestation-v7.py crea projects/dion-hecatombe-v7.json y registra recursos; protección contra sobrescribir proyectos existentes. El nuevo terreno referencia core.gltfV4 (sin cambiarlo); rootsGLB con108ramas independientes, registradas en root-audit.66objetos en proyecto (un nuevo conjunto de raíces). Sus componentes se pueden editar desde árbol. Los centros de expansión del shader están fijados a esta composición; mover una espina manualmente no mueve automáticamente la mancha ni sus raíces, que son un recurso independiente. Esto es una composición estática, no un sistema dinámico de infestación.

Verificación verify-dion-v7.cjs:66objetos, carga/shaders sin errores, cámaras7..10 y guardado/reapertura. dion-v7-verification.json; capturas preview-dion-v7-calle/gigante/entrelazadas/ramificada.png revisadas. Raíces siguen suelo pero no calculan colisiones con cada escombro: intersecciones menores posibles. No se modificó clienteUNR/juego.
