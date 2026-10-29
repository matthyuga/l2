# L2: observación de carga y simulación semanal de energía

Proyecto real: E:\l2-local. Kevin pidió analizar la PC, encender L2 y simular una semana de consumo. 12/10/2026.

El servidor ya funcionaba; Start-L2Local.ps1 confirmó listo sin reinicios. Quedó local con DB3307/login2106/enlace19014/game7777. No se abrieron puertos públicos, no se aplicó parche pendiente ni se alteró el plan Economizador.

Informe: E:\l2-local\reports\consumo-semanal-2026-10-12\INFORME.md. Captura 180,037 s/36 muestras, sin cliente ni conexiones al juego en extremos. CPU PC~2,6%, servicios~0,028%, suma working sets~888MiB; GPU telemetría~15,39W,48–49C. No hay medición accesible de potencia/temperatura CPU ni consumo total de enchufe. E: reside en Seagate Portable USB.

Simulación con supuestos explícitos 80/110/150 W totales =>13,44/18,48/25,20 kWh en168h. No son rango medido ni predicción de carga. CSV/JSON/script reproducible y snapshot de script junto al informe. Sin tarea semanal ni monitor persistente.

Usuario informa factura mensual reciente ARS50.000, extremos100.000; no informó kWh/tarifa. No inferir precio unitario a partir del total. Ejemplos100/200/300ARS-kWh son hipotéticos, no cotizaciones locales.
