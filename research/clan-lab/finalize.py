from pathlib import Path
import hashlib,json,re,shutil
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent;b=r/'backups/clan-lab-2026-10-10'
log=(r/'logs/game-stderr.log').read_text(errors='replace')
m=re.search(r'ClanLabVerification SUCCESS: (\d+) checks',log)
assert m and 'ClanLabVerification FAILED' not in log
assert 'Roster Coliseo: 19 perfiles Player preparados' in log
assert 'CrestTable: Loaded 6 Crests.' in log
assert 'No se preparo el perfil normal' not in log
before=json.loads((b/'before.json').read_text());after=json.loads((b/'after.json').read_text());assert before==after,'Real DB changed during verification'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'server/libs/GameServer.jar')=='0c8c6655b8aae903d98f733815619813c4977c750e5c6126d44674027ad5aea6'
client=json.loads((r/'research/client-comfort/v3/installed-hashes.json').read_text())
assert all(sha(Path(p))==h for p,h in client.items() if not p.endswith('GameServer.jar'))
srcbase=r/'source/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/ClanLab'
cloudbase=r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data/scripts/custom/ClanLab'
for name in ('ClanLab.java','ClanLabVerification.java'):
 src=r/'server/game/data/scripts/custom/ClanLab'/name
 assert src.read_bytes()==(s/name).read_bytes()
 for base in (srcbase,cloudbase):
  dest=base/name
  assert not dest.exists() or dest.read_bytes()==src.read_bytes(),'Concurrent mirror edit'
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
shutil.copy2(r/'logs/game-stderr.log',b/'game-pass.log')
proof={'checks':int(m[1]),'status':'PASS','real_clans_unchanged':True,'reserved_test_clan_cleaned':True,'clan_skills':22,'core_client_unchanged':True,'roster_ready':19,'pid':int((r/'run/game.pid').read_text())}
(s/'verification.json').write_text(json.dumps(proof,indent=2))
doc=f'''# Paneles de clan de prueba — 10/10/2026

Dentro del juego: `.clanlab` abre inicio con dos botones. `.clannivel` abre niveles; `.clanskills` abre habilidades. Solo Hellkevin GM y lider de su propio clan. No requiere target y no selecciona clanes ajenos.

Niveles: ascenso directo hasta8, sin rebajar, con resumen y Aplicar/Cancelar. No aprende skills automaticamente. Prueba gratuita sin consumir adena, objetos, SP ni reputacion; condiciones habituales de poblacion/quests son omitidas para el laboratorio. Los maestros de clan normales conservan sus reglas.

Skills: catalogo instalado22habilidades, filtros por nivel5/6/7/8 y Todas, paginacion, Actualizar, detalle con icono/efecto/rango minimo, nivel aprendido/maximo. Aprender siguiente nivel normal, con Aplicar/Cancelar. No puede saltarse rangos, aprender skills futuras, superar maximo ni otorgar habilidades de residencia/subunidad. Pasivas modifican stats automaticamente; la elegibilidad social del miembro se respeta. Una skill aprendida por el clan no necesariamente beneficia a todos sus integrantes. Reputacion negativa desactiva efectos segun reglas nativas.

Los cambios son persistentes al aplicarlos. Se usan Clan.changeLevel y Clan.addNewSkill con verificacionDB; refresca rango social, pasivas, skills y estado de miembros conectados. Una confirmacion vence2minutos y se cancela al navegar. Revalida clan/lider/nivel/skill al aplicar y bloquea cambios durante muerte, combate/casteo/ataque/eventos/Olimpiadas/disolucion. No fija el GM para personajes nuevos; el acceso queda limitado al laboratorio.

Instalacion: dos archivos nuevos en server/game/data/scripts/custom/ClanLab. No se modifico GameServer.jar ni el cliente. Sin NPC nuevo ni cambios de apariencia. Tu Hellsing sigue nivel5 sin skills hasta que uses Aplicar; Holly y Sacred tambien sin cambios.

Verificacion: {proof['checks']} checks PASS en motor real con AmberOwnerProbe offline y clan descartable negativo, no Hellsing. Ascenso4a8, secuencia completa22skills, persistencia y recarga, efectos segun rango, aumentoHP real, rechazos de datos invalidos/stale/niveles futuros, HTML paginado dentro del limite y rutas voice. SnapshotDB de clanes/skills/12miembros/probe identico antes/despues; fixture borrado. No se confirmo visualmente el menu dentro del cliente. Roster19/19,6crests, hashescore/cliente conservados.

Fuentes, script de instalacion, snapshot y prueba: research/clan-lab. Backup: backups/clan-lab-2026-10-10. Verificador opt-in lab.clanlab.verify=true one-shot completado, no prueba en curso. Arranque habitual no activa esa propiedad. Fuentes source/dist y cloud-repo sincronizadas sin commit/push.
'''
p=r/'CLAN-PANELES-LAB.md';p.write_text(doc,encoding='utf-8')
name='31_CLAN_PANELES_LAB_2026-10-10.md'
for folder in ['CONTINUIDAD-W10','CONTINUIDAD-W11']:
 shutil.copy2(p,r/folder/name);shutil.copy2(p,r/'cloud-repo'/folder/name)
 q=r/folder/'LEER-PRIMERO.md';txt=q.read_text(encoding='utf-8-sig')
 if name not in txt:txt+='\nPanelesclan10/10: ver `'+name+'`. .clanlab / .clannivel / .clanskills; Hellkevin GM lider, prueba gratuita, ascenso hasta8 y22skills por nivel. Aplicar/Cancelar, cambios persistentes solo al pulsar. '+str(proof['checks'])+' checksPASS; clanes reales sin cambios.\n';q.write_text(txt,encoding='utf-8')
 shutil.copy2(q,r/'cloud-repo'/folder/q.name)
