# Alas, vuelo y combate montado ? 13/10/2026

Idea del usuario: alas como alternativa visual a montura voladora; exploracionterrazas; montura tanque conHPantesdeljinete mientrasjugadorlanzaHydroBlast. No implementado.

Codigo local comprobado: entity/actor/Player.java mount(Summon)6461 desequipaarma/escudo, detienetoggles, setMount,broadcastRide y pet.unSummon6492. setMount9426 activa setFlying(true) paraWYVERN; NONEdesactiva. Restriccion skills8899+:STRIDER permite skill.isMagic oSiegeAssault;WYVERN soloBreath/Aegis. No afirmar prohibiciongeneral demagiamontada ni queHydroBlastprobadoingame.

ValidatePosition90 tiene rama especialisFlyingparaalturaZ. MoveToLocation89 verificageocelda completamente bloqueada ypuertas: vuelo no equivale eliminar todaslascolisiones/geodata. Sinvideoconcreto noidentificar skillGM comorealvuelo/desactivaciongeodata.

PlayerStatus149+ transfertdamageservitor a1000distancia ylimita aHP-1. Es precedentedeabsorbcion, no sistemaHPmonturatanque listo, puespetdesapareceal montar yreglastienenlimitesdistintos.

Propuesta: poolHPlogicodearmaduramontura,derivacionde da?o PvPantesHPjinete,desmontajealagotarse; definirCP/criticos/DOT/debuffs/curas yvueloseguroaldesmontar. Entidadmontura realcontargetpropio/subida2actores yanimacionesesotrotrabajomayor. Alasornamentales nocreanvuelo. Menorcosteartisticonogarantizamenorcostetecnico porclientepose/animaciones/movimiento/aterrizaje/sync.

No modificarserver/client ni comprarcontenidocomoreaccion aestaidea. Proyecto vueloexploracionseparadodePvPmontado sepuedeprototiparcuandousuarioautoricelaimplementacion.
