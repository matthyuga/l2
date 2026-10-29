# Lineage 2: Giran caos V9

- Proyecto real: `E:\l2-local`. Implementado el 11/10/2026.
- `.giran` ahora abre dos bandos: 19 bots anteriores + Hellkevin defienden; 20 nuevos atacan con Raiders nivel5, crest/ally0. Hellsing conserva Giran; Holly/Sacred/Fury/Waves registrados como defensores. Logos anteriores intactos.
- Seis parties atacantes 5/3/3/2/2/2 y tres solos (Rhogar, Urkan, Veyron); supports acompañados. Agendas variables, accesos norte/sur, demoras y patrullas/intercepción. Ares y Nyx conservan su labor de guardianes.
- Dagna despliega un Siege Golem; Borin un Wild Hog Cannon. Despliegue instantáneo del lab mediante efectos nativos13/299, sin enseñar skills/cambiar builds. Daño nativo, duración/mantenimiento nativos; uno de cada por ejecución. El cañón usa Summon.doCast4230 y el gólem ataca la cara accesible de puertas; evita exigir ruta al centro de la puerta cerrada.
- Prueba final PASS1095: bandos/parties, PvP HP/CP, heal, 64 destinos distintos, daño de ambas máquinas, movimiento y limpieza; sin humano ni conquista. SQL/roster posteriores PASS39/39; todos offline, owner/calendario preservados. GameServer queda activo, siege inactivo, activación manual `.giran` > Preparar > Iniciar. `.giran legacy` conserva modo anterior.
- Runtime/fuentes/cloud overlay sincronizados. Cliente y core intactos. Backup privado y evidencia: `backups\giran-chaos-v9-2026-10-11`. Documento: `GIRAN-CAOS-DOS-BANDOS-V9.md`. Verificación opcional `Start-L2Local.ps1 -VerifyGiranChaos`, solo sin clientes.
- Pendiente ver apariencia del marcador de bando y balance de batalla prolongada en el cliente. No afirmar validación visual realizada.
