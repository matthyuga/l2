# Lineage2 — pruebas de capacidad, 11/10/2026

Ruta real: E:\l2-local. Usuario autorizó hacer las simulaciones. GameServer PID25748 continuó vivo, sin reinicios ni clientes conectados.

Se construyó helper opt-in headless con 100 copias temporales de los 39 perfiles, cuatro clanes temporales, dos bandos, parties, movimiento, asalto y PvP nativos. Gólem/cañón y guardianes. Escalones39/50/75/100; ninguna modificación permanente de IA/builds originales.

Primera pasada sin protección de XP completó39/50 y cortó automáticamente en75 por sobrecarga. Diagnóstico: muerte baja a79, restauración a80 y escritura de skills; JFR encontró rutas y esperas a base. Exportación JSON pesada coincidió con parte de esta pasada: no usarla como comparación limpia. Exportación eliminada, JFR binarios conservados.

Segunda pasada protegió SOLO copias contra XP/drops con onEvent y teamsRED/BLUE, conservando daño/muertes.39/50 completos;75 movimiento/asalto completos y185/240 ciclosPvP antes de STOP manual.100 no ejecutado: pico de40,9segundos en coordinadorIA de75 justificó detener escalada. PvP p95:39=807,6ms,50=2444,1ms,75 parcial=7960,6ms. Heap global máximo segunda pasada~1994MiB de8192 disponibles. Movimiento/asalto mucho más rápidos. RAM no fue el primer límite; latencia del coordinador sí. No certificar75/100 como fluidos ni extrapolar miles dividiendo RAM por huella local. CPU%global16threads no descarta cuello serial. Heartbeat separado mucho más rápido: no equivale a JVM congelada. Peso relativo de rutas/BD/summons/revival aún no aislado.

CleanupPASS y verificación independiente:39 personajes,117subs,9704skills,259dyes,78variables,1075items,6clanes,castillo/inscripciones idénticos al respaldoSQL. Cero filas temporales, cero objetosWorld/refsPets/servitors, bloqueo libre, siege inactivo,WorldPlayers0.20nuevos checkerPASS. HP/MP/posición guardianes/puertas restaurados por snapshot. Logs históricos conservados.

Informe: E:\l2-local\reports\capacity-benchmark-2026-10-11\INFORME.md. CSV/JSON/JFR en mismo directorio y protected. RespaldoSQL privado en backups\capacity-benchmark-2026-10-11. Helpers tools-src\custom\GiranSiegeLab\GiranCapacityBench*.java y Capacity*Attach*.java; no autoload. Verificador lab-panel\scripts\verify-capacity-cleanup.js. Final native-cleanup.txt y cleanup-verification.json son evidencia.

Próximo trabajo razonable: aislar/corregir picos antes de aumentar combate simultáneo. No se cambió IA productiva para este objetivo. Prueba corta, aleatoria, sin cliente: no mide FPS, red a espectadores, horas de estabilidad ni múltiples sieges.
