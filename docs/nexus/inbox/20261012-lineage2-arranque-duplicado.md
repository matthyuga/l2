# L2 no abria: arranque duplicado

- Ruta real E:\l2-local, 12/10/2026 ~13:12-13:19 Buenos Aires.
- Usuario reporto lanzadores negros sin entrar. Cuatro GameServer simultaneos (18272,5388,19168,3532), ninguno aun en7777, con4JVM compitiendo. Thread main18272 leyendoXML TeleporterData, no bloqueo WorldRegion.
- Se eliminaron solo3duplicados (sinclientes/puerto), conservo18272; puerto7777 abierto13:14:54, registradoLogin. Login19116 yMariaDB11920 conservados. run/game.pid corregido18272.
- Start-L2Local.ps1 corregido: mutexLocal porhashruta, espera otroslanzadores, adoptaGameServerpreexistente cargando, falla rapido si servicio termina, mensajesprogreso. Mirrorcloud-repo/ops/windows sincronizado. Reserva backups/startup-single-instance-2026-10-12.
- Test2lanzadores trasmutex ambos esperan/luegoREADY, stderrvacio, solo1GameServer. HarnessExitCodeProcessnullcauso falsofallo inicial, resultadosverificadosporlogs/inventario. reports/startup-single-instance-2026-10-12/verification.json yDIAGNOSTICO.md.
- ClienteL2 finalmenteabierto/RespondingTrue/ventanaLineageII PID6712. HerramientaComputerUse nativepipeausente inclusoreset, sinverificacionvisualni login automatizado. Habia2clientes, intentoStop6712denegado(procesoelevado); inventarioposterior solo6712(elotrocerradoexternamente). No repetirStopsolecliente.
- Usuario puede usar2-JUGAR.cmd directamente, incluyearranque. Optimizacioncoleccioneslazy no revertida.
