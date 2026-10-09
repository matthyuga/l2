# Cuatro slots con skills independientes

**Histórico, corregido:** el usuario aclaró que sólo tercera debe depender
de la clase activa. La regla vigente acumula segunda y mantiene tercera
activa; ver [SUBACU-SEGUNDA-Y-TERCERA-ACTIVA.md](SUBACU-SEGUNDA-Y-TERCERA-ACTIVA.md).
La exclusividad completa descrita debajo ya no es la configuración vigente.

2026-10-08. Configuración: `CumulativeSubclassSkills = False`.

Principal y tres subclases pueden alcanzar tercera profesión y nivel 80.
El slot activo carga sus propios skills guardados en `character_skills.class_index`.
Al cambiar de clase, Mobius retira los skills anteriores, carga los del nuevo
slot, aplica sus pasivos/masteries y restaura sus dyes/atajos. Se conservan la
raza y el perfil racial FIGHTER/MYSTIC del personaje. Los skills de equipo,
clan y otros sistemas comunes siguen las reglas propias de Mobius.

Esta regla es global y alcanza skills de segunda y tercera profesión. Reemplaza
la acumulación anterior: una sub guardada no aporta skills ni masteries mientras
otro slot está activo. Aprender una habilidad no la borra de su slot al cambiar.
El cambio normal de clase cancela toggles, cubics y el servitor; los efectos
externos/buffs conservan las reglas de persistencia de Mobius.

## Pilotos preparados

| Piloto | Raza/perfil fijo | Principal | Sub 1 | Sub 2 | Sub 3 |
|---|---|---|---|---|---|
| Caelan | Humano FIGHTER | Sagittarius | Adventurer | Titan | Duelist |
| Ignara | Humana MYSTIC | Archmage | Mystic Muse | Storm Screamer | Dominator |
| Aelira | Elfa MYSTIC | Mystic Muse | Archmage | Soultaker | Dominator |
| Korvash | Orco MYSTIC | Dominator | Archmage | Mystic Muse | Soultaker |
| Morvain | Humano MYSTIC | Soultaker | Storm Screamer | Mystic Muse | Dominator |
| Sylira | Elfa MYSTIC | Storm Screamer | Archmage | Mystic Muse | Dominator |
| Velith | Elfa oscura MYSTIC | Storm Screamer | Archmage | Mystic Muse | Dominator |

Todos los slots se elevan con las APIs `addSubClass`, `setActiveClass` y
`rewardSkills` del servidor. No se fijan manualmente cifras de combate.
Los dyes de cada sub se guardan por slot: físicos +STR/+DEX; mágicos +INT/+WIT,
excepto Dominator que sólo recibe el dye +WIT permitido por su clase.

El inventario/equipo +4 de la principal continúa siendo el equipo del personaje,
compartido entre slots como en Mobius. Cambiar de slot no cambia automáticamente
el arma ni la armadura: para probar las subs físicas de Caelan en pelea será
necesario equipar armas compatibles con esas clases. Las subs mágicas usan la
Arcana Mace y Arcana Robe existentes. Los buffs de referencia se aplican a la
principal al final de la preparación.

`RealHumanPilots` migra la receta v1 a `human-pilots-v2-active-slot`. Si detecta
una clase de sub editada por el usuario, se detiene en ese piloto sin sustituirla.
Un piloto conectado se omite. Un piloto guardado en una sub activa conserva su
selección en el siguiente arranque y no recibe el refresco de principal.

## Telemetría y comprobación

Las capturas nuevas llevan `rules_version=fixed-racial-active-slot-v1`.
El laboratorio deja las capturas de las reglas anteriores como históricas.
Una lectura de otro slot/clase tampoco se presenta como stats de la clase activa.
Los nueve NPC del gauntlet permanecen vinculados a sus perfiles separados,
sin añadirles subclases con esta tarea.

La verificación recorre los cuatro slots de cada piloto: nivel/clase de tercera,
raza/perfil fijo y origen de los seis atributos; skills guardados del slot
presentes con su nivel correcto y skills exclusivos de los demás slots ausentes.
Se guarda la Sub 3 activa, se recarga un Player nuevo, se verifica otra vez y
se devuelve el piloto a principal. La captura final debe coincidir con la de
la principal antes de pasar a Sub 3. Esta comprobación prueba carga y persistencia,
no daño, DPS ni IA de combate.

Resultado del arranque del 8 de octubre, 20:49–20:52: 7/7 pilotos preparados y
verificados tras recarga; 35/35 comprobaciones de slot aprobadas, sin filtración
de skills exclusivos de otros slots. Las siete referencias terminan en su
principal, nivel 80, con tres subs nivel 80 y estadísticas buffeadas iguales
antes y después del recorrido. Compilación Java y siete comprobaciones de
sintaxis del panel correctas.

Respaldo local previo: `E:\l2-local\backups\active-class-skills-2026-10-08`.
No publicar su dump SQL. Para revertir, recuperar el Player.ini anterior con
el servidor detenido y preservar cualquier progreso nuevo de la base.
