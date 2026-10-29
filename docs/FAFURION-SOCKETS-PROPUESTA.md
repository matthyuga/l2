# Fafurion: propuesta de sockets, gemas y engranajes

12/10/2026. Estado: diseño viable a partir del código local; no hay sockets instalados, gemas creadas, buffs nuevos ni activaciones de combate. La integración inicial se describe en FAFURION-ARMAS-INTEGRACION.md.

## Experiencia propuesta

Tres sockets por instancia de arma. Gemas o engranajes aportan atributos individuales; ciertas combinaciones habilitan una habilidad activa, una pasiva o un efecto automático sujeto a una condición. Dos Fafurion Cutter pueden tener construcciones diferentes. Enchant, gema y resonancia son progresiones distintas; insertar una gema no debería cambiar el tipo físico/mágico del arma por accidente.

Primera interfaz: un NPC artesano con ventana HTML estándar de Interlude, elección del arma, tres ranuras, información del atributo, coste, insertar y extraer. También se puede sumar un comando de consulta. Para que las ranuras aparezcan en el tooltip nativo o en una ventana nueva del cliente habrá que trabajar la interfaz del cliente: el pack actual no aporta ese soporte. El nombre y descripción de un template en DAT son comunes a todas sus copias; no sirven para mostrar sockets diferentes de cada instancia.

## Ejemplos de combinaciones

Estos valores son ejemplos de diseño, no efectos activos ni balance aprobado. Arrancar con números pequeños y medir contra las armas S actuales.

| Componente | Atributo individual de ejemplo | Combinación / condición propuesta | Poder resultante de ejemplo |
|---|---|---|---|
| Rubí de Furia | +3% P.Atk | Dos rubíes + engranaje de caza; cinco monstruos válidos derrotados | Furia breve de velocidad de ataque |
| Zafiro Arcano | +3% M.Atk | Dos zafiros + núcleo de marea; daño mágico efectivo acumulado | Habilidad de agua o buff arcano |
| Esmeralda Vital | Pequeño bonus a curación efectiva | Dos esmeraldas + núcleo de auxilio; HP real restaurado a aliados | Protección temporal al aliado o grupo |
| Engranaje de Guardia | Pequeño bonus de CP máximo | Combinación de guardia; CP real restaurado hasta un umbral | Regeneración/protección breve de CP |
| Núcleo de Duelo | Atributo menor definido por el rol | Combinación ofensiva; baja PvP válida | Escudo o buff breve, con reutilización |

Definir si el requisito dispara el efecto automáticamente, carga una habilidad para activarla manualmente o completa una misión que desbloquea el socket de forma permanente. Las tres opciones se pueden programar, pero tienen sensaciones y necesidades de persistencia distintas. Para una primera versión recomiendo bonus individual + resonancia temporal, sin conversión de arma y sin crecimiento permanente por bajas.

El agua puede ser solo estética, un modificador elemental real o una skill de agua. Nuestro core tiene `waterPower`, `waterRes` y cálculo de atributos en Formulas; usar agua no implica automáticamente aumentar P.Atk y M.Atk. Habría que definir qué ataques se benefician y probar resistencias/skills, sin asumir el sistema de piedras de otra crónica.

## Soporte real encontrado

- `mechanics/variables/ItemVariables.java`: variables por `objectId` guardadas en `item_variables`, con seguimiento de cambios y guardado asíncrono. Base posible para consultar el estado por instancia.
- `mechanics/events/holders/actor/player/OnPlayerItemEquip.java` y `OnPlayerItemUnequip.java`: ciclo de equipo; sirven para añadir y retirar bonus propios del arma.
- `OnPlayerPvPKill.java`: autor y objetivo de una baja PvP contabilizada. Para otras muertes de jugador habrá que definir si cuentan y revisar los eventos de muerte correspondientes; no todos los modos implican sumar PvP.
- `OnAttackableKill.java`: jugador, monstruo y si intervino summon. Permite definir la atribución en vez de contar indiscriminadamente a toda la party.
- `OnCreatureDamageDealt.java` y otros eventos de combate: base para disparadores por daño, con filtros y comprobación del contexto de cada evento.
- `entity/item/Weapon.java`: habilidades de equipo, por enchant y activaciones sobre crítico/magia. Las habilidades del template afectan todas las copias; un sistema por gema necesita resolver también la instancia equipada.
- `handlers/skill/effects/Heal.java`, `HealPercent`, `HealOverTime`, `CpHeal`, `CpHealPercent`, `CpHealOverTime`: calculan cantidades restauradas después de limitar sobrecuración. Ya notifican a `AmberContract.notifyHealing`. Esa llamada está acoplada a Amber y no distingue recurso ni skill: conviene extraer un observador reutilizable que incluya HP/CP, autor, receptor, cantidad y origen, manteniendo Amber funcionando.

Estas piezas permiten construirlo; no constituyen un sistema terminado de sockets.

## Reglas necesarias para que funcione bien

1. Persistir gemas por ID de instancia del arma, nunca solamente por item ID ni por personaje. Decidir si viajan con el arma al comerciar y cómo funcionan depósito, drop, destrucción, cristalización y transformación.
2. Validar en servidor propiedad, arma seleccionada, slots disponibles, materiales y coste. Consumir materiales y guardar los sockets en una operación consistente. El guardado diferido de ItemVariables, por sí solo, no garantiza atomicidad con el consumo de inventario: evitar pérdida o duplicación al caerse el proceso.
3. Añadir bonus con un origen identificable y quitarlos al desequipar, morir, cambiar arma o desconectarse según el diseño. Reconstruir correctamente al entrar al juego; nunca acumularlos por equipar repetidamente.
4. Poner cooldown y límites de acumulación. Cambiar de arma no debe reiniciar la reutilización del personaje ni permitir mantener todas las resonancias. Decidir qué buffs pueden permanecer tras desequipar.
5. Contar cantidades reales: cero por sobrecuración, nada por atacar cadáveres, nada por daño inexistente. Separar HP de CP. Definir curas propias, mascotas, pociones, curas periódicas y curas de una gema; impedir que el efecto se active recursivamente a sí mismo.
6. Filtrar bajas: monstruos relevantes por nivel/tipo y reglas explícitas para summons/party; PvP contra rivales válidos, con límite por víctima/tiempo. Definir duelos, eventos, bots y Olympiad. No usar IP como único criterio de abuso.
7. Mostrar el estado y condiciones con claridad, incluidas cargas, cooldown, requisitos pendientes y costes de extracción. No anunciar efectos que todavía no se hayan habilitado.

## Implementación sugerida

Primero un prototipo de NPC, tres gemas con atributos pequeños, guardado seguro por arma y un único disparador PvE. Verificar insertar/extraer, recargar sesión, guardar/cargar, intercambiar, equipar repetidamente y retirar bonus. Después sumar curación HP/CP y PvP, y finalmente resonancias entre componentes y cualquier UI nativa más elaborada.

Las pruebas de combate deben medir el resultado contra equipos S normales y en los escenarios de nuestro servidor, incluidas subclases acumuladas y bots. La propuesta no aumenta todavía el poder de las siete armas instaladas.
