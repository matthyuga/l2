# Noctis y observacion PvP, fase 1

2026-10-09. Activo, verificado tras reinicio seguro. Mejora de los pilotos `.ia`, no de la secuencia de19 `.arena`.
No se cambian stats, equipo, buffs de base, raza ni build.

## Cambios de conducta

- Summons contados antes de las decisiones de cura, incluso si ya murieron.
- Maximo dos solicitudes de invocacion aceptadas por duelo, incluida la inicial.
  Un casteo interrumpido consume ese presupuesto; no hay reintentos ilimitados.
- No invoca otro summon durante el casteo pendiente ni con HP<=60% en combate.
- Apaga Arcane Power antes de curarse si su HP/MP cruzan los umbrales vigentes.
  Apagar un toggle sigue la misma retirada de efecto que Player.useMagic:
  una solicitud false del motor al apagarlo no se trata como rechazo.
- Curacion no urgente espaciada cuatro segundos; emergencia HP<25% sin esa pausa.
- Si no esta en emergencia, permite silence/root de corto alcance antes de cura.
- Llama al summon cuando necesita cura y esta fuera de rango o linea de vision.
  Suspende su ataque mientras regresa; no lo cura a distancia artificialmente.

## Observacion de ambos jugadores

Nueva tabla `lab_duel_observations`, vinculada a `lab_ai_runs.run_id`.
Cada500ms: ambos Players y sus summons, HP/CP/MP y maximos, coordenadas,
target, casteo, muerte, silencio/root/stun y cubics de Player.
Ademas registra baseline y aparicion/desaparicion de efectos con
skill_id:nivel:effector_id, y presencia/ausencia de entidades.
Sin captura fuera de las pruebas `.ia`; no modifica al jugador observado.
Cola limitada4096, escritura asincrona por lotes; perdidas se avisan en log.

Reporte read-only:

`tools\node-portable\node.exe lab-panel\scripts\duel-report.js [run_id]`

Sin numero toma la ultima prueba manual. Devuelve JSON con resultado,
duracion, decisiones, casteos/dano existentes, recursos observados y cambios
de efectos. Todavia no hay vista nueva en el panel.

## Limites honestos

No cubre cada aspecto del juego. Es la primera fase del analisis PvP.
Un efecto observado demuestra que estuvo presente, pero un efecto ausente
no demuestra resistencia. Una desaparicion NO se etiqueta automaticamente
como Cancellation: puede ser expiracion, muerte o retirada voluntaria.
Muestreo500ms puede perder efectos breves/reaplicaciones identicas.
Eventos de curacion exacta, consumo de items del jugador, duracion exacta de
controles, buff cancelado y motivo de resistencia requieren hooks del motor
en una fase posterior. No se inventa historial de duelos viejos.

## Pruebas

Java compila contra GameServer actual, preservando personalizacion racial.
PASS108 checks nuevos (invocaciones pendientes, presupuesto y curas) +335
checks anteriores. Prueba aislada opt-in AI_SMOKE comprueba acciones reales
y ahora genera observaciones del mago y fisico/summon en instancia privada.
Falta validar decisiones nuevas en un duelo manual de Noctis.

Integracion confirmada: AI_SMOKE SUCCESS10/10, runs10/11 SMOKE_PASS;
observaciones en run11 de ambos pilotos y Nightshade, efectos TP/totem/UD
observados en base. Reporte run11 sin error, perfiles offline tras limpieza.
Roster19/19+copias7/7PASS. No afirmar aun eficacia de decisiones PvP.

Backup: E:\l2-local\backups\noctis-observation-v2-2026-10-09.
