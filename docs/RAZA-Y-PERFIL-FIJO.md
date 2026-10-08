# Raza y perfil inicial independientes de la clase

Implementado y verificado el 8 de octubre de 2026.

## Regla del servidor

- La raza guardada del personaje gobierna STR, DEX, CON, INT, WIT y MEN base.
- El perfil inicial FIGHTER/MYSTIC se guarda en `character_variables.RACIAL_PROFILE`.
- Evolucionar la principal, añadir una sub o activar otra clase no cambia raza ni perfil.
- Dyes, pasivos, equipo y buffs siguen aplicándose mediante las fórmulas normales. Los stats finales sí pueden cambiar con las skills: conservar atributos base no significa conservar todo el daño.
- El cambio explícito de raza mantiene el perfil y toda la build. En Build Lab existe **Cambiar SOLO raza**, herramienta GM sin precio por ahora. El servicio público/VIP, moneda y tarifa aún no están implementados.
- **RESET origen + principal (GM)** es otra operación, deliberadamente distinta: reinicia origen y principal. No es el botón normal de raza.

Las plantillas raíz elegidas son humano 0/10, elfo 18/25, elfo oscuro 31/38,
orco 44/49 y enano 53. El enano no tiene plantilla mystic nativa: usa sus
atributos nativos 53 incluso si el perfil guardado es MYSTIC.

## Alcance de este cambio

Se independizaron los seis atributos. El crecimiento de HP/MP/CP por nivel,
la velocidad base y las bases de ataque/defensa siguen siendo los de la clase
activa. Los recursos y demás derivados sí reciben el efecto del nuevo
CON/MEN/etc. Revisar esas curvas raciales completas es una fase diferente;
no se cambiaron fórmulas ni se añadieron multiplicadores artificiales.

No se modificaron las reglas existentes de acumulación/masteries ni se
añadieron subs a los siete pilotos de comparación. Sólo la principal sigue
con tercera profesión en esos pilotos.

## Migración y compatibilidad de datos

Se migraron los 17 personajes previos, usando raza guardada y el perfil de
la **principal guardada**, no el de la sub activa. Para personajes anteriores
sin historial de creación es una reconstrucción del origen actualmente
guardado, no una afirmación sobre su primera creación histórica.

Hellkevin: humano FIGHTER, principal Paladin (5), activa Mystic Muse (103).
Sus seis atributos base pasan a humano fighter; el INT/WIT de la sub élfica
ya no reemplaza ese origen. No se tocaron sus objetos, clases, dyes, skills,
posición ni fila de `characters`. Necesita una nueva captura al ingresar;
sus cifras anteriores no sirven para evaluar la nueva regla.

La tabla `lab_player_stats` etiqueta las capturas nuevas como
`rules_version=fixed-racial-v1`. El panel excluye las lecturas históricas
sin esa versión de la comparación actual y pide recapturar. El historial
de fases 2–5 y los nueve NPC del Coliseo se conserva: no se debe mezclar
esa telemetría histórica con nuevas mediciones como si fueran equivalentes.

## Verificación ejecutada

- Compilación completa del core y compilación de los scripts modificados.
- Siete pilotos reales preparados y recargados: misma cantidad de skills,
  equipo, dyes, buffs y stats antes/después de la recarga.
- `RacialProfileVerification`: ocho comprobaciones reales con `Player`,
  usando sólo `RacialProbe` de la cuenta técnica `racialtest`, sin cliente,
  desconectado y sin IA de combate. No es un nuevo rival PvP.
- Humano fighter: `[40,30,43,21,11,25]` en origen, Sagittarius principal,
  Tyrant sub de segunda, Spellsinger sub de segunda y recarga con mago activo.
- Cambio explícito a orco: `[40,26,47,18,12,27]`, misma principal/subs,
  persistente tras recarga. Restauración final a humano y principal.
- API del laboratorio: plantilla racial correcta y lecturas nuevas compatibles;
  lectura vieja de Hellkevin marcada histórica.
- Reinicios sin clientes conectados; último arranque sin fallos de carga.

En el primer ensayo apareció un fallo de inicialización de variables antes
de la carga completa. Se corrigió con `getVariables()` y se repitieron las
pruebas. Las posiciones de los siete pilotos se recuperaron exactamente del
respaldo previo; no se restauraron sus stats ni se anuló el efecto racial.

## Comparación corregida: mismo Storm Screamer

Nivel 80, cero subs, mismo equipo +4, dyes y veinte efectos.

| Stat final | Velith: elfa oscura | Sylira: elfa clara |
|---|---:|---:|
| M.Atk | 4727.93 | 3572.15 |
| Casting speed | 1125 | 1365 |
| P.Atk | 516.08 | 483.00 |
| P.Def | 929.35 | 929.35 |
| M.Def | 1477.03 | 1518.83 |
| Atk. speed | 422 | 426 |
| HP / CP / MP | 5191 / 1479 / 4951 | 5364 / 1528 / 5096 |
| STR / DEX / CON | 23 / 23 / 24 | 21 / 24 / 25 |
| INT / WIT / MEN | 49 / 24 / 27 | 42 / 28 / 30 |

Estos valores vienen de personajes reales, no del XML de NPC ni de un
porcentaje manual. M.Atk no equivale directamente a DPS: falta comparar
skills, resistencias, casteo, críticos y consumo en combate controlado.

## Archivos y recuperación

Core: `Player.java`, `PlayerStat.java`. Scripts: `AdminBuildLab.java`,
`LabTelemetry.java`, `RacialProfileVerification.java`. Panel:
`lab-panel/server.js`, `lab-panel/public/app.js`.

Respaldo local: `E:\l2-local\backups\fixed-racial-profile-2026-10-08`:
jar anterior, fuentes anteriores y dump SQL completo previo. No publicar
ese dump ni credenciales. Para volver al core anterior detener sólo el
game server sin clientes y recuperar el jar anterior; no restaurar toda
la base encima de progreso nuevo. La columna/variables agregadas pueden
permanecer, pero las capturas deben volver a versionarse acorde al core.
