# Cerebro tactico de salas: integracion y comparacion

15/10/2026. **Integrado y activo** en GameServer PID27412. No se reinicio la ronda ni se movio al personaje del usuario para activarlo. Se preservan las cuatro salas/instancias, tandas, votos y parties humanas.

## Resultado de las comparaciones

Se usaron seis personajes nativos de laboratorio, con sus builds/equipo, buffs y consumibles normales. Cada rival se comparo durante dos combates de30s, intercambiando que lado usaba cada cerebro. Entre combates se restauraron recursos, efectos, cargas y reuse del banco; no se rellenaron recursos durante el combate fuera de las potas normales. Sin respawn dentro de esas ventanas.

| Referencia | Dano nuevo | Dano referencia | Diferencia de dano | Muertes nuevo/referencia |
|---|---:|---:|---:|---:|
| Controlador de salas anterior |49.352,7|20.494,5|+140,8%|0/4|
| Combate adaptado del siege |46.043,9|44.878,0|+2,6%|1/4|
| Prioridades Ares/Nyx adaptadas |44.652,0|32.214,0|+38,6%|1/2|

Conclusion:en esta muestra la mejora es marcada frente al controlador anterior. Frente al siege, el dano es practicamente equivalente y la diferencia favorable aparece en supervivencia/soporte. No se demuestra superioridad universal:el nuevo perdio una pasada contra la referencia de guardianes; influyen la composicion, terreno y RNG. Son seis ensayos exploratorios, no una estimacion estadistica de win rate.

`trials.csv` contiene las12filas validas (dos lados por combate), `comparison.json` los agregados y `roster.txt` las identidades/clases/equipo. Las ordenes no se usaron como sustituto de dano:el dano procede de ON_CREATURE_DAMAGE_RECEIVED y las skills de ON_CREATURE_SKILL_USE.

### Que se comparo exactamente con los mejores NPC/bots locales

- Baseline LEGACY:instantanea del brain de salas previo, guardada como PvpLegacyBrain en research.
- SIEGE_CAST:adaptador de combate que usa **el metodo cast real de SiegeSquadBrain**, sus prioridades ofensivas/curacion/defensa y las mismas potas de las salas. Sustituye objetivos/amistades de castillo por blancos legales de la sala. No ejecuta conquista, treguas o formaciones dependientes del castle.
- GUARDIAN_PATTERN:prioridades de ataque de GiranGuardianBrain/Ares-Nyx, trasladadas a los mismos Player para conservar atributos comparables. No se trasladaron las estadisticas especiales de los guardianes ni su patrulla.

No es un duelo contra los Ares/Nyx originales con sus HP/estadisticas de NPC. No se inicio ni se modifico un siege para hacerlo. Esa distincion evita atribuir al cerebro una ventaja causada por atributos diferentes.

El equipo fijo de un lado llevaba healer/archer/dagger y el otro mage/tank/duelist; al invertir cerebros ambos controladores pasaron por ambas composiciones. No se crearon clones, se cambiaron builds o se concedieron skills. Los seis perfiles incluian ArenaNerys, Velith, Caelan, ArenaValerian, ArenaRiven y ArenaDarion. Se usaron solo personajes libres del roster verificado; los activos de produccion y los reservados para la siguiente tanda quedaron fuera del banco.

## Mejora implementada

`PvpTacticalEngine` opera sobre los Player ya reservados. Resuelve nueve roles por clase nativa y arma, con31nombres avanzados del core comprobados, incluyendo EVA_SAINT/EVA_TEMPLAR.

- Healer:prioriza vida del destinatario legal; curas propias de emergencia y seguimiento de soporte. No pasa a golpe fisico porque no pueda castear.
- Mage:nukes de su familia, debuff faltante, Silence ante caster y distancia. Evita repetir controles cada500ms.
- Archer:RapidShot, StunShot/ataques aprendidos y retirada nativa con margen de perimetro.
- Dagger:Bluff, blows y Backstab condicionado a posicion; defensa por HP.
- Tank:Stun/root, ataque, UltimateDefense y habilidades propias de supervivencia.
- Warrior:habilidades compatibles con arma/cargas y ataque nativo. No concede cargas artificiales.
- Summoner:invocacion especifica de su familia/servitor, TP cuando corresponde y orden al pet contra rival propio de sala.
- Support:canciones/danzas conocidas y validacion de todos los receptores del efecto de party.
- Buffer:habilidades de su familia (por ejemplo chants de Doomcryer), detectar ausencia y no sobrescribir una variante equivalente mas fuerte del mismo abnormal.

