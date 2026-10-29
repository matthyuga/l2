# Diagnostico summon, sin implementar fix

Proyecto real E:\l2-local. Usuario pide revisar summon que no obedece movimiento.
Servicios DB/GameServer apagados al diagnostico; no arrancados. No pudo consultar
estado vivo ni observaciones SQL de ultima pelea. Sin cambios core/IA/config.

Confirmado en fuente Y javap jar actual: SummonAI.setIntentionAttack y
setIntentionFollow rechazan si PATHFINDING>0 y PathFinding.findPath=null.
GeoEngine.ini PathFinding=2. Unica geodata21_19.l2j (Elven); Coliseo24_19
sin geodata. PathFinding retorna null inmediatamente si origen/destino singeo.
Probe Java read-only contra GameServer vigente carga geodata y confirma:
PathFinding2, Coliseumgeo=false, Elvengeo=true, Coliseumsummonpath=null.
Evidencia E:\l2-local\backups\summon-diagnosis-2026-10-09\SummonPathProbe.java.
Primer probe tambien invoco canMoveToTarget que inicializa FenceData/DB y
dio warnings por pool ausente; no hubo DB disponible ni writes efectivos.
Se retiro esa invocacion y probe final limpioPASS. No servicios arrancados.

Causa general de seguimiento/ataque para TODOS summons en zonas singeo,
no especifica Nightshade ni usuario. MoveToTarget(action53) usa otra ruta y
puede fallar por controles/target/movimiento; no atribuir toda orden a causa
unica sin observacion viva. Noctis tambien afectado. GeodataColiseo pendiente.
Fix recomendado condicionar prechequeo estricto a coberturageo y permitir
movimiento normal donde nohaygeo, sin apagar PATHFINDING global ni atravesar
obstaculos dondehaygeo. Siguiente implementacion requiere autorizacionusuario.
