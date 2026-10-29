# Dust2 V5 local: V4 NO resolvió subir escalones

Kevin probó V4: estaba arriba, bajó y no pudo subir otra vez. Nueva captura. Coordenadas vivas139360,56464,8056 heading54217, radio9/alto23. Escalera concreta8000->8016->8032 en Y56496/56464, anchoX139232..139440. NSWE ya permite subida; no paredes nativas cercanas. No declarar resuelta la física del cliente por las442 pruebas de servidor.

Instalada prueba LOCAL V5 en E:/l2-local/research/dust2-ramp-v5: actor nativo deco01.Box02 HGDust2V5RampExample con pendiente26.565°, oculto sobre2peldaños, Y56528/Z8000 -> Y56464/Z8032. Visual no cambia; el plano puede separar algo los pies de peldaños durante subida.26 alturas geo(+8u) ajustadas dentro del rectángulo, NSWE intacto. **`.dust2 escalera`** lleva al pie139336,56560,8045 mirando hacia subida; `.dust2 salir` regresa. Handler runtime/source/cloud sincronizado y actualizado en vivo por redefine, geo reloadRegion. GS9536 no reinició. Kevin cerró L2 expresamente antes de reemplazar mapa.

51 consultas geométricas nativas y364 movimientos bidireccionales +comando real +regreso PASS (no certifica física cliente).16.002payloads anteriores intactos salvo myLevel, se añadió1actor. BackupE:/l2-local/backups/dust2-ramp-v5-20261014-161229 (mapa+geo+3handlers). Manifiestos principal/V2/V3/V4/V5 actualizados. No usar instaladores viejos. Sin commit/push.

PENDIENTE: async pide usar `.dust2 escalera`, subir/bajar/repetir. **Esperar validación cliente antes de generalizar rampas al mapa**. Si también falla, revisar colisión del actor/mesh/cliente, no más aperturas NSWE o escala sin diagnóstico. Critical al cerrar separado y aún no resuelto. Bots/galería sin cambios.
