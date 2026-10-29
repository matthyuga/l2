# Nexus TV v4 optimizada — 17/10/2026

Proyecto real E:\l2-local, controlador nexus-tv. Kevin pidió optimizar1080p. Instalados cambios solo Python (server/decoder/renderer), sin DLLs/paquetes/modelo/posición. Reiniciado solo controlador, ningún cliente L2 abierto/cerrado.

Comparación aislada actual mismo banco: local1080p30 salida23,13→28,59FPS, proceso37,48→20,56ms; YouTube salida16,8→22,2FPS y contenido11,7→20FPS, eligióhd720. No confundir con FPS del motor ni afirmar30estables: p95 local56,59ms y máximo84,50ms. Prueba dentro de Giran con ambos clientes pendiente de Kevin.

Conversión BGRA nativa/lienzo reutilizado,2hilosFFmpeg, cadencia absoluta, caché de tarjetas, vista previa/compatibilidad y consulta de estado fuera del envío principal, backpressure Chrome. Calidad/resolución conservadas. Variante ctypes descartada por no mejorar.

Checks pausa/seek/play/calidades/cámara/off/lista/HD/512/preview PASS; imágenes idénticas al original; receptorD3D9 con patrón1080p pausado180/180, HRESULT0. Estado finalv4 listo, cámara/fullhd/volumen30/sinerror, lista conservada. Sin commit/push.

Informe: E:\l2-local\research\giran-screen\optimization-v4\INFORME.md. Evidencia final.json/baseline-isolated.json/installed-check.json. Respaldo E:\l2-local\backups\nexus-tv-opt-20261017. Audio y4Kfluido pendientes. No abrir/cerrar clientes automáticamente.
