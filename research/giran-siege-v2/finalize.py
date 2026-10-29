from pathlib import Path
import json,hashlib,re,shutil
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent;b=r/'backups/giran-siege-v2-2026-10-11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log=(r/'logs/game-stderr.log').read_text(errors='replace')
m=re.search(r'GIRAN_V2_VERIFY PASS checks=(\d+) ticks=(\d+) moved=(\d+) damagedDefenders=(\d+)',log)
assert m and 'GIRAN_V2_VERIFY FAILED' not in log and 'OutOfMemoryError' not in log
before=json.loads((b/'state-before.json').read_text());after=json.loads((b/'after.json').read_text())
assert all(before[k]==after[k] for k in ('human','inventory','clans','skills','castle','siege','guards'))
assert len(after['pilots'])==19 and all(p['level']==80 and p['online']==0 for p in after['pilots'])
core=json.loads((s/'core-proof.json').read_text());assert sha(r/'server/libs/GameServer.jar')==core['new']
proof={'status':'PASS','native_checks':int(m[1]),'smoke_ticks':int(m[2]),'pilots_moved':int(m[3]),'defenders_damaged':int(m[4]),'human_and_inventory_unchanged':True,'castle_clans_schedule_registrations_unchanged':True,'all19_offline80':True,'path_pool_max_buffers':32,'old_retained_buffers':468,'global_array_memory_cap_bytes':68513792,'core_changed_entries':core['entries_changed'],'test_invulnerability':True,'test_opened_outer_doors':True,'full_siege_balance':'user trial pending','pid':int((r/'run/game.pid').read_text())}
(s/'verification.json').write_text(json.dumps(proof,indent=2))
shutil.copy2(r/'logs/game-stderr.log',b/'game-pass.log')
old=json.loads((r/'research/giran-siege/installed.json').read_text())
for folder in ('source/L2J_Mobius_CT_0_Interlude/dist/game','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game'):
 for src in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
  dest=r/folder/'data/scripts/custom/GiranSiegeLab'/src.name
  if dest.exists() and dest.read_bytes()!=src.read_bytes():assert src.name in old and sha(dest).upper()==old[src.name],'Concurrent mirror edit:'+str(dest)
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
for name in ('PathFinding.java','NodeBuffer.java'):
 src=r/'source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/geoengine/pathfinding'/name
 dest=r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/geoengine/pathfinding'/name
 if dest.exists() and dest.read_bytes()!=src.read_bytes():assert name=='PathFinding.java' and dest.read_bytes()==(b/'PathFinding-before.java').read_bytes(),'Concurrent core source mirror edit'
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
src=r/'source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/entity/clan/ClanMember.java';dest=r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/entity/clan/ClanMember.java'
if dest.exists() and dest.read_bytes()!=src.read_bytes():assert dest.read_bytes()==(b/'ClanMember-before.java').read_bytes(),'Concurrent clan source mirror edit'
dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
dest=r/'cloud-repo/ops/windows/Start-L2Local.ps1';assert dest.read_bytes()==(b/'Start-L2Local-before.ps1').read_bytes() or dest.read_bytes()==(r/'Start-L2Local.ps1').read_bytes();shutil.copy2(r/'Start-L2Local.ps1',dest)
doc=f'''# Giran: escuadrones y correccion de bloqueo — 11/10/2026

`.giran` → Reunir escuadrones → Iniciar siege. El modo inicial ahora es Objetivos por escuadron. Hellsing escolta a Hellkevin; los otros cuatro clanes avanzan con capitan, blanco, progreso y ruta propios. Reagrupar conmigo vuelve a la escolta; Retirada y Finalizar conservan su funcion. El panel muestra la tarea actual de cada clan. Los pilotos no castean conquista.

| Escuadron | Agenda |
|---|---|
| Hellsing | Escolta, proteccion y asistencia del conquistador |
| Holly | Puerta exterior norte, cristal de entrada, puerta interior norte, torre de fuego oriental |
| Sacred | Puerta exterior sur, guardias del patio sur, puerta interior sur, cristal oriental |
| Fury | Puerta exterior norte, Ares, puerta interior norte, cristal central |
| Waves | Puerta exterior sur, guardias del patio norte, puerta interior sur, torre de fuego norte, Nyx |

Al terminar su agenda, cada clan protege al conquistador. Comparten los cuellos de botella cuando hace falta romper las mismas puertas, pero conservan objetivos propios. Los integrantes siguen a su capitan, se reagrupan si quedan lejos, atienden amenazas cercanas y mantienen autoataque nativo. Cadencias de decision 750–1300 ms y salida escalonada 1,6 s por clan; no se teletransportan atravesando puertas. Reintento de movimiento si estan detenidos 12 s. Los objetivos eliminados por otro escuadron tambien se dan por completados.

## Bloqueo y bando

El GameServer agoto sus 2 GB de heap: OutOfMemoryError en IA/red/schedulers. La reserva ThreadLocal de caminos retenia 468 NodeBuffer y unos 900 MB de arrays. Se reemplazo por una reserva global exclusiva, sin espera bloqueante, limitada por los conteos configurados: 32 buffers, 68.513.792 bytes de arrays como maximo. Si estan ocupados, la solicitud devuelve null para el reintento nativo, sin retener un buffer por hilo. El algoritmo A* y geodata se conservan. Jar: solo cambiaron PathFinding.class, su SingletonHolder y ClanMember.class para reconocer pilotos activos sin socket; todas las otras entradas, incluidos parches anteriores, son identicas.

Start-L2Local.ps1 usa 4 GB de heap en esta PC de 32 GB. Ajusta automaticamente 2/3/4 GB segun memoria fisica y permite -GameHeapMb; LoginServer se conserva. No basta con subir memoria: el pool acotado corrige la retencion.

Los pilotos ahora enlazan ClanMember.setPlayer al cargar. ClanMember.isOnline reconoce Player.isLabControlled cuando esta activo sin socket: antes, el chequeo de offline shop excluia a todos los pilotos aunque el enlace estuviera presente. El motor nativo les asigna estado atacante y lado Giran; antes faltaba ese enlace/reconocimiento y Amber llego a considerar enemigo a Riven. No se modifico Amber: ahora su comprobacion nativa isSiegeFriend reconoce a los atacantes aliados. Experiencia/nivel del piloto reservado se conservan durante la prueba y al limpiar. Se recuperaron seis perfiles que habian bajado a 79 por muertes de este asedio: Myrentha, Noctis, Ignara, Aelira, Arden y Selene. Hellkevin no se cargo ni se modifico.

## Conquista manual

No requiere item. Seal of Ruler (246, nivel 1) consume 50 MP y tarda 180.000 ms: tres minutos fijos, sin reduccion por casting speed. Solo el lider de un clan atacante inscrito, durante el siege, sobre el artefacto correcto y a su altura. La comprobacion de conquista admite hasta 200 unidades/45 de diferencia vertical; el alcance de casteo de la skill es 85, por lo que hay que acercarse al pedestal. Mantener el casteo sin interrupcion. Los 300 Gemstone C (2131) corresponden a Build Headquarters (247), no a Seal of Ruler. Fuente local: server/game/data/stats/skills/00200-00299.xml y condiciones nativas de conquista.

## Validacion

Pool: 128 hilos, 25.600 solicitudes, arrendamiento exclusivo, limite 32 buffers y menos de 80 MiB en arrays; PASS. Prueba nativa opt-in de 85 segundos: {proof['native_checks']} checks, 19 Players reservados en cinco parties, amistad entre todos los pares de atacantes, objetivos reales atacables, artefacto excluido, {proof['pilots_moved']} pilotos desplazados y {proof['defenders_damaged']} defensores/puertas con perdida real de HP. Para verificar avance sin esperar romper puertas, la prueba abrio solo las puertas exteriores a los 35 s y dio invulnerabilidad temporal a los pilotos. No mide balance ni una conquista completa; esos quedan para la prueba de Kevin.

Limpieza nativa terminada: 19 pilotos offline nivel 80, bosses retirados, parties desarmadas, lock liberado. Snapshots: Hellkevin completo e inventario, cinco clanes/skills, castillo/fecha/inscripciones y 382 guardias configurados identicos. Propietario Giran NPC. Full run de castillo, rutas interiores bajo combate y balance requieren prueba ingame. IA especial de Ares/Nyx sigue pendiente; conservan combate base.

Fuentes/pruebas: research/giran-siege-v2. Backup: backups/giran-siege-v2-2026-10-11 (OOM/histograma/Jar/scripts anteriores/snapshots/proof). Continuidad 33 en W10/W11 y Nexus. Source/dist/cloud overlay sincronizados, sin commit/push. No repetir instalador V1 ni lab.giran.install=true: clanes ya creados. Verificador V2 opt-in -VerifyGiranAgenda; arranque normal no inicia siege ni prueba automatica.
'''
p=r/'GIRAN-SIEGE-ESCUADRONES-V2.md';p.write_text(doc,encoding='utf-8')
base=r/'GIRAN-SIEGE-LAB.md';txt=base.read_text(encoding='utf-8');notice='\n> Actualizacion 11/10/2026: reemplazada la conducta de grupo por agendas independientes y corregido OOM/bando. Ver GIRAN-SIEGE-ESCUADRONES-V2.md; las ordenes de movimiento V1 descritas abajo son historicas.\n'
if 'GIRAN-SIEGE-ESCUADRONES-V2.md' not in txt:base.write_text(notice+txt,encoding='utf-8')
name='33_GIRAN_ESCUADRONES_V2_2026-10-11.md'
for folder in ('CONTINUIDAD-W10','CONTINUIDAD-W11'):
 shutil.copy2(p,r/folder/name);shutil.copy2(p,r/'cloud-repo'/folder/name)
 q=r/folder/'LEER-PRIMERO.md';txt=q.read_text(encoding='utf-8-sig')
 if name not in txt:q.write_text(txt+'\n11/10 Giran V2: ver '+name+'. OOM corregido, agendas independientes, bandos nativos y19pilotos80. Conquista manual246:50MP/3min/sinitem.\n',encoding='utf-8')
 shutil.copy2(q,r/'cloud-repo'/folder/q.name)
