"""Record Kevin's explicit in-game confirmation, keeping earlier failures as history."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
confirmation=dict(date_local='2026-10-14',source='Kevin, explicit reply to in-game walls/floors test',quote='Sí, ahora pisos y paredes funcionan',scope='User-confirmed floor support and wall blocking during manual exploration; no exhaustive route, camera, combat LOS, performance or exit-crash certification.')
m=json.loads((D/'installation.json').read_text())
assert all(hashlib.sha256(Path(r['target']).read_bytes()).hexdigest()==r['after_sha256'] for r in m['files']), 'Installed files changed since last deployment'
for rel in ['verification.json','native-floor/verification.json','native-walls/verification.json']:
 p=D/rel;v=json.loads(p.read_text());v['client_physics_verified']=True;v['verification_source']='user_report';v['client_confirmation']=confirmation
 if rel=='verification.json':
  v.update(continuous_native_floor_client_verified=True,native_walls_client_verified=True,client_exit_critical_resolved=False,current_status='Manual exploration: floors and walls confirmed working by Kevin')
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
m['client_physics_verified']=True;m['client_confirmation']=confirmation
for key in ['native_floor_support','native_wall_support']:
 if key in m:m[key]['client_physics_verified']=True;m[key]['client_confirmation']=confirmation
(D/'installation.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');(Path(m['backup'])/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
note='> Confirmación posterior de Kevin, 14/10/2026: «Sí, ahora pisos y paredes funcionan». Suelo y bloqueo de paredes confirmados por el usuario dentro de L2 tras instalar native-walls. Las incidencias y pendientes anteriores se conservan debajo como historial; no equivalen al estado actual. El critical de salida sigue sin confirmación de resolución.\n\n'
for rel in ['README.md','native-floor/README.md','native-walls/README.md']:
 p=D/rel;p.write_text(note+p.read_text(encoding='utf-8'),encoding='utf-8')
p=ROOT/'DUST2-EN-L2.md';p.write_text(p.read_text(encoding='utf-8')+'\n## Validación dentro de L2\n\nKevin confirmó el 14/10/2026: «Sí, ahora pisos y paredes funcionan». La versión actual combina el mapa visual de Dust2 con soporte nativo de suelo y paredes siguiendo la geodata. Confirmación de recorrido manual, no certificación exhaustiva de todos los puntos.\n\nEl critical de salida reportado anteriormente sigue pendiente de diagnóstico/confirmación; no se declara corregido por esta prueba.\n',encoding='utf-8')
print('Recorded explicit in-game user confirmation; installed hashes verified; no client/server changes.')
