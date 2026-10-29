from pathlib import Path
import hashlib,json,re,shutil,struct
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent;b=r/'backups/giran-siege-2026-10-10'
log=(r/'logs/game-stderr.log').read_text(errors='replace')
m=re.search(r'GIRAN_VERIFY PASS checks=(\d+)',log)
assert m and 'GIRAN_VERIFY FAILED' not in log and 'GIRAN_ROSTER INSTALL FAILED' not in log
assert 'Roster Coliseo: 19 perfiles Player preparados' in log
before=json.loads((b/'before.json').read_text());after=json.loads((b/'after.json').read_text())
assert all(row in after['clans'] for row in before['clans']), 'Original clans changed'
assert before['skills']==after['skills'] and before['castle']==after['castle'] and before['guards']==after['guards']
new={row['clan_name']:row for row in after['clans'] if row['clan_name'] in ('Fury','Waves')}
assert len(after['clans'])==5 and set(new)=={'Fury','Waves'}
for row in new.values():assert row['clan_level']==5 and row['hasCastle']==0 and row['crest_id']>12 and row['ally_crest_id']>12
mapping={name:new[clan]['clan_id'] for clan,names in {'Fury':['Riven','Eryndor','Korvash','Aelira'],'Waves':['Brunna','Lethiel','Sylira','Velith']}.items() for name in names}
assert len(after['members'])==len(before['members'])
for old,cur in zip(before['members'],after['members']):
 expected=dict(old)
 if old['char_name'].startswith('Arena') and old['char_name'][5:] in mapping:expected['clanid']=mapping[old['char_name'][5:]]
 assert expected==cur, f'Unexpected character change {old["char_name"]}: {expected} != {cur}'
assert len(after['siege'])==5 and all(row['type']==1 and row['castle_owner']==0 for row in after['siege'])
assert {row['clan_id'] for row in after['siege']}=={row['clan_id'] for row in after['clans']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'server/libs/GameServer.jar')=='0c8c6655b8aae903d98f733815619813c4977c750e5c6126d44674027ad5aea6'
client=json.loads((r/'research/client-comfort/v3/installed-hashes.json').read_text())
assert all(sha(Path(p))==h for p,h in client.items() if not p.endswith('GameServer.jar'))
assert sha(r/'server/game/data/geodata/23_22.l2j')=='aedaa9a4e2bc1b82957ca5610109c550930ecdf18bcb80f1f1064aeb26b1fa46'
assert 'GeoEngine: Loaded 3 regions.' in log
for folder in ('source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game'):
 for sub in ('data/scripts/custom/GiranSiegeLab','data/lab/giran'):
  for src in (r/'server/game'/sub).iterdir():
   if src.suffix not in ('.java','.dds'):continue
   dest=r/folder/sub/src.name;assert not dest.exists() or dest.read_bytes()==src.read_bytes(),'Concurrent mirror edit';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 src=r/'server/game/data/stats/npcs/custom/giran_lab_guardians.xml';dest=r/folder/'data/stats/npcs/custom'/src.name;assert not dest.exists() or dest.read_bytes()==src.read_bytes();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 src=r/'server/game/data/geodata/23_22.l2j';dest=r/folder/'data/geodata'/src.name;assert not dest.exists() or dest.read_bytes()==src.read_bytes();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
