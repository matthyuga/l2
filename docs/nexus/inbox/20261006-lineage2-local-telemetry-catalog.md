# Lineage II local: catálogo telemétrico

- Fecha: 2026-10-06.
- Ruta real: `E:\l2-local`.
- Cliente: `E:\l2`.
- Estado: servidor Interlude local y panel de laboratorio activos.
- Cambio: `LabTelemetry` ahora conserva perfiles separados por raza principal,
  clase activa, ranura Principal/Sub 1-3, build completa, nivel, equipo y efectos.
- Interfaz: el panel muestra el “Catálogo vivo” dentro de Telemetría.
- Regla de diseño: cambiar Principal/Sub conserva la raza de la principal; cambiar
  raza es una acción separada de `//buildlab` y será un servicio pagado al publicar.
- Documento local: `E:\l2-local\BITACORA_LABS_PORTATILES_2026-10-06.md`.
- Reglas añadidas: Guts/Frenzy se reemplazan; Zealot convive; siete tótems funcionan
  con cualquier arma y solamente uno queda activo; Overlord puede elegirse como Sub
  directo; las masteries pasivas con el mismo nombre conservan sólo el nivel mayor.
- Despliegue: `GameServer.jar` recompilado, instalado y validado con Login, Game,
  MariaDB y panel activos.
- Fase 2 completa: 89/89 perfiles limpios obtenidos de objetos `Player` reales a
  nivel 80; no se fabricaron estadísticas por SQL.
- Cobertura base definida: 89 estados (9 iniciales, 18 primeras, 31 segundas y 31
  terceras). Cinco razas requieren nueve anclas por las raíces guerrero/místico.
- Panel: mapa de cobertura limpia por etapa, raza y raíz; estado final 89/89.
- Criterio: nivel 80, principal activa, sin Subs, equipo ni efectos. Los efectos ahora
  forman parte de la clave del perfil y no sobrescriben la muestra limpia.
- Plan local: `E:\l2-local\PLAN-COBERTURA-TELEMETRICA.md`.
- Fase 1 completa: nueve personajes físicos creados en `telemetryf` y `telemetrym`,
  uno por cada raíz inicial, todos nivel 1 y Master/GM. Validación: 9 personajes,
  9 classId iniciales, 5 razas y cero duplicados tras un segundo reinicio.
- Respaldo previo: `E:\l2-local\backups\telemetry-anchors-2026-10-06\before.sql`.
- Auditoría de fase 2: 89 clases únicas, cero duplicados y cero perfiles sin skills;
  etapas 9/18/31/31 y razas 29/20/20/13/7. Los nueve anclajes quedaron offline,
  nivel 1, clase inicial, sin equipo ni subclases.
- El recorrido automático bloquea eventos de profesión intermedios y es idempotente:
  con cobertura completa no vuelve a modificar personajes tras un reinicio.
- Respaldo de fase 2: `E:\l2-local\backups\telemetry-phase2-2026-10-06\before.sql`.
- Fase 3 completa: 465/465 parejas de terceras profesiones y 930/930 estados reales
  (cada pareja con A principal activa y B en Sub 1 activa), a nivel 80, sin equipo
  ni efectos.
- Auditoría de fase 3: las 31 profesiones tienen 30 compañeras, cero discrepancias
  de skills, cero asimetrías entre los dos estados, rango de 49 a 138 skills y
  promedio de 105,07. IDs compartidos: 6 a 59; colisiones de mastery: 2 a 7.
- Corrección de núcleo: después del autolearn se restaura la acumulación completa;
  skills compartidas conservan el nivel mayor y las masteries del mismo nombre usan
  como desempate determinista el ID menor. `GameServer.jar` fue recompilado y
  desplegado.
- Panel: nueva matriz consultable de parejas y seguimiento de Fase 3. Ejemplos:
  `Cardinal + Dominator` suma 138 skills; `Duelist + Dreadnought` comparte 41 IDs y
  presenta 7 colisiones de mastery.
- Reinicio de control idempotente: las 930 filas conservaron exactamente su firma y
  el recolector no modificó el plantel. Los nueve anclajes permanecen offline, nivel
  1, en su clase inicial, sin subclases ni equipo.
- Respaldo de fase 3: `E:\l2-local\backups\telemetry-phase3-2026-10-06`.
- Siguiente fase: seleccionar una muestra dirigida de builds de cuatro clases usando
  la matriz de parejas; no recorrer por fuerza bruta los 125.860 conjuntos.
- Fase 4A completa el 7 de octubre de 2026: `lab_four_class_candidates` contiene
  125.860/125.860 builds, 4.060 por principal y 31.465 conjuntos únicos de skills.
- Generación teórica sin tocar personajes: combina los `skill_key` validados de la
  Fase 3 con metadatos XML y normaliza IDs/niveles y masteries determinísticamente.
- Rango previsto: 88–231 skills; promedio 176,42. Máxima amplitud: `Soultaker +
  Cardinal + Wind Rider + Dominator`, 231 skills.
- Muestra dirigida: 155 builds, cinco por cada una de las 31 principales y 31 por
  criterio (`amplitud`, `afinidad`, `estrés`, `híbrida`, `cobertura`). Todas las
  profesiones aparecen al menos 13 veces.
- Auditoría: cero clases repetidas, cero desórdenes de Subs, cero hashes incorrectos.
  Segunda ejecución idempotente con firma idéntica.
