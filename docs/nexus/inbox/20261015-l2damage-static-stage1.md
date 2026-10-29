# L2Damage — primera etapa estática terminada

15/10/2026. Usuario autorizó analizar primera etapa y avisar cuando hiciera falta instalar. Parche V3.4 extraído en E:\l2-damage\analysis\patch-v3.4 (406archivos,2.071.476.921bytes), subconjunto base system+mapas21_19/20_17 extraído en analysis/baseline-interlude. NO se preparó cliente jugable, ejecutó juego/DLLobjetivo, creó cuenta/contactó servidor ni tocó E:\l2/Mobius.

Documento principal E:\l2-damage\analysis\PRIMERA-ETAPA.md. Inventario/hash406,31PE,121comparables(41idénticos80distintos),9DAT/config decodificados, cinco tablas parseadas y comparadas con footerSafePackagePASS. Scripts reproducibles inventory.py,tables.py,decode413.cjs y evidencias en reports. Hashes system originales sin cambiosPASS. Reportes iniciales *keyword-lines.json son barrido binario preliminar; usar tablas *-parsed.json para conclusiones estructuradas.

REA6.5/Ghidra12.1.4: entry.dll x86UPX strings sincoincidencias(no prueba ausencia), l2.bin x86 con referencias InitEngine y arranque CRT descompilado0x109224da. l2.exe28MB, secciones.aazaltamente entrópicas, sin descompilación exhaustiva/ejecución/desempaquetado. MCP cerrado tras guardar evidencias. Interface.u126/license0:3946names7048exports,123names184exports añadidos respecto base; adiciones Teaser/EventMatchGM/Observer y variasUI, no selector PvP/voto dedicado en nombres/cadenas revisados. Xdat solo comparación de cadenas, no render/treecompleto.

ZoneName362registros igualbase, solo Siren'sDen->Sailren'sDen(id362). ElvenVillage113map21_19;Primeval20_17. Hunting220igualbase2cambios. Parche no reemplaza esas2baldosas (traeLobby17_16,19_22,23_21,23_23,23_24,24_12). No polígonos/reglasPvPrecuperados. Systemmsg2090vs2032; bienvenidaDamage94personalizada; no rotaciónenadiciones. NPC6541vs6511,30añadidos,MaximGlobalGK35722/etc; nombre no prueba spawn/menúactual.

Hipótesis: reglas principally servidor; no afirmar código ausente en todo binario ni recuperaciónpackDamage. Próximo paso útil para límites/timer/flag/respawn: preparar E:\l2-damage\client aparte, aplicarparche, entrar y observar. Esta etapa no autorizó ni efectuó ese arranque; se avisó al usuario que ya hace falta para esas preguntas. REAestático puede ampliarse para funcioneslocales concretas. Damage rotaciónaleatoriasinvoto,HELLGAMESvotaciónpropia al final (preferenciapersistente).

READMEobjetivo pide desactivarfirewall/AV, no se siguió. l2.ini127.0.0.1 sininvestigar conexiónreal; logincluido26/04/2021histórico, no pruebaactual.