shutil.copy2(r/'logs/game-stderr.log',b/'game-pass.log')
proof={'status':'PASS','checks':int(m[1]),'clans':5,'participants':20,'reserved_pilots':19,'party_size':4,'guard_positions':382,'boss_npc_ids':[903200,903201],'original_clans_and_castle_unchanged':True,'core_client_unchanged':True,'siege_started':False,'combat_pathfinding_balance':'pending user trial','pid':int((r/'run/game.pid').read_text())}
(s/'verification.json').write_text(json.dumps(proof,indent=2))
doc='''# Giran: prueba de asedio — 10/10/2026

Abrir `.giran` (tambien `.siegegiran`) con Hellkevin GM, lider de Hellsing. No requiere cliente modificado. Preparacion gratuita del laboratorio. Castillos restantes y combates `.arena`, `.ia`, `.agite` conservan su modulo; no pueden usar simultaneamente los mismos pilotos.

## Equipos

Todos atacantes, cuatro miembros por escuadron: Hellkevin y los diecinueve perfiles Player reales reservados del laboratorio, nivel80, main y tres subclases, equipo +4 y habilidades existentes.

| Clan | Lider | Otros integrantes |
|---|---|---|
| Hellsing | Hellkevin | Vaelkor, Noctis, Selene |
| Holly | Kaelis | Gorvak, Myrentha, Ignara |
| Sacred | Caelan | Arden, Zhurak, Morvain |
| Fury | Riven | Eryndor, Korvash, Aelira |
| Waves | Brunna | Lethiel, Sylira, Velith |

Fury y Waves creados a nivel5, cada uno con alianza propia del mismo nombre y crest de clan/alianza tomada de los originales crest-ally-fury.bmp y crest-ally-waves.jpg. DDS DXT1 con clan16x16/alianza8x16, doce filas visibles y cuatro de relleno. No vuelve el error de dimensiones12 no potencia de2. Los tres clanes anteriores conservan nivel, lider, alianza, emblemas, reputacion y skills. No se entregaron nuevas skills de clan/hero.

## Prueba

1. Esperar roster19/19; finalizar otros eventos, salir de party y combate. Desactivar invulnerabilidad GM. El castillo debe continuar sin propietario y sin otro siege activo.
2. `.giran` → Reunir escuadrones: crea cinco parties nativas, lleva a todos al campamento frente a Giran, prepara buffs/consumibles de los pilotos. No inicia el asedio; hay diez minutos para comenzar.
3. Iniciar siege: activa el motor nativo, puertas, tres torres de control, dos de fuego y guardias. Duracion120min. Aparecen Ares y Nyx una sola vez, dentro del castillo.
4. Seguir y asistir: los diecinueve siguen a Hellkevin y asisten su target de guardia, boss, torre o puerta. Asalto automatico: seleccionan esos blancos cercanos dentro de1600unidades; sin blanco siguen al jugador. Avanzar por las puertas con el grupo; no hay teletransporte a traves de puertas ni ruta estrategica de asedio automatica.
5. Retirada devuelve pilotos al campamento. Finalizar detiene el siege iniciado por este panel, desinvoca summons de los pilotos, desmonta parties, retira bosses y devuelve personajes a su posicion original. Cancelar antes de iniciar solo retira la preparacion.

Los pilotos usan skills/items y daño nativos, asistencia/heal/resurreccion por party, summons, shots y potas; no atacan players, mascotas, comerciantes ni el artefacto. El autoataque fisico mantiene la intencion del motor. Los muertos aceptan resurreccion; en esta prueba vuelven al campamento tras30s si nadie los resucita. Hellkevin conserva muerte/resurreccion normales. Los buffs de pilotos se reinician para la prueba y sus consumibles pueden consumirse normalmente; no se reemplazan equipo, main ni subclases.

La conquista la decide el motor: Hellkevin como lider usa Seal of Ruler (246) sobre el artefacto, a menos200unidades y altura valida. Los otros lideres tienen la skill nativa pero la IA no captura automaticamente. Giran inicial NPC; si se conquista se conserva propietario y resultado. Finalizar no borra una conquista, ni restablece silenciosamente el castillo a NPC. El fin nativo limpia inscripciones y reprograma fecha; si no hubo conquista Reunir/Registrar vuelve a inscribir cinco clanes. Si hubo conquista se necesita preparar expresamente otra modalidad antes de repetir.

## Defensores

382 posiciones nativas de guardias configuradas para Giran (no son382 bosses). Ares903200 y Nyx903201 son copias aisladas de los benchmarks900200/900201, sin modificar los originales del Coliseo. Conservan stats, skills, apariencia y combate base del motor. HP18000/16000 respectivamente; EXP/SP0 y sin drops, respawn desactivado. IA especial, fases, decisiones de defensa y balance para veinte atacantes quedan pendientes, tal como solicito Kevin.

Se instalo geodata23_22 de Giran: faltaba en el servidor. Parser nativo valida los65536bloques, veinte campamentos y dos posiciones de bosses con piso y NSWE transitables. Nyx se posiciona en117700,145150 con piso-2640; el ancla anterior estaba bloqueada y se corrigio antes de la prueba. Fuente fija: https://raw.githubusercontent.com/naustagic/L2JOrion_Interlude/98e351766c569504210a24d96a9f39262f19b397/L2jOrion_Geodata/geodata/23_22.l2j ; SHA256 aedaa9a4e2bc1b82957ca5610109c550930ecdf18bcb80f1f1064aeb26b1fa46,4412705bytes. Core GeoEngine sin modificaciones; regiones anteriores21_19/24_19 conservadas. El servidor carga tres regiones.

## Verificacion y continuidad

CHECKS checks PASS: clanes persistidos y recargados, miembros reservados/main/subs, parties nativas, registros atacantes DB/cache, puertas/zona/artefacto, campamentos con altura geodata, DDS validos y templates aislados. El verificador no cargo a Hellkevin, no inicio el asedio ni cambio propietario. Combate completo, recorrido de puertas y balance todavia requieren la prueba ingame.

Snapshots antes/despues: clanes originales/skills/castillo/382guardias identicos; entre todos los personajes solo cambio clanid de los ocho nuevos miembros. Los perfiles continúan offline al terminar la comprobacion. Hash del core y archivos del cliente conservados. Solo scripts/4DDS/XML nuevos; GameServer reiniciado, LoginServer conservado.

Fuentes research/giran-siege y server/game/data/scripts/custom/GiranSiegeLab. XML server/game/data/stats/npcs/custom/giran_lab_guardians.xml. Backup backups/giran-siege-2026-10-10. Fuentes, assets, documentos y continuidad32 copiados a source/dist y cloud-repo, sin commit/push. Instalacion de clanes opt-in -Dlab.giran.install=true, NO repetir: los clanes ya existen. Verificacion opt-in -Dlab.giran.verify=true one-shot terminada; arranque normal no instala ni inicia asedio.
'''.replace('CHECKS',str(proof['checks']))
p=r/'GIRAN-SIEGE-LAB.md';p.write_text(doc,encoding='utf-8')
name='32_GIRAN_SIEGE_LAB_2026-10-10.md'
for folder in ('CONTINUIDAD-W10','CONTINUIDAD-W11'):
 shutil.copy2(p,r/folder/name);shutil.copy2(p,r/'cloud-repo'/folder/name)
 q=r/folder/'LEER-PRIMERO.md';txt=q.read_text(encoding='utf-8-sig')
 if name not in txt:txt+='\nGiran siege 10/10: ver `'+name+'`. Cinco clanes x4, todos atacantes; Fury/Waves creados con crests, NPC+copias Ares/Nyx. `.giran` reunir/iniciar/seguir/asalto/retirada/finalizar. Siege no iniciado, IA especial bosses pendiente.\n';q.write_text(txt,encoding='utf-8')
 shutil.copy2(q,r/'cloud-repo'/folder/q.name)
