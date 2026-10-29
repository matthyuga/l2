# Giran: defensa competitiva y Amber — 11/10/2026

Hellsing conserva Giran, conquistado por Kevin en la prueba anterior. `.giran` → Reunir escuadrones → Iniciar siege prepara la defensa del propietario actual frente a Holly, Sacred, Fury y Waves. Hellsing mantiene su escuadron con Hellkevin y sus tres pilotos. El panel muestra el objetivo de cada clan. El siege comienza solo cuando lo pedis.

## Amber

Invocar y activar **Asistencia de Amber** en Alt+K o la barra. Mientras caminas, busca blancos de combate dentro de1100 unidades del amo y conserva un limite de1200 de separacion. Prioriza agresores/apoyos/summons enemigos y oportunidades de menor defensa, menos HP o aislamiento. Usa ataques nativos continuos; si un callback llega antes de completar la preparacion del arco, programa un unico reintento al vencer ese plazo para no quedar bloqueada con ATTACK activo. No aumenta dano ni ignora alcance/visibilidad, paz, instancia o reglas PvP. Jugadores neutrales no son blancos automaticos. Ordenes manuales de seguir/detener vuelven a control manual; caminar con el amo conserva la asistencia.

Incluye guardias enemigos, cristales y puertas cerradas de un siege activo donde el amo es atacante registrado. Una puerta que ya estan golpeando otros atacantes gana prioridad. Las puertas del propio castillo y los guardianes aliados quedan protegidos. Muros que requieren armas de siege quedan excluidos. La IA nativa de summon rechazaba la puerta por pedir una ruta hasta su centro; Amber admite iniciar el ataque contra la cara visible y deja al motor nativo resolver acercamiento, arco, cadencia, shots, impacto y HP. Contra puertas usa flechas normales o de fuego; la lluvia queda para combatientes.

## Clanes que compiten

Las agendas V2 conservan rutas/objetivos por escuadron y formacion con su capitan. Comparten blancos de puerta cuando observan otros atacandola, pero cada clan compite por el castillo. Dentro del campo activo, los clanes rivales son enemigos nativos; no se amplian reglas PvP fuera del campo ni contra participantes no inscritos. Buscan agresores, enemigos cercanos en el interior y lideres que esten conquistando, con prioridad para interrumpirlos.

Kaelis, Caelan, Riven y Brunna pueden usar **Seal of Ruler246** al llegar al artefacto, protegidos por su escuadron. Son180.000ms fijos,50MP iniciales y ningun item; el casteo puede interrumpirse. No se usa una captura instantanea por script. Todos los pilotos reciben un minimo de1200 Gemstone C2131; son para Build Headquarters247, que consume300, no para el artefacto. Los lideres intentan levantar su campamento con el skill nativo al comienzo.

Si cambia el propietario durante la partida, se actualizan bandos, agendas y guardianes. El motor reconstruye las defensas y traslada atacantes segun sus reglas; los bots que quedan fuera del campo se reagrupan. Finalizar conserva el resultado de propiedad. Los pilotos reservados se recuperan a nivel80 tras morir; el humano mantiene las reglas normales de experiencia.

## Ares y Nyx

Dos guardianes persistentes de Giran, con sus modelos, stats y skills originales del laboratorio. Usan la IA nativa de Defender y protegen al propietario actual; se limpia el combate anterior al cambiar de dueno. Las fases especiales de boss aun no estan implementadas.

Si caen, el propietario puede usar **Revivir guardianes caidos** en `.giran` (`.giran revivir`). Si no lo hace, reviven tras60s en el punto nativo de la sala de resurreccion, esperan10s protegidos y vuelven caminando al combate. El boton revive en el lugar de caida. Se utiliza este panel porque la resurreccion ordinaria de jugadores/summons no revive estos NPC. No dan XP,SP ni drops. Se conservan al terminar y al reiniciar mientras exista propietario.

## Validacion

Compilacion y prueba nativa opt-in: **141 checks PASS**. Se cargo solo a los19 pilotos, sin Hellkevin. Amber redujo HP de una puerta por arco nativo sin target del amo y de un NPC de campo mientras el amo caminaba, con dos disparos consecutivos comprobados. Los cuatro lideres iniciaron el casteo nativo de conquista; se aborto antes de completar los3 minutos para conservar la propiedad. Se comprobo HP inicial restaurado de ambos guardianes, alianza, muerte, revival manual y revival en la sala. La espera de60s se acelero solo en la prueba; la fase de espera en sala fue comprobada.

Comparacion persistente: personaje completo/inventario de Hellkevin, clanes/reputacion/Blood Alliance/skills, Giran/fecha y382 registros de guardias identicos. Hellsing mantiene hasCastle=3. Cuatro clanes rivales inscritos como atacantes,19 pilotos offline nivel80. El siege de prueba termino y no queda un combate automatizado activo. No se ha medido una partida completa de defensa ni el balance de clanes/guardianes.

Core sin modificaciones en esta version: SHA256`d082689917659a814f1863f304eb0092af213d1b5b8419e7179cc7d69ddabac0`. Se conserva el pool acotado V2/heap4GB. No hay cambios de cliente. Source/dist/cloud overlay y continuidad W10/W11 actualizados localmente, sin commit/push.

Fuentes: `research/giran-siege-v3`; respaldo privado: `backups/giran-siege-v3-2026-10-11`. Flag opt-in `Start-L2Local.ps1 -VerifyGiranDefense`; arranque habitualfalse, sin iniciar pruebas ni siege. Los generadores stage.py/finish-stage.py son historicos, no recrean por si solos todas las correcciones finales; los Java finales y verification.json son la referencia. No repetir la instalacion inicial de clanes V1 ni lab.giran.install=true.
