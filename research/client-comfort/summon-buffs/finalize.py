from pathlib import Path
import hashlib,json,re,shutil,datetime
r=Path(__file__).resolve().parents[3];s=Path(__file__).resolve().parent
log=(r/'logs/game-stderr.log').read_text(errors='replace');m=re.search(r'SummonBuffVerification SUCCESS: (\d+) checks',log)
assert m and 'SummonBuffVerification FAILED' not in log,'Summon checks not passed'
assert 'Roster Coliseo: 19 perfiles Player preparados' in log,'Wait for roster19'
assert 'No se preparo el perfil normal' not in log
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'server/libs/GameServer.jar')==sha(s/'GameServer.jar')
old=json.loads((r/'research/client-comfort/v3/installed-hashes.json').read_text())
assert all(sha(Path(p))==h for p,h in old.items() if not p.endswith('GameServer.jar')),'Client assets changed'
proof={'at':datetime.datetime.now().isoformat(),'checks':int(m[1]),'status':'PASS','templates':12,'owner_classes':['mage','fighter'],
 'real_npc_bypass_effects_stats_duration':True,'player_buffs_unchanged':True,'previous_client_assets_unchanged':True,'roster_ready':19,
 'game_pid':int((r/'run/game.pid').read_text().strip()),'core_sha256':sha(r/'server/libs/GameServer.jar'),
 'core_changes':['SchemeBuffer.class'],'npc':'Thiago / Scheme Buffer50008','duration_seconds':7200,
 'buttons':['Auto Buff Summon','Summon Fisico','Summon Magico'],
 'mode':'one-shot summon verifier completed; no ongoing tests; regular next launcher has no summon test flag',
 'manual_review':'Pending user visual/button check in NPC menu; effects via actual NPC bypass verified headless'}
(s/'verification.json').write_text(json.dumps(proof,indent=2))
shutil.copy2(r/'logs/game-stderr.log',r/'backups/summon-buffs-2026-10-10/summon231-roster19-pass.log')
text=f'''# Buffs para summons — 10/10/2026

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

Verificacion: {proof['checks']} checks PASS, doce templates por dos clases de amo. Se llama el bypass real del NPC y se verifican efectos de ataque/velocidad, aumento de stats reales, duracion, perfil independiente del propietario y de buffs ya aplicados, overrides, preset de jugador original, sin summon, perfil invalido y ausencia de cambios a skills/shortcuts/efectos del amo. Incluye AmberServitor real. Primera prueba detecto clasificacion de Spectral Lord por Corpse Kaboom; corregida excluyendo ataques a cadaveres y ampliada con Feline Queen. Segunda corrida completa PASS.
La prueba headless no sustituye la revision visual de botones dentro del cliente, pendiente del usuario. Verificador one-shot terminado, probe offline retirado, roster19/19 y servidor disponible. Arranque habitual2-JUGAR no activa pruebas.

Respaldo: `backups/summon-buffs-2026-10-10`. Fuentes/prueba/hashes/logs: `research/client-comfort/summon-buffs`; verificacion opt-in `lab.summonbuff.verify=true` solo para el laboratorio.
'''
doc=r/'SUMMONS-AUTOBUFF.md';doc.write_text(text,encoding='utf-8')
name='29_SUMMONS_AUTOBUFF_2026-10-10.md'
for folder in ('CONTINUIDAD-W10','CONTINUIDAD-W11'):
 shutil.copy2(doc,r/folder/name);shutil.copy2(doc,r/'cloud-repo'/folder/name)
 p=r/folder/'LEER-PRIMERO.md';addition='\n## Buffs de summons — 10/10/2026\n\nVer `'+name+'`: Thiago tiene Auto Buff Summon y perfiles manuales fisico/magico. El perfil depende del summon; Amber fisica aunque el amo sea mago. '+str(proof['checks'])+' checks PASS con efectos/stats reales, duracion2horas y roster19/19. SoloSchemeBuffer.class + menuNPC; cliente/Amber conservados.\n'
 if name not in p.read_text(encoding='utf-8-sig'):p.write_text(p.read_text(encoding='utf-8-sig')+addition,encoding='utf-8')
 shutil.copy2(p,r/'cloud-repo'/folder/'LEER-PRIMERO.md')
shutil.copy2(doc,r/'cloud-repo/docs'/doc.name)
cloud=r/'cloud-repo/research/client-comfort/summon-buffs';shutil.copy2(s/'verification.json',cloud/'verification.json')
note='FINALIZADO buffs de summons. Thiago50008: Auto Buff Summon (segun skills/atributos base del SUMMON), overridesFisico/Magico; playerautobufforiginalclaseactiva. Amber fisica. Excluidas explosiones sobre cadaver para no clasificar Spectral Lord como caster. '+str(proof['checks'])+' checks PASS con12templates x amomago/guerrero, NPCbypass real, efectos/stats/duracion7200 y no cambios al amo. Core soloSchemeBuffer.class; otrasentries y cliente iguales albackup. Source/runtime/cloud sincronizados sincommit/push. Verificadorone-shotacabado, probeoffline, roster19/19, ventanaGameServerliberada. Continuidad29/SUMMONS-AUTOBUFF.md; backup summon-buffs-2026-10-10. Revisionvisual menu pendienteusuario.\n'
Path('K:/_CodexNexus/inbox/20261010-lineage2-summon-buffs.md').write_text(note,encoding='utf-8')
Path('K:/_CodexNexus/inbox/20261010-lineage2-summon-buffs-in-progress.md').write_text('FINALIZADO, ventana libre. Ver 20261010-lineage2-summon-buffs.md.\n',encoding='utf-8')
p=Path('K:/_CodexNexus/sessions/lineage2-local.md');addition='\n10/10/2026: buffs summons en Thiago: automatico segun summon y perfiles manuales. Amber fisica, buffs del amo conservados, '+str(proof['checks'])+' checks PASS, roster19/19. Continuidad29; inbox/20261010-lineage2-summon-buffs.md.\n'
if '20261010-lineage2-summon-buffs.md' not in p.read_text(encoding='utf-8-sig'):p.write_text(p.read_text(encoding='utf-8-sig')+addition,encoding='utf-8')
print(json.dumps(proof,indent=2))
