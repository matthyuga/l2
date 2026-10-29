from pathlib import Path
import json,re,hashlib,shutil
root=Path(__file__).resolve().parents[2];stage=Path(__file__).parent
log=(root/'logs/game-stderr.log').read_text(encoding='utf-8',errors='replace')
match=re.search(r'GIRAN_V3_VERIFY PASS checks=(\d+)',log)
assert match,'Native defense verification must pass before documenting completion'
checks=int(match.group(1))
proof={'checks':checks,'native':['owned siege sides','competing attackers hostile','Amber autonomous native gate HP loss with owner target unset','Amber field NPC HP loss while owner walks, including two consecutive native arrows','four rival leaders start native Seal channel then abort','both guardians start with restored native HP','guardian ally predicate/native death/manual revival/timed room revival'],'persistent':'human/inventory,clans/reputation/blood/skills,castle owner/schedule,382guard records identical;four rival attackers registered;19pilots offline80','core_sha256':hashlib.sha256((root/'server/libs/GameServer.jar').read_bytes()).hexdigest(),'limits':['not a full competitive conquest/balance run','guardian automatic60second wait accelerated in test;10second holding phase checked','manual NPC resurrection uses owner panel, not ordinary player resurrection skill']}
(stage/'verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
shutil.copy2(root/'logs/game-stderr.log',root/'backups/giran-siege-v3-2026-10-11/native-defense-pass.log')
for pkg in ['GiranSiegeLab','AmberContract']:
 for p in (root/'server/game/data/scripts/custom'/pkg).glob('*.java'):
  for dest in [root/'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom'/pkg,root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom'/pkg]:
   dest.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest/p.name)
shutil.copy2(root/'Start-L2Local.ps1',root/'cloud-repo/ops/windows/Start-L2Local.ps1')
doc=f'''# Giran: defensa competitiva y Amber — 11/10/2026

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

Compilacion y prueba nativa opt-in: **{checks} checks PASS**. Se cargo solo a los19 pilotos, sin Hellkevin. Amber redujo HP de una puerta por arco nativo sin target del amo y de un NPC de campo mientras el amo caminaba, con dos disparos consecutivos comprobados. Los cuatro lideres iniciaron el casteo nativo de conquista; se aborto antes de completar los3 minutos para conservar la propiedad. Se comprobo HP inicial restaurado de ambos guardianes, alianza, muerte, revival manual y revival en la sala. La espera de60s se acelero solo en la prueba; la fase de espera en sala fue comprobada.

Comparacion persistente: personaje completo/inventario de Hellkevin, clanes/reputacion/Blood Alliance/skills, Giran/fecha y382 registros de guardias identicos. Hellsing mantiene hasCastle=3. Cuatro clanes rivales inscritos como atacantes,19 pilotos offline nivel80. El siege de prueba termino y no queda un combate automatizado activo. No se ha medido una partida completa de defensa ni el balance de clanes/guardianes.

Core sin modificaciones en esta version: SHA256`{proof['core_sha256']}`. Se conserva el pool acotado V2/heap4GB. No hay cambios de cliente. Source/dist/cloud overlay y continuidad W10/W11 actualizados localmente, sin commit/push.

Fuentes: `research/giran-siege-v3`; respaldo privado: `backups/giran-siege-v3-2026-10-11`. Flag opt-in `Start-L2Local.ps1 -VerifyGiranDefense`; arranque habitualfalse, sin iniciar pruebas ni siege. Los generadores stage.py/finish-stage.py son historicos, no recrean por si solos todas las correcciones finales; los Java finales y verification.json son la referencia. No repetir la instalacion inicial de clanes V1 ni lab.giran.install=true.
'''
(root/'GIRAN-DEFENSA-AMBER-V3.md').write_text(doc,encoding='utf-8')
shutil.copy2(root/'GIRAN-DEFENSA-AMBER-V3.md',root/'cloud-repo/docs/GIRAN-DEFENSA-AMBER-V3.md')
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
 shutil.copy2(root/'GIRAN-DEFENSA-AMBER-V3.md',root/folder/'34_GIRAN_DEFENSA_AMBER_V3_2026-10-11.md')
 p=root/folder/'LEER-PRIMERO.md';s=p.read_text(encoding='utf-8');line='\n11/10 Giran V3: ver34_GIRAN_DEFENSA_AMBER_V3_2026-10-11.md. Hellsing ahora propietario; cuatro clanes rivales pueden conquistar y pelear entre ellos, Amber puertas/farm, guardianes aliados/revivir/sala. Prueba nativa y estado persistente PASS.\n';p.write_text(s+line,encoding='utf-8')
cloudstage=root/'cloud-repo/research/giran-siege-v3';cloudstage.mkdir(parents=True,exist_ok=True)
for p in stage.rglob('*'):
 if p.is_file() and p.suffix in {'.java','.json','.js','.ps1','.py'} and 'classes' not in p.parts:
  dest=cloudstage/p.relative_to(stage);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
nexus=Path('K:/_CodexNexus');note=f'''# Giran V3 completado — 11/10/2026
Proyecto real E:\\l2-local. Hellsing conserva Giran conquistado por Kevin. Amber con Asistencia activada busca perimetro1100 al caminar, blancos aislados/vulnerables y puertas enemigas en siege; corregida validacion SummonAI que exigia ruta al centro de puerta cerrada. Ataques/dano nativos.
`.giran` reunir/iniciar ahora admite propietario: cuatro clanes rivales compiten, lideres castean246nativo3min/50MP/sinitem, Gemstone C minimo1200 paraHQ247(300). Guardianes Ares/Nyx Defenders aliados al propietario actual, revival panelmanual o60s sala+10s espera. IA especial bosses/balance pendientes.
Compilacion y prueba nativa {checks}checks PASS; estado persistente humano/clanes/castillo intacto, solo4registrosatacantes nuevos.19pilotosoffline80. Core V2 d082 sin cambios; cliente intacto. Fuentes/cloud espejados local sin commit/push. Continuidad34W10/W11 y GIRAN-DEFENSA-AMBER-V3.md; backups/giran-siege-v3-2026-10-11. Flagsverificacionopt-in, siege solo a pedido. GameServer libre para siguiente sesion cuando se avise al usuario que ya puede entrar.
'''
(nexus/'inbox/20261011-giran-v3.md').write_text(note,encoding='utf-8')
(nexus/'inbox/20261011-giran-v3-in-progress.md').write_text('COMPLETADO. Ver20261011-giran-v3.md; no hay bloqueo de trabajo activo de esta sesion.\n',encoding='utf-8')
p=nexus/'sessions/lineage2-local.md';p.write_text(p.read_text(encoding='utf-8')+f'\n11/10 Giran V3: Amber puertas/perimetro, defensa competitiva4clanes/lideres246, guardianes actuales aliados/revival. {checks}checks nativosPASS; humano/propiedadHellconservados. Verinbox/20261011-giran-v3.md y continuidad34.\n',encoding='utf-8')
print('Final docs, source/cloud, portable continuity and Nexus updated; no commit/push.')
