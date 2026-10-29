# Cerebro tactico integrado y probado

Sesion salas15/10/2026. Trabajo E:/l2-local/research/pvp-tactical-engine; RESULTADOS.md, comparison.json, mechanics.txt, live-audit.txt y installation.json. Activo PID27412 sin reiniciar ronda/trasladar usuario.12fuentes runtime/source/overlay; sin cliente/core. Ultimo verificador cadena verify-installation.py:61hashes.

Seis combates validos30s, mismos6perfiles con lados intercambiados:vslegacy +140,8%dano y0/4muertes;vsadaptador siege +2,6% y1/4;vspatron AresNyx +38,6% y1/2. Muestra pequena, no estadistica ni victoria universal. Siege usa cast real con objetivos de sala; guardianes prioridades trasladadas a Players iguales, no NPC originales con stats especiales. No se inicio siege. Mediciones invalidas de fixtures de teleport descartadas y documentadas.

Casos nativos en Primeval pasaron:heal aliado2526HP, Silence ejecutado(resistido en muestra), UD, kite103unidades dentro de mapa, summon+TP, danzas/buffs party, FFA-noheal y otra instancia-noheal.31clases avanzadas mapeadas;9roles. En vivo6/6bots tacticos auditados. Parties humanas, rondas y tandas conservadas.

GM `.salas bots cerebro clasico|tactico`; defaulttactico en arranque. Roster selector exacto temporal restaurado, fixtures ybaselines solo research. No reejecutar agentes que definen clases sobre mismoPID. Rollback normal requiere parar bots/servidor antes de restore.py; snapshot roster aun no persistente ante crash.

Limites:desniveles/capasElven, VOS no probadoahora; reviveautomatico completo, corpse summons/cubics/pet skills/AoEhostil no certificados/completos. NoLLM ni MPinfinito. Antes de prometer IA humana o mayorcapacidad leer RESULTADOS.md.

17:02 cierre: nueva auditoria PASS6/6 y61hashes. Se observaron timeouts de LabTelemetry/pool JDBC hasta16:59:52; en dump posterior sin esperaHikari y consulta actualsinbloqueos largos. Causa no confirmada; revisar telemetria antes de aumentar carga. No se cambiaron DB ni otra sesion. Detalle RESULTADOS.md.
