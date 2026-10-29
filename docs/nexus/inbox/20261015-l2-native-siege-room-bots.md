# HELLGAMES: bots de sala con perfiles siege ACTIVOS

Usuario reporto bots quietos y pidio usar perfiles siege con subclases, clan/sinclan, variados, partiesaleatorias. E:/l2-local/research/pvp-siege-bots.

Servidor estaba detenido al inicio; se inicio normalmente. PID27412. Bot controller hotredefined sin reemplazar lobby/reloj ni moverusuarios.24bots nativos activos:6porcada sala, perfilPARCIAL. Muestra17clases,17conclan/7sinclan,9parties. No clones: reserva temporal de perfiles offline verificados NormalNpcRoster/RealHumanPilots con3subs/equipo/habilidades; no usa perfilesqueotraspruebastenganonline niHellkevin. No mezcla partiesconjugadoresreales;partyfilterowned comprobado enrevisionfinal.

IA adaptada del siege para acercamiento/atasco, casts, curacionparty y autoattack nativos; sinobjetivoscastillo. Targetautomatico solo botspropios, nohumanos. Parties2..4aleatorias dentroequipo, regroupcadaron-da. Revive10s solobots.

TestsPASS6/6movieron>100unidades, SQLfingerprint clases/subs/skills/clans/equipmentcantidadesigualtrasrelease; votetie2/2,duplicados/tardios/abstencion/mapa/newroundPASS. Liveaudit24bots4rooms17clases9parties;movimientoyHP-CPcomprobados. BancoScript constructor alteraba registry yquitabaNPCcallbacks: SE RESTAURO producción ScriptManager registro +callbacks; lobby-registry-audit.txtPASS. No repetirfixture sinrestaurarregistro. Testextra16profilestardominutos porDBtelemetria; noajustarpool/pauseglobal.

IMPORTANTE retirar `.salas bots parar todas` ANTES de apagarserver/usar siege. Perfilesprestados guardan snapshot soloRAM; release restaura posicion/exp/resources/cooldowns/cantidadesefectospreviosaunvigentes. Crashrecoverypersistente NOimplementado. Noafirmarclones/intactopersistenciacrash. Botsseapaganporarranque;24actualesseiniciaronexpresamente.

9fuentes/scripts instalados runtime/source/overlay. Backupbackups/pvp-siege-bots-20261015-145524, rollbackhashguard.Stopbotsnormal,luegoserver,restore.py. Ordenrollback siege-bots/UI/bots/rondas/sync/autoflag. ReadREADME conlimites.