- Panel: nueva sección Fase 4A y API `/api/telemetry/build-candidates`.
- Generador: `E:\l2-local\lab-panel\scripts\generate-phase4a.js`.
- Respaldo: `E:\l2-local\backups\telemetry-phase4a-2026-10-07`.
- Siguiente paso: Fase 4B, medir las 155 builds reales en cuatro clases activas
  (620 estados a nivel 80, sin equipo ni efectos).
- Fase 4B completa el 7 de octubre de 2026: 155/155 builds y 620/620 estados reales,
  cinco builds por cada una de las 31 principales.
- Ejecución: nueve anclas por raíz racial natural; cada build añade tres Subs reales
  y mide Principal/Sub 1/Sub 2/Sub 3 a nivel 80, sin equipo ni efectos.
- Auditoría: cero fallos, diferencias de conteo/hash/`ID:nivel`, builds incompletas,
  ranuras incorrectas, perfiles no seleccionados o cambios de raza.
- Distribución: 31 builds y 124 estados por criterio (`amplitud`, `afinidad`,
  `estrés`, `híbrida`, `cobertura`). Rango 93–231 skills; promedio 176,91.
- Tabla: `lab_four_class_profiles`. El panel muestra 155/155 y 620/620, además de
  los cuatro estados reales dentro de cada candidato.
- Las nueve anclas fueron restauradas offline, nivel 1, clase inicial, sin Subs ni
  equipo.
- Reinicio idempotente: firma de las 620 filas idéntica y roster sin modificaciones.
- Respaldo: `E:\l2-local\backups\telemetry-phase4b-2026-10-07`.
- Corrección del plan: la Fase 4 no terminaba en 4B. Fase 4C selecciona finalistas
  y Fase 4D realiza combate controlado; el contraste externo queda para Fase 5.
- Fase 4C completa el 7 de octubre de 2026: 30 finalistas, cinco por categoría
  (`física`, `mágica`, `tanque`, `soporte`, `summoner`, `híbrida`).
- Tipos: 12 de rendimiento, seis de amplitud, seis de estrés y seis de control.
- Cobertura: las 31 terceras profesiones, 30 grupos no ordenados únicos y 24
  principales; ninguna principal se usa más de dos veces.
- Fuente: 620 estados reales comparados con sus perfiles limpios mediante razones
  logarítmicas y medias geométricas. Son índices de selección, no poder de combate.
- Auditoría: cuatro perfiles válidos por finalista, cero hashes distintos y firma
  idempotente `ec026f090be9db3da777412d4721e2c6`.
- Tabla/script: `lab_build_finalists` y
  `E:\l2-local\lab-panel\scripts\analyze-phase4c.js` (`npm run phase4c`).
- Panel: API `/api/telemetry/finalists`, tabla 30/30 y seguimiento con 4D pendiente.
- Respaldo: `E:\l2-local\backups\telemetry-phase4c-2026-10-07`.
- Siguiente etapa: Fase 4D, combate controlado; Fase 5 después.
- Fase 4D preparada el 7 de octubre de 2026: `lab_combat_benchmark_plan` contiene
  95 casos y 285 pasadas previstas (tres repeticiones), todavía 0 completadas.
- Distribución: 15 salidas físicas, 10 mágicas, cinco de soporte, cinco de
  invocación y 30 resistencias contra cada uno de Ares y Nyx.
- Contexto fijado: armadura S natural, arma compatible por clase, Tateossian,
  enchant +0 y sin buffs externos. Manifiesto: `lab-panel\phase4d-kits.json`.
- Atlas (`NPC 900202`) añadido como blanco neutral inmóvil e inmortal con 1.000
  P. Def/M. Def; Ares y Nyx quedan para supervivencia.
- Panel: `/api/telemetry/benchmarks`, 95 casos y progreso 0/285.
- Firma idempotente: `be540784830299badeae72a3b735cd5ea2651c853c4308fa41b99fbff78f7304`.
- Game Server reiniciado sin jugadores conectados; todos los servicios activos y
  los nueve anclajes restaurados. Respaldo: `backups\telemetry-phase4d-2026-10-07`.
- Próximo bloque: instrumentar y ejecutar las pasadas reales; Fase 4D sigue en curso.

## Actualización 2026-10-07 — Fase 4D completada

- Ejecutor automático, incremental y reanudable incorporado en `LabTelemetry.java`.
- Resultado: 95/95 casos y 285/285 pasadas `CORE_ACCELERATED`, exactamente tres
  repeticiones por caso y cero métricas obligatorias inválidas.
- El motor usa `Player`, builds, equipo S +0, skills, stats, fórmulas y efectos
  reales; el reloj es acelerado y no reproduce latencia, movimiento ni decisiones
  humanas.
- Promedios: 103,56 DPS físico, 67,75 DPS mágico, 119,22 DPS de invocación,
  407,94 HPS; supervivencia 26,79 s contra Ares y 3,22 s contra Nyx.
- Nyx queda marcado para calibración antes de decisiones finas de balance.
- Panel actualizado con resultados medios por protocolo y progreso 285/285.
- Los nueve anclajes quedaron offline, nivel 1, clase inicial, sin Subs y con cero
  objetos. Se respaldaron y retiraron 14 objetos temporales de pilotos interrumpidos.
- Volcado final: `E:\l2-local\backups\telemetry-phase4d-2026-10-07\phase4d-results-final.sql`.
- Documentación actualizada: `PLAN-COBERTURA-TELEMETRICA.md` y
  `BITACORA_LABS_PORTATILES_2026-10-06.md`.
- Fase 4 cerrada. Siguiente etapa prevista: Fase 5, comparación documentada con
  otros servidores, sin aplicar buffs/nerfs directamente desde estos picos.
