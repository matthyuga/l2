# Roster de 39 bots

11/10/2026. Se añaden los veinte perfiles aprobados; se conservan los diecinueve anteriores.

Cada incorporación tiene un Player técnico persistente `ArenaNombre`, nivel 80,
principal y tres subs en tercera profesión. Rige segunda acumulativa y tercera
sólo de la clase activa, con verificación de skills en los cuatro slots y tras
recarga. Raza y perfil de origen se mantienen al cambiar de slot.

El listado usa nombres de segunda profesión para reconocer las builds:

| Nº arena | Nombre | Raza | Principal | Sub 1 | Sub 2 | Sub 3 |
|---|---|---|---|---|---|---|
| 20 | Darion | Humano | Gladiator | Tyrant | Destroyer | Warcryer |
| 21 | Valerian | Humano | Paladin | Bishop | Sword Singer | Warcryer |
| 22 | Malrik | Humano | Dark Avenger | Phantom Summoner | Tyrant | Warcryer |
| 23 | Lucien | Humano | Warlock | Bishop | Shillien Knight | Prophet |
| 24 | Seraphine | Humana | Prophet | Bishop | Elven Elder | Overlord |
| 25 | Darius | Humano | Warlord | Destroyer | Sword Singer | Warcryer |
| 26 | Thalion | Elfo | Temple Knight | Elven Elder | Sword Singer | Warcryer |
| 27 | Elowen | Elfa | Sword Singer | Bishop | Temple Knight | Warcryer |
| 28 | Faelith | Elfa | Elemental Summoner | Bishop | Shillien Knight | Prophet |
| 29 | Nerys | Elfa | Elven Elder | Bishop | Overlord | Temple Knight |
| 30 | Draven | Elfo oscuro | Shillien Knight | Phantom Summoner | Bishop | Warcryer |
| 31 | Nysera | Elfa oscura | Bladedancer | Tyrant | Destroyer | Warcryer |
| 32 | Veyron | Elfo oscuro | Phantom Ranger | Tyrant | Destroyer | Warcryer |
| 33 | Zareth | Elfo oscuro | Phantom Summoner | Bishop | Shillien Knight | Overlord |
| 34 | Saevra | Elfa oscura | Shillien Elder | Bishop | Overlord | Temple Knight |
| 35 | Rhogar | Orco | Tyrant | Destroyer | Shillien Knight | Warcryer |
| 36 | Mazhura | Orca | Warcryer | Bishop | Sword Singer | Overlord |
| 37 | Urkan | Orco | Gladiator | Tyrant | Destroyer | Warcryer |
| 38 | Dagna | Enana | Bounty Hunter | Tyrant | Destroyer | Warcryer |
| 39 | Borin | Enano | Paladin | Bishop | Sword Singer | Warcryer |

## Equipo y acceso

Armas adecuadas a la principal: duales, espada/escudo, maza mágica con Acumen,
Heaven’s Divider con Focus, arco con Focus, puños o martillo. Armadura S heavy para espadas,
duales, espada de dos manos y Bounty Hunter; light para arquero/Tyrant; robe para mystics.
Armas, armaduras, escudos y joyas +4. Buffs físicos o mágicos y dyes legales;
los supports Seraphine/Nerys/Saevra/Mazhura reciben WIT, sin INT restringido.
Los equipos no se sustituyen automáticamente al activar una subclase.

`.arena lista` enumera 39; `.arena probar Darion` o `.arena probar 20`
selecciona uno. `.arena iniciar` / `.arena repetir` recorren los 39.
Los NPC 901119–901138 aparecen sólo durante el duelo y se retiran al finalizar
o cancelar. El panel Rivales del Coliseo incluye las nuevas fichas y subs.

## Alcance de IA

Esta etapa implementa identidad, builds, equipo, persistencia, selección y
telemetría. Los nuevos NPC usan ataque básico del motor (arquero para Veyron).
No se han implementado sus rotaciones, summons, curas, controles ni estrategias.
Los roles tácticos de la propuesta quedan para el siguiente trabajo de IA.
Los grupos fijos de `.agite`, Giran y la sala Elven conservan su composición.

## Respaldo y verificación

Respaldo privado: `backups/roster-39-2026-10-11`, SQL previo y archivos anteriores.
Código sincronizado en runtime, source y overlay local; sin commit/push automático.

Comprobaciones read-only:

- `tools/node-portable/node.exe lab-panel/scripts/verify-arena-roster.js`
- `tools/node-portable/node.exe lab-panel/scripts/verify-new-roster-39.js`

La autoprueba opt-in `Start-L2Local.ps1 -VerifyArenaSpawns` verifica los 39 NPC
bajo demanda, cancelación, transición entre rondas, derrota y desconexión.
El arranque normal no activa esta prueba.

Resultado de activación: roster 39/39 preparado; 312 verificaciones de slots
y 39 recargas completas. Selector: 117 casos válidos y 6 inválidos PASS.
XML validado contra npcs.xsd y scripts Java compilados contra el core instalado.
`verify-new-roster-39.js`: 20/20 PASS para persistencia, sexo, origen racial,
nivel, principal, equipo/joyas +4 y estado offline.
`verify-arena-roster.js`: 39/39 PASS, nueve stats NPC=Player y copias anteriores
7/7 conservadas. `ArenaSpawnVerification SUCCESS`: 123 comprobaciones, los
39 rivales bajo demanda, cancelación, victoria, ronda siguiente, derrota y
desconexión. Prueba de una sola ejecución terminada; el servidor queda libre.
La conducta táctica y su eficacia PvP siguen pendientes por pedido del usuario.

Ajuste PvP 11/10: Darius usa Heaven’s Divider Focus +4 (6607), en lugar de Saint Spear. Arden/Darius tienen ataques SWORD/SWORD en sus copias NPC, sin ataque POLE.
