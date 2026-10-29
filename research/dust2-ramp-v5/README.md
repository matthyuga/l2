# Dust2 V5: prueba local de apoyo inclinado — 14/10/2026

Kevin probó V4 y confirmó que **sigue sin poder subir**: estaba arriba, bajó y no pudo regresar. Nueva captura muestra el mismo problema. No considerar las442 pruebas NSWE del servidor como confirmación del cliente.

Se capturó posición viva: Hellkevin139360,56464,8056 heading54217, radio9.0 y collisionHeight23.0. El tramo concreto tiene suelo visible8000 en Y>=56496,8016 entre56464..56496,8032 en Y<=56464; ancho del peldaño intermedio X139232..139440. La geodata V4 permite los pasos y no hay paredes nativas V4 en el entorno inmediato. El fallo persistente requiere probar una solución en la colisión del cliente; no se presenta una causa interna del motor como demostrada.

## Prueba instalada

Un solo actor nativo **HGDust2V5RampExample**, con deco01.Box02 original, inclinado26.565°. Superficie superior entre Y56528/Z8000 y Y56464/Z8032; ancho208u, espesor normal4u y solapes mínimos. Rotation(0,0,4836), ajustado a la matriz nativa. Oculto: la escalera visual no cambia. El plano pasa por encima del perfil dentado, por lo que durante el ascenso puede haber separación visual entre el pie y algún peldaño; el objetivo inicial es verificar que la física del cliente admita una subida continua. No se generalizó a todo el mapa.

Se ajustaron26 alturas de geodata dentro de ese rectángulo (dos filas de13 celdas, +8u), conservando NSWE y las demás capas. Se agregó **`.dust2 escalera`**, llegada139336,56560 (efectivaZ8045), mirando al norte hacia los peldaños. El regreso usa `.dust2 salir`. Comando en runtime/source/cloud, recompilado; handler vivo actualizado por redefineClasses sin alterar esquema y región recargada con GeoEngine.reloadRegion(24,19).

-51 consultas geométricas sobre la malla nativa transformada verificaron una pendiente continua y alturas de extremo, tolerancia.004u.
-16.002 payloads existentes preservados byte por byte, salvo myLevel para agregar una referencia. Solo se añadió un actor.
-Ver121, CRC y roundtrip íntegros.
-server-probe.txt PASS364 consultas de movimiento bidireccional por la rampa, comando real con Player transitorio y regreso. No se creó personaje persistente ni se movió al usuario durante la prueba.
-Kevin cerró L2 explícitamente antes de instalar. GameServer9536 siguió activo. Backup **E:/l2-local/backups/dust2-ramp-v5-20261014-161229**,5 archivos (mapa, geodata y3 handlers). Manifiestos principal/V2/V3/V4 yV5 sincronizados. Restaure mapa+geo+handler juntos si retira esta prueba; no ejecutar instaladores históricos sobre el estado actual.

## Pendiente obligatorio para generalizar

Pregunta async enviada: abrir L2, usar `.dust2 escalera`, subir, bajar y volver a subir. Esperar confirmación en cliente antes de replicar a las demás escaleras. Si falla también esta pendiente, no continuar abriendo NSWE ni cambiando escala a ciegas: revisar parámetros de colisión del actor/mesh y la ejecución real del cliente. Critical al cerrar sigue pendiente y separado; no se aplicaron cambios a DLLs/audio/shaders/cachés. Galería y bots bajo demanda sin cambios.
