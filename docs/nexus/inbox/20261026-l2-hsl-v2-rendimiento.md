# HSL v2 instalado: destello y rendimiento

El usuario confirmó que funciona la integración v1 dentro del creador, pero reportó destello original y lentitud al arrastrar. REA sobre DLL enviada confirma setter nativo HairColor cada 40ms en arrastre y GetPrivateProfileIntW por cada DrawTexture (diagnóstico). Evidencias guardadas en E:\l2-local\research\character-creation\2026-10-26-hsl-ingame-v2.

V2 instalada en ambos perfiles: solo NexusHairHslGame.dll. Ahora RGB reutiliza material por instancia sin recargar apariencia (setter solo fallback de inicialización), track de preview filtrado por modelo y aplicación inmediata tras cambios, consulta de diagnóstico una vez, plano H/S cacheado, LUT luminancia. Alpha/protegidos exactos; delta RGB máximo1/255 observado. Microbenchmark 524288pixeles75.619ms ->2.850ms (~26.5x cálculo, NO FPS). 20506 checks,183 transiciones función real sin carga de recursos, preflight motor realPASS.

Server, engine, NWindow y protocolo sin cambios. Manifiesto v1 actualizado con hashes v2 para conservar rollback completo. Backup E:\l2-local\backups\hair-hsl-ingame-v2-20261026-232116. installation.json/rollback.py/README/final-verification en carpeta v2. Confirmación visual de fluidez/destello v2 pendiente. No afirmar que se ha medido FPS.
