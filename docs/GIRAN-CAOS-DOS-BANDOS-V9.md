# Giran: dos bandos y movimientos variables (V9)

Implementado el 11 de octubre de 2026. `.giran` abre este escenario; `.giran legacy` conserva el laboratorio anterior. Activación manual por Hellkevin, líder de Hellsing. Giran debe pertenecer a Hellsing y estar sin siege activo.

## Bandos y grupos

Hellsing, Holly, Sacred, Fury y Waves defienden: los 19 bots anteriores más Hellkevin, con sus logos. Ares y Nyx mantienen su patrulla, combate y resurrección como guardianes. Los veinte nuevos integran Raiders, clan nivel 5 sin crest ni alianza, registrado como atacante mediante el motor nativo. El indicador de bando usa el estado nativo del siege.

| Grupo atacante | Integrantes |
| --- | --- |
| 5 | Darion, Valerian, Seraphine, Mazhura, Nysera |
| 3 | Malrik, Lucien, Nerys |
| 3 | Darius, Thalion, Elowen |
| 2 | Draven, Saevra |
| 2 | Zareth, Faelith |
| 2 | Dagna, Borin |
| Solo | Rhogar |
| Solo | Urkan |
| Solo | Veyron |

Son seis parties nativas y tres jugadores realmente sin party. Los healers y soportes tienen compañeros. Las recetas, razas, clases principales, tres subclases, dyes y equipo +4 permanecen iguales.

Cada grupo elige acceso norte/sur y demora inicial independientes. Tras las puertas, cambia objetivos del patio y salón, con pausas y desplazamientos variables. Los defensores patrullan e interceptan amenazas. Darion intenta la conquista nativa con su escolta. Se conservan geodata, puertas, colisiones, ataque, curación y resurrección nativos. Durante el combate los desplazamientos usan AI y rutas; los teleports se limitan a preparar, traer aliados, reaparecer y limpiar el laboratorio.

## Maquinaria

Dagna despliega un Siege Golem (14737); Borin, un Wild Hog Cannon (14768), una vez por ejecución. Es un despliegue instantáneo explícito del laboratorio mediante los efectos Summon nativos 13/299: no agrega skills aprendidos ni cambia profesiones. Comprueba las condiciones nativas, consume los cristales y MP iniciales y abastece las gemas de mantenimiento. Cada entidad conserva sus estadísticas, mantenimiento y duración nativa de veinte minutos. Si muere o expira, no se reemplaza en esa ejecución.

El gólem ejecuta ataques nativos contra puertas válidas a distancia de melee; el cañón usa su skill nativo 4230 y su tiempo de lanzamiento/reuso. Se respetan distancia, visibilidad y legalidad del objetivo. Ambos se retiran al finalizar.

La orden genérica de summon exige una ruta hasta el centro elevado de la puerta cerrada. Para estas dos máquinas, el controlador usa un punto accesible frente a la puerta y la ejecución nativa de ataque/lanzamiento; el cañón recibe la intención CAST de su AI. No modifica geodata ni aplica daño manual.

## Uso

1. Abrir `.giran` sin party, fuera de combate y sin invulnerabilidad GM.
2. Pulsar **Preparar defensa y atacantes** y luego **Iniciar siege**.
3. Las órdenes patrullar, seguir, traer y retirada controlan a los defensores aliados; los atacantes mantienen sus agendas.
4. **Finalizar siege** limpia parties, Players, summons y bloqueo global. La finalización del asedio y una conquista efectiva conservan el resultado nativo.

El modo comparte exclusión con `.arena`, `.ia`, `.agite` y el laboratorio anterior. Desconexión del operador cancela y limpia. No cargar Hellkevin como piloto artificial.

## Verificación y continuidad

Compilación local con JDK 25. La prueba optativa `Start-L2Local.ps1 -VerifyGiranChaos` exige ausencia de clientes y nunca carga al usuario ni completa una conquista; prueba bandos, parties, combate, soporte, destinos variables, maquinaria contra puertas y limpieza. Restaura propietario, calendario, reputación y contadores de clanes y deja las inscripciones del nuevo escenario preparadas. Consultar `GIRAN_CHAOS_VERIFY` en `logs/game-stderr.log` para el resultado de cada ejecución.

La apariencia exacta del indicador y el equilibrio de una batalla prolongada se revisan en el cliente. Las pruebas aisladas no sustituyen esa revisión visual.

Resultado final: `GIRAN_CHAOS_VERIFY PASS` (1095 comprobaciones, 19:56:48). Se comprobó daño PvP en HP/CP, intercepción defensora, curación real, 64 destinos distintos, daño del cañón y del gólem contra puertas, desplazamiento nativo del solitario, bandos y parties, alianza de los guardianes y limpieza. No se cargó al usuario ni se completó una conquista. Las comprobaciones de persistencia posteriores pasaron: veinte Raiders offline, cinco logos anteriores intactos, inscripciones correctas, equipo/recetas de los veinte nuevos y roster completo 39/39. Evidencia: `backups/giran-chaos-v9-2026-10-11/verify-final.log`, `persistence-final.json` y `roster-final.txt`.

Durante el diagnóstico se recargó únicamente `GiranChaosMachinery` en la JVM local mediante un helper de instrumentación, sin tocar clases del core. Al terminar se instaló la versión limpia, equivalente en comportamiento y sin trazas de diagnóstico. Los helpers de diagnóstico no forman parte del arranque normal ni son necesarios para usar el escenario.

Backup previo: `backups/giran-chaos-v9-2026-10-11`, incluyendo SQL privado. Runtime: `server/game/data/scripts/custom/GiranSiegeLab`; espejos: `source/L2J_Mobius_CT_0_Interlude/dist` y `cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist`. No se modificaron el cliente ni el core.
