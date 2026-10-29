# Dust2 integrado como exploración en L2 — 14/10/2026

Kevin autorizó incorporarlo. Proyecto real E:/l2-local; cliente E:/l2.

Ya instalado HGDust2Arena.usx y 37 actores sobre el mapa actual24_19, conservando muelle y aeronave. 9.932 triángulos, 34 texturas. Parcela141000,57000,8000, escala GoldSrc1.5. Geodata87.390 celdas, 2.153 multicapa, CT/T conectados. Comandos .dust2 / ct / t / salir / estado. Inicialmente paz y respawn al muelle; sin rondas ni bombas, sin cambio de nacimiento/equipo.

Reinicio ordenado sin clientes: nuevo GameServer21308, Login18184 intacto. PASS de prueba transitoria real del handler: 40 pisos, pasos permitidos/bloqueados, alturas superpuestas, paz/respawn, CT/T y regreso; pisos de muelle/nave/Coliseo preservados. Recursos nativos y cifrado verificados. **No hay comprobación visual ingame todavía**, faltan cámara/recorrido completo y LOS de combate para certificarlo como arena PvP.

Documentos E:/l2-local/DUST2-EN-L2.md y research/dust2-integration/README.md; installation.json y server-smoke.txt. Respaldo E:/l2-local/backups/dust2-integration-20261014-131945. Retirar Dust2 antes de rollbacks de aeronave/muelle; no aplicar builds históricos sobre el mapa actual. Se preservaron las diferencias entre WorldContent.ini de runtime/source/cloud. Sin commit/push.
