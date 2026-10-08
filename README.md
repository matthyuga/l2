# Laboratorio Lineage II Interlude

Repositorio de continuidad del servidor local basado en L2J Mobius Interlude.
Conserva el trabajo propio del proyecto sin publicar el cliente de Lineage II,
binarios de terceros, bases activas, credenciales, herramientas portátiles ni
perfiles locales del navegador.

## Qué contiene

- `mobius-overlay/`: archivos nuevos o modificados sobre L2J Mobius Interlude.
- `apps/lab-panel/`: panel de personajes, clases, skills, balance y telemetría.
- `apps/idea-lab/`: laboratorio local de ideas y su espacio de trabajo.
- `ops/windows/`: lanzadores y operaciones portátiles para Windows.
- `docs/`: instalación, arena, bitácora y plan de cobertura telemétrica.
- `data/telemetry/`: resultados reproducibles que no contienen cuentas ni claves.
- `research/chatgpt-notes/`: material conceptual exportado para continuidad.
- `research/external-servers/`: expedientes fechados y verificables de referencia.

## Estado registrado

Al 7 de octubre de 2026:

- 9 personajes ancla físicos;
- 89/89 perfiles limpios de clase;
- 465/465 parejas y 930/930 estados;
- 125.860 candidatos de cuatro clases;
- 155 builds reales y 620 estados;
- 30 finalistas;
- Fase 4D completa: 95 casos y 285/285 pasadas de combate controlado.
- Fase 5A: L2Nyx documentado, 360/360 pasadas de calibración de Nyx y
  progresión mágica Storm Screamer 12/12.
- Fase 5A.3: Hurricane fija frente a mejor skill, 240/240 pasadas.
- Fase 5A.6: comparación física de Humano, Elfo, Elfo oscuro, Orco y Enano,
  1.200/1.200 pasadas con posición, clase, equipo y rival controlados.

La primera ronda 5A demostró que las escalas 100%, 75%, 60% y 50% siguen siendo
demasiado severas para el objetivo de 10–20 segundos. El NPC original no fue
modificado; la próxima ronda se concentrará en 30%, 25% y 20%. En paralelo se
midió un Storm Screamer normal solo y tras añadir Mystic Muse, Archmage y
Soultaker. Nyx se conserva como rival élite independiente.
La comparación aislada mostró que Mystic Muse y Archmage no aumentan M.Atk:
la ventaja práctica aparece porque Aura Flare puede lanzarse 37 veces frente a
15 Hurricanes, aunque consume proporcionalmente más MP.
La comparación física final dejó P.Atk, velocidad, crítico, recursos y
STR/DEX/CON exactamente iguales en las cinco razas porque la clase activa
Dreadnought aporta la plantilla numérica. El catálogo pasó de 59 a 92 skills al
sumar tres Subs, sin acumulación de masteries físicas. La antigua base 5A.4 se
conserva sólo como antecedente: Arden se había cargado muerto y Final Frenzy
contaminó su P.Atk. La repetición 5A.6 también normaliza la posición frente a
Atlas para que altura y orientación no alteren la probabilidad de acierto.

## Base técnica

El overlay fue generado desde el repositorio oficial de L2J Mobius:

- upstream: `https://gitlab.com/MobiusDevelopment/L2J_Mobius.git`
- rama local: `master`
- commit base observado: `d47756357`
- distribución: `L2J_Mobius_CT_0_Interlude`

Para reconstruir el código, prepara una copia compatible de L2J Mobius y copia el
contenido de `mobius-overlay/` sobre la raíz de esa copia. No copies la carpeta
`mobius-overlay` como un nivel adicional.

## Panel de laboratorio

El panel usa Node.js y MariaDB. Después de clonar:

1. copia `apps/lab-panel/config.example.json` como `config.json`;
2. completa únicamente valores locales;
3. ejecuta `npm install` dentro de `apps/lab-panel`;
4. usa `npm run check` antes de iniciar el panel.

`config.json`, bases, logs, PID, `node_modules` y estados de ejecución se excluyen
del repositorio.

Los scripts que administran MariaDB esperan las variables locales
`L2_DB_PASSWORD` y `L2_DB_ROOT_PASSWORD`; sus valores no deben guardarse en Git.
Los archivos de `ops/windows/` están preparados para copiarse a la raíz de una
instalación local que tenga las carpetas `server`, `tools`, `run` y `logs`.

Cada envío a GitHub ejecuta una validación de sintaxis del panel. Las pruebas que
necesitan Game Server o MariaDB siguen siendo locales.

## Exclusiones deliberadas

No se versionan:

- `E:\l2`, instaladores, archivos `.cab`, `.rar`, mapas, texturas o binarios del
  cliente;
- runtimes completos de Game/Login Server;
- JDK, Node, MariaDB y herramientas descargadas;
- datos de MariaDB, cuentas, personajes, contraseñas o cookies;
- backups operativos, volcados generales, logs y capturas de diagnóstico;
- perfiles de Edge/Chrome y artefactos de compilación.

Consulta [docs/README-ES.txt](docs/README-ES.txt) para el uso local y
[docs/PLAN-COBERTURA-TELEMETRICA.md](docs/PLAN-COBERTURA-TELEMETRICA.md) para el
estado completo de telemetría.
