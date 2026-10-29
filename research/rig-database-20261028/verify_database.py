import pathlib,sqlite3,hashlib,zlib,json,struct
from build_database import ROOT,PRIMARY,COMPONENTS

db=sqlite3.connect(ROOT/'rig-catalog.sqlite');assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall()
channels=0
for row in db.execute('SELECT input_component_type,input_count,output_component_type,output_count,output_width,input_raw_zlib,output_raw_zlib,input_sha256,output_sha256 FROM channels'):
    it,ic,ot,oc,ow,ib,ob,ih,oh=row;inp=zlib.decompress(ib);out=zlib.decompress(ob)
    assert len(inp)==COMPONENTS[it][1]*ic;assert len(out)==COMPONENTS[ot][1]*oc*ow
    assert hashlib.sha256(inp).hexdigest()==ih;assert hashlib.sha256(out).hexdigest()==oh;channels+=1
artifacts=0
for sha,path in db.execute('SELECT sha256,snapshot_path FROM artifacts WHERE snapshot_path IS NOT NULL'):
    assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==sha;artifacts+=1
assert db.execute('SELECT count(*) FROM joints WHERE model_key=?',(PRIMARY,)).fetchone()[0]==144
assert db.execute('SELECT count(*) FROM source_bones WHERE model_key=?',(PRIMARY,)).fetchone()[0]==144
assert db.execute('SELECT count(*) FROM segments').fetchone()[0]==0
assert db.execute('SELECT count(*) FROM experiments').fetchone()[0]==0
report={'sqlite_integrity':'ok','foreign_keys':'ok','decoded_channel_blobs_sha256_verified':channels,'snapshots_sha256_verified':artifacts,'models':db.execute('SELECT count(*) FROM models').fetchone()[0],'sett_joint_count':144,'source_bone_count':144,'semantic_segments':0,'retarget_experiments':0}
(ROOT/'database-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report));db.close()