shutil.copy2(p,r/'cloud-repo/docs'/p.name)
mirror=r/'cloud-repo/research/giran-siege';mirror.mkdir(parents=True,exist_ok=True)
for p in s.iterdir():
 if p.suffix in ('.java','.py','.ps1','.js','.json','.xml','.l2j'):shutil.copy2(p,mirror/p.name)
for p in (r/'crest/prepared').glob('*'):
 if p.name.startswith(('fury-','waves-')):dest=r/'cloud-repo/crest/prepared'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
n=Path('K:/_CodexNexus/inbox');note='FINALIZADO E:\\l2-local: Giran NPC siege preparado, cinco clanes x4 (Hellkevin+19 Player reales). Fury Riven/Eryndor/Korvash/Aelira, Waves Brunna/Lethiel/Sylira/Velith, nivel5 alianza/emblemas propios. Todos atacantes inscritos. .giran manual reunir/iniciar/seguir/asalto/retirada/finalizar; guardias382posiciones/puertas/torres/captura nativos120min. Ares903200/Nyx903201 copias aisladas de benchmarks, IAespecial y balance pendientes. '+str(proof['checks'])+' checks PASS; originalclanes/castillo y core/cliente conservados, siege NO iniciado. Continuidad32 en discoportable, GIRAN-SIEGE-LAB.md, backupgiran-siege-2026-10-10. No repetir flag lab.giran.install: clanes ya creados. Ventana GameServer libre; verificacion acabada.\n'
(n/'20261010-lineage2-giran-siege.md').write_text(note,encoding='utf-8');(n/'20261010-lineage2-giran-siege-in-progress.md').write_text('FINALIZADO; ventana libre. Ver 20261010-lineage2-giran-siege.md.\n',encoding='utf-8')
q=Path('K:/_CodexNexus/sessions/lineage2-local.md');txt=q.read_text(encoding='utf-8-sig')
if '20261010-lineage2-giran-siege.md' not in txt:q.write_text(txt+'\n10/10/2026 Giran NPC siege preparado .giran,5clanes x4 Fury/Waves nuevosconcrests,19pilotos. Ares/Nyx copias aisladas; IAespecial pendiente. Siege no iniciado, originalclanes/castillo/core/cliente conservados. Ver inbox/20261010-lineage2-giran-siege.md y continuidad32.\n',encoding='utf-8')
print(json.dumps(proof,indent=2))