for p in (p,base):shutil.copy2(p,r/'cloud-repo/docs'/p.name)
mirror=r/'cloud-repo/research/giran-siege-v2';mirror.mkdir(parents=True,exist_ok=True)
for p in s.iterdir():
 if p.suffix in ('.java','.py','.ps1','.js','.json'):shutil.copy2(p,mirror/p.name)
note=f'FINALIZADO 11/10 E:\\l2-local GiranV2: OOM2GB corregido con PathFinding poolglobal32buffers(<80MiBarrays), heap4GBestaPC. Agendas independientes4clanes + Hellsing escolta, cadencias variables/capitanes. ClanMember online link restaurado: bandos/amigos nativos (Amber no modificada). Seis pilotos muertos79recuperados80; preservanXP. NativeSmoke85s PASS {proof["native_checks"]}checks,{proof["pilots_moved"]}movidos,{proof["defenders_damaged"]}defensoresdamaged; test invul/outerdoorsopen,nohuman/conquista. Estadohuman/inventory/clanes/skills/castillo/fecha/inscripciones/382guards identico;19offline80. Seal246sinitem50MP3minfijos. Recorrido completo/balance yIAespecialbossespending. Docs GIRAN-SIEGE-ESCUADRONES-V2.md/continuidad33enportable/source/cloud,sincommitpush. GameServer ventana libre; no repetirV1installer/claninstall.\n'
inbox=Path('K:/_CodexNexus/inbox');(inbox/'20261011-giran-v2.md').write_text(note,encoding='utf-8');(inbox/'20261011-giran-v2-in-progress.md').write_text('FINALIZADO; GameServer libre. Ver 20261011-giran-v2.md.\n',encoding='utf-8')
q=Path('K:/_CodexNexus/sessions/lineage2-local.md');txt=q.read_text(encoding='utf-8-sig')
if '20261011-giran-v2.md' not in txt:q.write_text(txt+'\n11/10 Giran V2: OOM pool32/heap4GB, agendas independientes, bandos nativos/19pilotos80. Prueba nativa PASS. Conquista246sinitem50MP3min. Continuidad33; ver inbox/20261011-giran-v2.md.\n',encoding='utf-8')
print(json.dumps(proof,indent=2))
