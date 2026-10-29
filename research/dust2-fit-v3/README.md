# Dust2 ajuste V3 — 14/10/2026

Kevin probó V2 y reportó puertas infranqueables y pies hundidos. Capturas: personaje en la abertura de puertas y sobre escalones. Además volvió a aparecer critical **al cerrar** a las 15:29:37: FMallocWindows::Free <- DeleteObject(61586) <- DeleteGarbage(SSQ_ent08) <- UObject::PurgeGarbage <- UObject::StaticExit <- appPreExit. No se confirmó la causa del critical ni se declara corregido.

V2 se redujo en exceso: se había usado la collisionHeight del servidor como referencia de altura visible del personaje. Esa comparación no certifica las dimensiones del modelo del cliente. V3 usa escala GoldSrc 1.0, intermedia entre original 1.5 y V2 0.625. Conserva la corrección del espejo en Y y las UV derechas de V2. Los 37 actores visuales usan DrawScale .32 y DrawScale3D (1,-1,1). HGDust2Arena.usx queda intacto en esta revisión.

El soporte V2 se calculaba con alturas de geodata cuantizadas a 8u y después restaba 43.35; eso dejaba los pisos invisibles por debajo del suelo visible. V3 registra alturas de la geometría antes de cuantizar y separa rectángulos por altura visual, alineando los soportes a ese dato. La superficie se deriva de _column truncada a unidades enteras; con esta escala las superficies planas tienen coordenadas enteras. No se afirma ajuste perfecto en todas las pendientes.

- 38.955 celdas añadidas; 30.372 capas alcanzables; 40 puntos CT/T conectados.
- 1.793 pisos nativos y 1.331 paredes nativas, con deco01.Box02 original; soportes de 4u de espesor.
- 116.945 pasos dirigidos libres sin paredes de otro nivel en la línea central.
- Comprobación adicional con cuerpo de radio 10.5 y altura 70 contra las paredes nativas: 26.505 centros conectados y los 40 inicios CT/T conectados. Es una comprobación conservadora de geometría, no ejecuta física del cliente ni certifica todas las razas o todas las puertas.
- Se verificaron 8.242 payloads ajenos a esta revisión sin alteración, incluido muelle/aeronave. Colisiones V2 se desactivan y retiran de myLevel; sus exports permanecen históricos.
- Geodata reconstruida sobre la base anterior a Dust2 ya usada por V2, con guardas de hash de la instalación actual. No se descartan cambios concurrentes.
- CT [141448,54536,7936] y T [140168,57704,8192] son referencias de llegada (altura de geodata +24); el handler, paz/respawn y bounds se actualizan juntos en runtime/source/cloud.
- Cifrado Ver121, CRC y roundtrip de mapa verificados antes de instalar. Backup E:/l2-local/backups/dust2-fit-v3-20261014-154214; installation.json registra 8 archivos. Manifiestos principales y V2 actualizados para conservar las restauraciones previas. No ejecutar instaladores históricos ni reejecutar prepare.py sobre V3.

La primera prueba del GameServer V3 detectó una subida bloqueada en [141384,55336,8072] -> [141384,55320,8080]. El diagnóstico descartó puertas y vallas: la celda destino tenía dos capas a 8u y el servidor elegía la inferior al moverse. El umbral entero de LAYER_MERGE dejaba sin fusionar la igualdad exacta a 8u. El generador aislado ahora usa 8.1 para fusionar diferencias enteras <=8 sin ese hueco de igualdad. Se regeneraron geodata, pisos y paredes; apply_step_fix.py respaldó la versión intermedia, instaló 2 archivos y sincronizó manifiestos. No cambió globalmente geolib.

Resultado final server-smoke.txt: PASS con 40 inicios, 192 subidas de 3.810 conexiones ascendentes, pasos abiertos/cerrados, capas, zonas, comandos CT/T, regreso y conservación de muelle/nave/Coliseo. GameServer final9536, LoginServer23432 conservado. Llegadas efectivas observadas CT141448,54536,7917 y T140168,57704,8173. Probe final de galería también pasó después de este último reinicio; estado final oculto.

Prueba del cliente pendiente: usar `.dust2` para ir a las nuevas coordenadas antes de recorrer puertas y escaleras. No considerar el PASS del servidor como validación de la física del cliente. Si el critical persiste, registrar si ocurre también saliendo desde Giran sin visitar Dust2; el nombre del objeto mostrado durante PurgeGarbage no demuestra por sí solo qué recurso causó el fallo. No se aplicaron cambios especulativos a DLLs, shaders, audio o cachés para disimularlo.
