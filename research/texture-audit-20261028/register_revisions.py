"""Accept ONLY verified material revisions; retain original artifacts and rig evidence."""
import pathlib,json,sqlite3,datetime,hashlib
from repair_materials import read,immutable,sha,CAT,ROOT
RIG=pathlib.Path(r'E:\l2-local\research\rig-database-20261028')
db=sqlite3.connect(RIG/'rig-catalog.sqlite');stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=RIG/'database-revisions'/('before-materials-'+stamp+'.sqlite');backup.parent.mkdir(exist_ok=True)
with sqlite3.connect(backup) as snapshot:db.backup(snapshot)
db.execute('PRAGMA foreign_keys=ON')
db.execute('CREATE TABLE IF NOT EXISTS material_revisions(model_key TEXT,old_sha256 TEXT,new_sha256 TEXT,created_utc TEXT,evidence_json TEXT,PRIMARY KEY(model_key,new_sha256))')
gallery=json.loads((CAT/'gallery.json').read_text('utf-8'));by={m['key']:m for m in gallery['models']};index=json.loads((CAT/'rig-data/index.json').read_text('utf-8'))
for rec in json.loads((ROOT/'revisions.json').read_text('utf-8')):
 key=rec['key'];m=by[key];old=pathlib.Path(rec['backup'])/'model.glb';new=CAT/m['gltf'];og,ob=read(old);ng,nb=read(new)
 assert sha(old.read_bytes())==rec['before_sha256'] and sha(new.read_bytes())==rec['after_sha256']
 assert immutable(og)==immutable(ng) and nb[:len(ob)]==ob
 assert ng.get('bufferViews',[])[:len(og.get('bufferViews',[]))]==og.get('bufferViews',[])
 prior=db.execute('SELECT artifact_sha256,summary_json FROM models WHERE key=?',(key,)).fetchone()
 if not prior:continue
 assert prior[0] in [rec['before_sha256'],rec['after_sha256']]
 db.execute('UPDATE artifacts SET snapshot_path=? WHERE sha256=?',(str(old),rec['before_sha256']))
 db.execute('INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?,?)',(rec['after_sha256'],str(new),new.stat().st_size,'glb',None))
 summary=json.loads(prior[1]);summary['artifact_sha256']=rec['after_sha256'];summary['material_revision_evidence']=str(ROOT/'revisions.json')
 db.execute('UPDATE models SET artifact_sha256=?,summary_json=? WHERE key=?',(rec['after_sha256'],json.dumps(summary),key))
 db.execute('INSERT OR IGNORE INTO material_revisions VALUES(?,?,?,?,?)',(key,rec['before_sha256'],rec['after_sha256'],stamp,json.dumps(rec)))
 public=CAT/'rig-data'/(key+'.json');data=json.loads(public.read_text('utf-8'));data['artifact_sha256']=rec['after_sha256'];data['material_revision_evidence']=str(ROOT/'revisions.json');public.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 if m.get('rig_analysis'):m['rig_analysis']['artifact_sha256']=rec['after_sha256']
 for row in index['models']:
  if row['key']==key:row['artifact_sha256']=rec['after_sha256']
 print('REGISTERED',key)
db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close()
(CAT/'rig-data/index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');(CAT/'gallery.json').write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf-8')