Potas, shots y materiales siguen los handlers y reutilizacion nativos. No hay dano artificial, MP infinito, cambio de estadisticas ni teleport como tactica. Movimiento comprueba altura, geodata y pertenencia al mapa. Targets automaticos siguen limitados a bots propios de la misma instancia; equipos mandan sobre clan/party.

Se conectaron `PvpSiegeBrain` y `PvpRoomBots`, conservando el cuerpo anterior como fallback. El tick tambien permite soporte sin enemigo y no reinicia casts en curso. El roster y el controlador de rondas no se modificaron permanentemente en esta etapa.

## Pruebas funcionales con ejecucion real

`mechanics.txt` y `mechanics-status.txt`:fixture aislado que eligio Primeval mediante un voto valido del modelo de ronda y completo todos los siguientes casos:

1. Curacion nativa de otro bot:dos casts y ganancia observada de2.526HP en el caso controlado.
2. Silence ejecutado por el caster apropiado. En la muestra final el efecto no quedo activo:las resistencias nativas se respetan, no se fuerza el debuff.
3. UltimateDefense activo sobre el tanque herido.
4. Kiting nativo con103unidades de desplazamiento observado dentro del perimetro de Primeval.
5. Summon real en la misma instancia y TransferPain activo.
6. Danza/cancion nativa que llego a un aliado; habilidades271/274/275 ejecutadas por el dancer.
7. Buffs faltantes repuestos por un buffer:chants1007/1251/1362 entre los eventos.
8. Un miembro de la misma party marcado como oponente FFA no fue curado.
9. Un actor llevado a una sala de otra instancia no fue seleccionado para curar.

Se fijaron HP bajos solo para provocar condiciones de estas pruebas funcionales; no se contabilizaron esas reducciones como dano del benchmark. Esos casos no prueban todas las habilidades ni todos los matchups de cada clase.

`live-audit.txt`:tras activar, seis de seis bots del encuentro real mostraron ticks tacticos. Se observaron casts nativos de nukes, Gloom, Silence, ShieldStun/Shackle, UltimateDefense y curas, manteniendo consumibles. El registro del lobby siguio apuntando al controlador original y no se observo un cliente real ni un objetivo de autoataque no reservado dentro de esa muestra. Los contadores nativos del roster acumulan tambien la actividad anterior a la activacion; los contadores tacticos empiezan con el nuevo cerebro, por lo que no deben confundirse.

`startup-check` compilo los scripts instalados contra las librerias actuales. `installation-audit.json` verifica61archivos de la cadena de salas. No se instalo Kotlin, un LLM, SQL de terceros ni cambios de cliente/core.

## Limites y pendientes concretos

- El muestreo comparativo es corto, con composiciones fijas intercambiadas; no prueba balance para todos los mapas, cantidades y clases.
- Elven tiene desniveles/capas que limitaron algunos acercamientos. Se rechazan destinos con salto vertical>128; no hay solucion completa de navegacion tactica por todas las capas. La prueba funcional de movimiento tambien se hizo en Primeval. No se certifico Valley of Saints en esta etapa.
- `controls` cuenta debuffs no daninos **ejecutados**, no necesariamente acertados. `healed_hp_samples` suma incrementos entre muestras e incluye regen/potas; no es una medicion atribuida solo a habilidades de cura. El tick medio del CSV incluye ambos cerebros y observacion; no sirve para atribuir coste individual ni afirmar capacidad de4salas llenas.
- La resurreccion usa la habilidad/request nativos, pero no se certifico en esta etapa un ciclo automatico completo de aceptar revive entre bots. Se conserva la reaparicion propia de bots a10s. No se fuerza revive de jugadores.
- Necromancer con summon sobre cadaver, cubics, habilidades del pet y todas las rotaciones/cargas no estan completas. El summon comprobado fue de ArcanaLord; no todas las invocaciones son intercambiables.
- No se ejecutan habilidades hostiles de area desde la nueva politica hasta verificar cada familia. Las areas positivas se revisan contra todos sus receptores y deben conservar las reglas nativas de alcance/clan/party.
- No se incorporo aprendizaje automatico ni conversaciones de Ollama. La IA es local y por reglas revisadas.
- El snapshot del roster aun no es persistente ante crash. Mantener retirada normal de bots antes de apagar o usar los mismos personajes en otro lab.

