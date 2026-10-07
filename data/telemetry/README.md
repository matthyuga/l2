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
