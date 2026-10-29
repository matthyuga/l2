# Niebla continental con Giran despejada — 25/10/2026

Kevin confirmó V1 (capturas parcial/opaca/apagada), pidió cubrir todo excepto Giran con bordes naturales. V2 preparada e instalada después de que confirmó cierre del juego por herramienta async. Trabajo E:\l2-local\research\map-fog-giran-v2; README técnico y manifiesto. Backup map-fog-giran-v2-20261025-221355.

Proxy nativo V2 y paquete NexusMapFogV2.u; NWindow/Interface conservados. Polígono municipal de custom_town.xml convertido a máscara alfa, nubes procedurales, hasta5 dibujos recortados por visor. Usa conversión nativa mundo→mapa para continental/urbano. Default modo2 opaco fuera de Giran. Controles anteriores parcial/opaca/apagar siguen; centrar deja de ser necesario y muestra explicación.

Compilación nativa, harness de hooks, HAL16Present, alpha de assets y BGRA exacto importado al paquete PASS. UCC no tiene xDxTex: texturas BGRA8 verificadas sin compresión, no fingir validación visual. Pendiente screenshot in-game y alineación en Giran/urbano. No hay servidor reiniciado ni .explora conectado, ni animación temporal. Restaurar V2 con restore.py vuelve V1; luego restaurar V1 si se desea retirar todo.
