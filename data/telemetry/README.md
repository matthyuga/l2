# Datos telemétricos publicados

`phase4d-results-final.sql` contiene únicamente el plan de benchmarks y las 285
pasadas finales de la Fase 4D. No incluye cuentas, contraseñas, tablas generales de
personajes ni la base activa del servidor.

Motor registrado: `CORE_ACCELERATED`. Usa objetos, clases, equipo, skills y fórmulas
del núcleo con reloj acelerado; no representa latencia, movimiento ni decisiones
humanas de una pelea PvP completa.

## Fase 5A.2 — progresión mágica

`phase5a2-magic-progression.sql` conserva 12 pasadas: tres repeticiones de un
Storm Screamer puro y tres tras cada incorporación acumulativa de Mystic Muse,
Archmage y Soultaker. Storm Screamer permanece activa en las cuatro etapas. El
protocolo usa nivel 80, Atlas, Arcana Mace +0, robe S, joyería S común, Blessed
Spiritshots y ningún buff externo.

El resumen agregado está en `phase5a2-magic-progression-summary.json`. Las dos
primeras Subs no cambiaron M.Atk ni casteo; Soultaker aumentó M.Atk 2,77%. Mystic
Muse cambió la mejor rotación de Hurricane a Aura Flare y casi duplicó el DPS del
protocolo. Nyx Élite no fue modificada y permanece como referencia separada.

## Fase 5A.3 — skill fija frente a mejor catálogo

`phase5a3-magic-comparison.sql` contiene 240 pasadas: cuatro etapas, dos
carriles y treinta repeticiones. El carril fijo usa Hurricane; el práctico elige
el mejor nuke disponible. `phase5a3-magic-comparison-summary.json` conserva los
promedios, dispersión, cadencia, daño por cast, críticos y MP.

Mystic Muse y Archmage no aumentaron M.Atk. Aura Flare produjo 88,67–95,17% más
DPS que Hurricane fija porque ejecutó 37 casteos frente a 15, a cambio de usar
2.553 MP frente a 1.035. Soultaker elevó M.Atk 2,77%, equivalente a cerca de
1,38% de daño teórico por la fórmula de raíz cuadrada.

## Fase 5A.4 — primera base racial física

> Registro histórico sustituido por 5A.6. Arden se cargó con 0 HP y Final
> Frenzy elevó el P.Atk de 877,98 a 1.007,28. No debe usarse como referencia de
> balance ni compararse numéricamente con la captura corregida.

`phase5a4-human-physical-baseline.sql` contiene 240 pasadas sobre Arden, Human
Fighter de nacimiento: cuatro etapas, dos carriles y treinta repeticiones. La
clase activa es Dreadnought y se añaden acumulativamente Titan, Fortune Seeker y
Maestro. El protocolo fija nivel 80, Atlas, Saint Spear +0, heavy S, joyería S
común, Soulshots y ningún buff externo.

`phase5a4-human-physical-baseline-summary.json` conserva el protocolo, auditoría,
atributos y agregados. Las 240 filas mantuvieron `race_id=0` y `HUMAN`. P.Atk
(1.007,28), velocidad (351), crítico (86), STR/DEX/CON (42/28/43) y recursos no
cambiaron al sumar Subs; el catálogo creció de 59 a 92 skills. Earthquake fue la
skill compatible elegida por potencia/ciclo, pero sus dos acciones por minuto no
superan las 42 acciones del autoataque. Esta medición es la referencia humana;
el efecto racial se aislará al replicarla sin cambiar ninguna otra variable.

## Fase 5A.6 — comparación física de las cinco razas

`phase5a6-five-race-physical-comparison.sql` contiene 1.200 pasadas: cinco
razas, cuatro etapas acumulativas, dos carriles y treinta repeticiones por
combinación. `phase5a6-five-race-physical-comparison-summary.json` conserva el
protocolo, auditoría, diagnósticos y agregados por raza.

La captura corrige dos contaminantes descubiertos durante la ampliación: revive
el anclaje antes de limpiar HP/efectos y coloca temporalmente a todos los
personajes en la misma posición respecto de Atlas. Esto evita que Final Frenzy o
las bonificaciones de altura/lado de la fórmula de acierto parezcan diferencias
raciales.

Humano, Elfo, Elfo oscuro, Orco y Enano dieron exactamente 877,9798 P.Atk, 351
de velocidad, 86 de crítico, 123 de precisión, 42/28/43 STR/DEX/CON y los mismos
recursos. Polearm Mastery aportó 129,3 P.Atk por igual a todos. El autoataque
promedió 43,79–44,71 DPS por raza, una dispersión pequeña dentro de desviaciones
de 4,62–4,74; no hay evidencia de un coeficiente racial de daño. En la
arquitectura actual la raza persistida conserva identidad/apariencia y la clase
activa aporta la plantilla numérica.
