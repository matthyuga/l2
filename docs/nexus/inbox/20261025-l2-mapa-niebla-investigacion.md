# L2: mapa ampliado y niebla — 25/10/2026

Proyecto real E:\l2-local. Investigación en research/map-fog-analysis-20261025/README.md y salidas de lectura de Interface.u/XDAT/NWindow.u del cliente system-hud.

Confirmado estáticamente: ya existe MinimapWnd_Expand; Enlarge Map abre esa ventana y Collapse vuelve al compacto. Ajusta tamaño según resolución con límite1024. No hace falta importar expansión de otra crónica. Máscara global opaca + personal tenue sigue propuesta, sin implementar.

REA abrió/identificó/cerró NWindow.dll PE x86. Frida attach no completó; no se cargaron scripts ni se verificó ejecución del mapa. Computer Use pipe no disponible. Lectura Unreal realizada con parsers locales, no atribuirla a REA. Juego siguió respondiendo, sin instalación/cambios de cliente o servidor. Próximo: cobertura de prueba en staging y validar desplazamiento/escala/orden de dibujo en ambos mapas.

Actualizaci?n: petici?n expl?cita de analizar composici?n con REA. Ghidra complet? NWindow.dll; 31 evidencias exportadas en research/map-fog-analysis-20261025/rea-map-composition-evidence.json y conclusiones COMPOSICION-REA.md. OnPaint0x101895c0, DrawWorldMap0x10187910, DrawTownMap0x10189130, arrastre0x1018b5d0; offsets internos+25c/+260. Padre XDAT com?n no transmite scroll interno. Propuesta PaintFog dentro del recorrido nativo; hook/firmas/m?scaras/transporte servidor-cliente y runtime a?n pendientes. Sin cambios al cliente/servidor.