shutil.copy2(p,r/'cloud-repo/docs'/p.name)
mirror=r/'cloud-repo/research/clan-lab';mirror.mkdir(parents=True,exist_ok=True)
for p in s.iterdir():
 if p.suffix in ('.java','.py','.ps1','.js','.json'):shutil.copy2(p,mirror/p.name)
n=Path('K:/_CodexNexus/inbox')
note='FINALIZADO E:\\l2-local: panelesingame .clanlab / .clannivel / .clanskills para HellkevinGM lider. Ascenso hasta8 y22skills disponiblesporclanlevel, filtros5-8, detalle icono/efecto/rango, Aplicar/Cancelar. Pruebagratuita sincostes, cambiosnativosguardados solo alclick. '+str(proof['checks'])+' checksPASS en clan descartable con probeoffline, persistenciareload/stats/rangos/invalid requests. Snapshots clanesreales/skills/members/probe iguales. Core y cliente intactos, roster19/19,6crests. VentanaGameServer libre; pruebaone-shot acabada. Docs CLAN-PANELES-LAB.md/continuidad31; backupclan-lab-2026-10-10. Revisionvisual usuario pendiente.\n'
(n/'20261010-lineage2-clanlab.md').write_text(note,encoding='utf-8');(n/'20261010-lineage2-clanlab-in-progress.md').write_text('FINALIZADO, ventana libre. Ver 20261010-lineage2-clanlab.md.\n',encoding='utf-8')
q=Path('K:/_CodexNexus/sessions/lineage2-local.md');txt=q.read_text(encoding='utf-8-sig')
if '20261010-lineage2-clanlab.md' not in txt:q.write_text(txt+'\n10/10/2026: paneles .clanlab niveles/skills, HellkevinGMlider, gratuito. '+str(proof['checks'])+' checksPASS, clanes sin modificaciones hasta aplicar. Ver inbox/20261010-lineage2-clanlab.md, continuidad31.\n',encoding='utf-8')
print(json.dumps(proof,indent=2))