## Operacion y vuelta al controlador anterior

Comandos GM:

```
.salas bots estado
.salas bots cerebro clasico
.salas bots cerebro tactico
```

El selector cambia el cerebro de las salas activas sin reasignar parties, reiniciar el reloj o rellenar recursos. Al arrancar normalmente queda habilitado el tactico por defecto. Para retirar actores/preparaciones sigue vigente `.salas bots parar todas`.

Instalacion:12fuentes sincronizadas en runtime/source/overlay, respaldo `E:/l2-local/backups/pvp-tactical-engine-20261015-165307`, manifiesto `installation.json`. Cuatro archivos por copia:dos controladores modificados y dos helpers nuevos. Para rollback completo:retirar bots normalmente, detener GameServer, ejecutar `restore.py` y arrancar por el lanzador normal. Para comparar comportamiento basta el comando clasico; no hace falta revertir archivos.

## Incidencias del banco y trazabilidad

Las pasadas de `discarded-fixture-v1` y `discarded-fixture-v2` **no se usan en las cifras**:primero se corrigio una sobrecarga de teleport que interpretaba instancia como randomOffset; despues se completo onTeleported para que actores sin cliente reaparecieran realmente. Se agregaron comprobaciones de spawn/instancia y minimo de dano. Los actores de esas pasadas fueron retirados por finally.

Tambien se ajustaron pruebas de mecanicas para que Silence tuviera un caster como rival efectivo tras el kite del healer, y para devolver el actor a mundo0/finalizar su stance antes de entrar por el lobby a otra instancia. Eran condiciones del banco, no evidencia de que debamos anular requisitos del juego.

Una redefinicion de prueba se rechazo al eliminar un nest sintetico de switch(enum). Se conservaron los atributos de la clase cargada y se usan switches por nombre para que la actualizacion de roles no reutilice un mapping sintetico anterior. La activacion final fue aprobada y auditada.

El selector exacto de perfiles se inyecto temporalmente para las pruebas y se restituyo al activar. PvpLegacyBrain, PvpTacticalSelection, fixtures y adaptadores del siege quedaron solo en research; no se instalan en el arranque normal. No volver a ejecutar agentes de definicion de helpers sobre este mismo proceso:las clases ya existen. Para repetir el banco, preparar un arranque de laboratorio con su selector/fixtures, conservando el registro del lobby y retirando siempre los actores.

## Comprobacion final 15/10 17:02

Se repitio la auditoria en vivo:6/6 bots con actividad tactica, registro del lobby intacto y sin clientes reales ni objetivos ajenos al roster en la muestra. Los perfiles del fixture quedaron offline;12reservas SQL corresponden a6activos+6preparados para la proxima tanda. Se verificaron nuevamente61hashes.

El registro mostro timeouts del pool JDBC (10conexiones ocupadas) en escrituras de LabTelemetry hasta16:59:52. En el thread dump de17:00:58 ya no se observaron esperas en Hikari/DatabaseFactory; la consulta posterior solo mostro operaciones de0segundos y la auditoria de combate completo normalmente. No se atribuye causalidad al cerebro ni se considera resuelto el cuello de botella:queda pendiente revisar volumen/cola de telemetria antes de ampliar bots o certificar carga. No se modificaron parametros de base de datos ni la otra sesion.
