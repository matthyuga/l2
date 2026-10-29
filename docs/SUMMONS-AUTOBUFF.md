# Buffs para summons — 10/10/2026

Instalados en Thiago, NPC Scheme Buffer50008 del Coliseo.

Invocar el summon o mascota, hablar con Thiago y pulsar `Auto Buff Summon`. Elige fisico o magico segun el summon. Tambien disponibles `Summon Fisico` y `Summon Magico` para decidir manualmente.
El `Auto Buff` del jugador conserva su deteccion por clase activa. El summon ya no hereda esa eleccion del amo.

Amber, gatos de ataque, Dark Panther y Spectral Lord reciben normalmente el perfil fisico (Might, Haste, Focus, Death Whisper, dances/songs configuradas).
Merrow y Magnus reciben magico por sus ataques; Seraphim, Feline Queen y Nightshade por su perfil de soporte.
Se examinan habilidades de dano magico contra blancos vivos y atributos BASE del template. Las explosiones que requieren cadaver no convierten a un melee en caster: Soulless y Spectral Lord quedan fisicos automaticamente; se puede elegir magico manual para usar otra estrategia.
Los buffs actuales y la clase del amo no cambian la clasificacion. Una criatura nueva usa las mismas reglas; los botones manuales cubren roles mixtos.

Se reutilizan FIGHTER_GROUP y MAGE_GROUP existentes, con los mismos niveles y duracion: SchemeBufferConfig.BufferDurationSeconds=7200 (2horas). No se retocaron presets, costes ni stats base. Aplicacion a pet sin summon o muerto devuelve un mensaje, sin aplicar al amo. Perfil invalido no concede efectos. Se actualizan estado/estadisticas del summon tras buffear.
Es un autobuff al pulsar el boton; no una renovacion permanente ni un buff gratis al invocar. Las reglas nativas de limite y superposicion de buffs siguen vigentes. La seleccion manual agrega el perfil elegido siguiendo esas reglas, sin purgar todos los efectos anteriores.

Produccion: solo `SchemeBuffer.class` en GameServer.jar y `server/game/data/html/mods/SchemeBuffer/50008.htm`. Todas las demas entradas del JAR identicas al respaldo, incluidos catalogoV3, reglas PvP, razas, IA y Amber. Cliente completo anterior sin cambios. Core fuente, menu, test y cloud sincronizados sin commit/push.

Verificacion: 231 checks PASS, doce templates por dos clases de amo. Se llama el bypass real del NPC y se verifican efectos de ataque/velocidad, aumento de stats reales, duracion, perfil independiente del propietario y de buffs ya aplicados, overrides, preset de jugador original, sin summon, perfil invalido y ausencia de cambios a skills/shortcuts/efectos del amo. Incluye AmberServitor real. Primera prueba detecto clasificacion de Spectral Lord por Corpse Kaboom; corregida excluyendo ataques a cadaveres y ampliada con Feline Queen. Segunda corrida completa PASS.
La prueba headless no sustituye la revision visual de botones dentro del cliente, pendiente del usuario. Verificador one-shot terminado, probe offline retirado, roster19/19 y servidor disponible. Arranque habitual2-JUGAR no activa pruebas.

Respaldo: `backups/summon-buffs-2026-10-10`. Fuentes/prueba/hashes/logs: `research/client-comfort/summon-buffs`; verificacion opt-in `lab.summonbuff.verify=true` solo para el laboratorio.
