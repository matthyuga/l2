"""Versioned rig observations from GLB bytes, plus the selected FBX import observation."""
import pathlib,json,struct,hashlib,sqlite3,zlib,math,re,collections,datetime,shutil,zipfile,sys

ROOT=pathlib.Path(__file__).resolve().parent
CAT=pathlib.Path(r'E:\l2-local\research\model-catalog')
PRIMARY='ext3_02b86c82826120'
PUBLIC=CAT/'rig-data';PUBLIC.mkdir(exist_ok=True)
DB=ROOT/'rig-catalog.sqlite'
COMPONENTS={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
WIDTH={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT2':4,'MAT3':9,'MAT4':16}
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def norm(s):return re.sub('[^a-z0-9]','',s.casefold())
IDENT=[1.,0,0,0,0,1.,0,0,0,0,1.,0,0,0,0,1.]
def mul(a,b):return [sum(a[k*4+r]*b[c*4+k] for k in range(4)) for c in range(4) for r in range(4)]
def matrix(node):
    if 'matrix' in node:return node['matrix']
    x,y,z,w=node.get('rotation',[0,0,0,1]);sx,sy,sz=node.get('scale',[1,1,1]);tx,ty,tz=node.get('translation',[0,0,0])
    return [(1-2*y*y-2*z*z)*sx,(2*x*y+2*z*w)*sx,(2*x*z-2*y*w)*sx,0,(2*x*y-2*z*w)*sy,(1-2*x*x-2*z*z)*sy,(2*y*z+2*x*w)*sy,0,(2*x*z+2*y*w)*sz,(2*y*z-2*x*w)*sz,(1-2*x*x-2*y*y)*sz,0,tx,ty,tz,1]

class GLB:
    def __init__(self,p):
        self.path=p;self.raw=p.read_bytes();magic,version,size=struct.unpack_from('<4sII',self.raw)
        assert magic==b'glTF' and version==2 and size==len(self.raw),'Invalid GLB header'
        pos=12;chunks=[]
        while pos<len(self.raw):
            n,kind=struct.unpack_from('<II',self.raw,pos);pos+=8
            assert pos+n<=len(self.raw),'Truncated GLB chunk';chunks.append((kind,self.raw[pos:pos+n]));pos+=n
        self.g=json.loads(next(b for k,b in chunks if k==0x4E4F534A));self.bin=next((b for k,b in chunks if k==0x004E4942),b'');self.cache={}
    def accessor(self,i):
        if i in self.cache:return self.cache[i]
        a=self.g['accessors'][i];assert not a.get('sparse'),'Sparse accessor needs explicit decoder'
        v=self.g['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0
        typ,n=COMPONENTS[a['componentType']];width=WIDTH[a['type']];packed_size=width*n;stride=v.get('byteStride',packed_size)
        start=v.get('byteOffset',0)+a.get('byteOffset',0);count=a['count']
        assert count==0 or start+(count-1)*stride+packed_size<=len(self.bin),'Accessor out of bounds'
        raw=b''.join(self.bin[start+k*stride:start+k*stride+packed_size] for k in range(count))
        result={'raw':raw,'format':'<'+typ*width,'count':count,'width':width,'component_type':a['componentType'],'normalized':a.get('normalized',False),'accessor':i}
        self.cache[i]=result;return result
    def rows(self,i):
        a=self.accessor(i)
        for row in struct.iter_unpack(a['format'],a['raw']):
            if a['normalized'] and a['component_type']!=5126:
                maximum={5120:127,5121:255,5122:32767,5123:65535,5125:4294967295}[a['component_type']];row=tuple(max(-1,x/maximum) for x in row)
            yield row

SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, created_utc TEXT, parser TEXT, limitations_json TEXT);
CREATE TABLE IF NOT EXISTS artifacts(sha256 TEXT PRIMARY KEY,path TEXT,bytes INTEGER,format TEXT,snapshot_path TEXT);
CREATE TABLE IF NOT EXISTS models(key TEXT PRIMARY KEY,title TEXT,artifact_sha256 TEXT REFERENCES artifacts(sha256),source_json TEXT,summary_json TEXT,run_id TEXT REFERENCES runs(id));
CREATE TABLE IF NOT EXISTS nodes(model_key TEXT REFERENCES models(key),node_index INTEGER,name TEXT,parent_index INTEGER,local_matrix_json TEXT,world_matrix_json TEXT,PRIMARY KEY(model_key,node_index));
CREATE TABLE IF NOT EXISTS joints(model_key TEXT REFERENCES models(key),skin_index INTEGER,joint_order INTEGER,node_index INTEGER,parent_joint_node INTEGER,inverse_bind_matrix_json TEXT,weighted_vertices INTEGER,PRIMARY KEY(model_key,skin_index,joint_order));
CREATE TABLE IF NOT EXISTS clips(model_key TEXT REFERENCES models(key),clip_index INTEGER,name TEXT,start_seconds REAL,end_seconds REAL,channels INTEGER,PRIMARY KEY(model_key,clip_index));
CREATE TABLE IF NOT EXISTS channels(model_key TEXT,clip_index INTEGER,channel_index INTEGER,target_node INTEGER,path TEXT,interpolation TEXT,input_component_type INTEGER,input_count INTEGER,output_component_type INTEGER,output_count INTEGER,output_width INTEGER,input_raw_zlib BLOB,output_raw_zlib BLOB,input_sha256 TEXT,output_sha256 TEXT,statistics_json TEXT,PRIMARY KEY(model_key,clip_index,channel_index),FOREIGN KEY(model_key,clip_index) REFERENCES clips(model_key,clip_index));
CREATE TABLE IF NOT EXISTS source_bones(model_key TEXT REFERENCES models(key),bone_index INTEGER,name TEXT,parent_name TEXT,observation_json TEXT,PRIMARY KEY(model_key,bone_index));
CREATE TABLE IF NOT EXISTS source_actions(model_key TEXT REFERENCES models(key),action_index INTEGER,observation_json TEXT,PRIMARY KEY(model_key,action_index));
CREATE TABLE IF NOT EXISTS annotations(model_key TEXT REFERENCES models(key),node_index INTEGER,label TEXT,authority TEXT,status TEXT,PRIMARY KEY(model_key,node_index,label));
CREATE TABLE IF NOT EXISTS segments(id INTEGER PRIMARY KEY,model_key TEXT,clip_index INTEGER,start_seconds REAL,end_seconds REAL,label TEXT,authority TEXT,status TEXT,CHECK(start_seconds>=0 AND end_seconds>start_seconds),FOREIGN KEY(model_key,clip_index) REFERENCES clips(model_key,clip_index));
CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY,source_model TEXT REFERENCES models(key),target_model TEXT REFERENCES models(key),parameters_json TEXT,status TEXT,result_json TEXT);
CREATE TABLE IF NOT EXISTS validations(model_key TEXT REFERENCES models(key),name TEXT,status TEXT,details_json TEXT,PRIMARY KEY(model_key,name));
CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY,authority TEXT,path TEXT,sha256 TEXT,limitations_json TEXT);
'''

def anatomy(name):
    n=norm(name)
    for prefix in ['mixamorig','bip001','bip01','bip','bone']:
        if n.startswith(prefix):n=n[len(prefix):];break
    aliases={'pelvis':'pelvis','hips':'pelvis','spine':'spine.lower','spine1':'spine.middle','spine2':'spine.upper','neck':'neck','head':'head'}
    if n in aliases:return aliases[n]
    for side,tokens in [('left',['left','l']),('right',['right','r'])]:
        for token in tokens:
            tail=n[len(token):] if n.startswith(token) else ''
            for part,words in [('clavicle',['clavicle','shoulder']),('upperarm',['upperarm','arm']),('forearm',['forearm','lowerarm']),('hand',['hand']),('thigh',['thigh','upleg']),('calf',['calf','leg','lowerleg']),('foot',['foot'])]:
                if tail in words:return side+'.'+part
    return None

def observe(m,db,run):
    p=CAT/m['gltf'];obj=GLB(p);g=obj.g;sha=digest(obj.raw)
    previous=db.execute('SELECT artifact_sha256 FROM models WHERE key=?',(m['key'],)).fetchone()
    if previous and previous[0]!=sha:raise ValueError('Artifact changed: use a new revision key instead of overwriting the baseline '+m['key'])
    db.execute('INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?,?)',(sha,str(p),len(obj.raw),'glb',None))
    db.execute('INSERT OR REPLACE INTO models VALUES(?,?,?,?,?,?)',(m['key'],m['title'],sha,canonical(m.get('source',{})),'{}',run))
    parents={}
    for i,node in enumerate(g.get('nodes',[])):
        for child in node.get('children',[]):
            assert child not in parents,'Node has multiple parents';parents[child]=i
    worlds={}
    def world(i,visiting=None):
        if i in worlds:return worlds[i]
        visiting=set(visiting or []);assert i not in visiting,'Node cycle';visiting.add(i)
        worlds[i]=mul(world(parents[i],visiting),matrix(g['nodes'][i])) if i in parents else matrix(g['nodes'][i]);return worlds[i]
    for i,node in enumerate(g.get('nodes',[])):
        assert all(math.isfinite(v) for v in world(i)),'Non-finite rest matrix'
        db.execute('INSERT OR REPLACE INTO nodes VALUES(?,?,?,?,?,?)',(m['key'],i,node.get('name',''),parents.get(i),canonical(matrix(node)),canonical(world(i))))
    weighted=collections.Counter();influence_hist=collections.Counter();weight_bad=0;influence_lost=[]
    for ni,node in enumerate(g.get('nodes',[])):
        if 'mesh' not in node or 'skin' not in node:continue
        skin=g['skins'][node['skin']]
        for primitive in g['meshes'][node['mesh']]['primitives']:
            attributes=primitive['attributes']
            if 'JOINTS_0' not in attributes:continue
            js=list(obj.rows(attributes['JOINTS_0']));ws=list(obj.rows(attributes['WEIGHTS_0']));assert len(js)==len(ws)
            extra=list(obj.rows(attributes['JOINTS_1'])) if 'JOINTS_1' in attributes else None;extra_w=list(obj.rows(attributes['WEIGHTS_1'])) if 'WEIGHTS_1' in attributes else None
            for vi,(jrow,wrow) in enumerate(zip(js,ws)):
                pairs=list(zip(jrow,wrow))+(list(zip(extra[vi],extra_w[vi])) if extra is not None else [])
                assert all(0<=j<len(skin['joints']) for j,w in pairs),'Joint index outside skin'
                active=[(int(j),w) for j,w in pairs if w>1e-8];influence_hist[len(active)]+=1
                if active and abs(sum(w for j,w in active)-1)>1e-4:weight_bad+=1
                for j,w in active:weighted[(node['skin'],j)]+=1
    bones=[];topology=[]
    for si,skin in enumerate(g.get('skins',[])):
        js=skin['joints'];assert len(js)==len(set(js)),'Repeated joint node within skin'
        ib=list(obj.rows(skin['inverseBindMatrices'])) if 'inverseBindMatrices' in skin else [None]*len(js);assert len(ib)==len(js),'Inverse bind count mismatch'
        for order,i in enumerate(js):
            par=parents.get(i)
            while par is not None and par not in js:par=parents.get(par)
            name=g['nodes'][i].get('name','');parent_name=g['nodes'][par].get('name','') if par is not None else None
            b={'skin':si,'order':order,'node':i,'name':name,'parent_node':par,'parent_name':parent_name,'rest_world_translation':world(i)[12:15],'local_matrix_column_major':matrix(g['nodes'][i]),'world_matrix_column_major':world(i),'inverse_bind_matrix_column_major':ib[order],'weighted_vertices':weighted[(si,order)]}
            if anatomy(name):b['anatomy_candidate']={'label':anatomy(name),'authority':'name-heuristic','status':'unverified'};db.execute('INSERT OR REPLACE INTO annotations VALUES(?,?,?,?,?)',(m['key'],i,anatomy(name),'name-heuristic','unverified'))
            bones.append(b);topology.append([name,parent_name])
            db.execute('INSERT OR REPLACE INTO joints VALUES(?,?,?,?,?,?,?)',(m['key'],si,order,i,par,canonical(ib[order]),weighted[(si,order)]))
    clips=[];all_finite=True;times_strict=True;quaternion_bad=0
    for ci,clip in enumerate(g.get('animations',[])):
        inputs=[obj.accessor(s['input']) for s in clip['samplers']];times=[v[0] for s in clip['samplers'] for v in obj.rows(s['input'])];start=min(times,default=0);end=max(times,default=0)
        db.execute('INSERT OR REPLACE INTO clips VALUES(?,?,?,?,?,?)',(m['key'],ci,clip.get('name',''),start,end,len(clip['channels'])))
        channels=[]
        for chi,c in enumerate(clip['channels']):
            sampler=clip['samplers'][c['sampler']];a=obj.accessor(sampler['input']);b=obj.accessor(sampler['output']);t=[r[0] for r in obj.rows(sampler['input'])];rows=list(obj.rows(sampler['output']))
            times_strict &= all(x<y for x,y in zip(t,t[1:]));all_finite &= all(math.isfinite(v) for row in rows for v in row)
            lo=[min(row[k] for row in rows) for k in range(b['width'])] if rows else [];hi=[max(row[k] for row in rows) for k in range(b['width'])] if rows else []
            target=c['target'];path=target['path'];node_index=target.get('node');interpolation=sampler.get('interpolation','LINEAR')
            if path!='weights':assert b['count']==a['count']*(3 if interpolation=='CUBICSPLINE' else 1),'Animation sample shape mismatch'
            stats={'min':lo,'max':hi,'varying_tolerance_1e_6':any(y-x>1e-6 for x,y in zip(lo,hi)),'start_seconds':min(t,default=0),'end_seconds':max(t,default=0),'input_accessor':sampler['input'],'output_accessor':sampler['output'],'input_normalized':a['normalized'],'output_normalized':b['normalized']}
            if path=='rotation':
                norms=[math.sqrt(sum(v*v for v in row)) for row in rows];stats['quaternion_norm_min']=min(norms,default=0);stats['quaternion_norm_max']=max(norms,default=0);quaternion_bad+=sum(abs(v-1)>1e-3 for v in norms)
            db.execute('INSERT OR REPLACE INTO channels VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(m['key'],ci,chi,node_index,path,interpolation,a['component_type'],a['count'],b['component_type'],b['count'],b['width'],zlib.compress(a['raw']),zlib.compress(b['raw']),digest(a['raw']),digest(b['raw']),canonical(stats)))
            channels.append({'index':chi,'node':node_index,'node_name':g['nodes'][node_index].get('name','') if node_index is not None else None,'path':path,'interpolation':interpolation,'input_samples':a['count'],'output_samples':b['count'],'output_width':b['width'],'output_sha256':digest(b['raw']),**stats})
        clips.append({'index':ci,'name':clip.get('name',''),'start_seconds':start,'end_seconds':end,'duration_seconds':end-start,'channel_count':len(channels),'varying_channels':sum(v['varying_tolerance_1e_6'] for v in channels),'channels':channels,'semantic_labels':[]})
    validation={'finite_values':all_finite,'strictly_increasing_animation_times':times_strict,'quaternion_samples_outside_norm_tolerance_1e_3':quaternion_bad,'weight_vertices_outside_sum_tolerance_1e_4':weight_bad,'acyclic_node_hierarchy':True,'skin_indices_and_inverse_bind_counts':True}
    for name,value in validation.items():db.execute('INSERT OR REPLACE INTO validations VALUES(?,?,?,?)',(m['key'],name,'pass' if value is True or value==0 else 'review',canonical(value)))
    summary={'schema_version':1,'key':m['key'],'title':m['title'],'gltf':m['gltf'],'authority':'decoded-glb-bytes','artifact_sha256':sha,'coordinate_system':'glTF 2: right-handed, Y up; matrices column-major; declared linear unit meters','joint_count':len(bones),'skin_count':len(g.get('skins',[])),'clip_count':len(clips),'topology_name_signature_sha256':digest(canonical(sorted(topology,key=lambda p:p[0])).encode()),'influence_histogram':dict(influence_hist),'weight_count_scope':'Positive influences counted over exported primitive vertices, including UV/material seam duplication and mesh instances. This is not the unique source-FBX vertex count.','validations':validation,'source':m.get('source',{}),'semantic_limits':['No attack, idle, damage or gameplay labels are established by track names.','Anatomical labels are unverified name heuristics.','Matching names or hierarchy does not prove retarget compatibility.']}
    if m.get('preview_review'):summary['preview_review']={**m['preview_review'],'authority':'analyst-visual-observation'}
    report={**summary,'bones':bones,'clips':clips};(PUBLIC/(m['key']+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    db.execute('UPDATE models SET summary_json=? WHERE key=?',(canonical(summary),m['key']))
    return report

def compare(a,b):
    buckets=collections.defaultdict(list)
    for bone in b['bones']:buckets[norm(bone['name'])].append(bone)
    pairs=[];unmatched=[]
    for bone in a['bones']:
        matches=buckets[norm(bone['name'])]
        if len(matches)==1:
            match=matches[0];pairs.append({'source_node':bone['node'],'source':bone['name'],'target_node':match['node'],'target':match['name'],'basis':'normalized-name-only','status':'candidate-not-tested','same_normalized_parent':norm(bone['parent_name'] or '')==norm(match['parent_name'] or '')})
        else:unmatched.append({'name':bone['name'],'node':bone['node'],'reason':'ambiguous-name' if matches else 'no-name-match'})
    return {'source':a['key'],'target':b['key'],'source_joint_count':len(a['bones']),'target_joint_count':len(b['bones']),'candidate_count':len(pairs),'same_parent_candidate_count':sum(p['same_normalized_parent'] for p in pairs),'candidates':pairs,'unmatched_source':unmatched,'status':'name-and-parent-screening-only','retarget_tested':False,'limitations':['No motion was transferred.','Proportions, rest rotations, axes, contacts and appendage function still need verification.']}

def main():
    catalog=json.loads((CAT/'gallery.json').read_text('utf-8'));models=[m for m in catalog['models'] if m.get('external_asset') and m.get('status')=='ready' and (m.get('asset_analysis',{}).get('bones',0)>0 or m.get('asset_analysis',{}).get('animations',0)>0)]
    if DB.exists():
        backups=ROOT/'database-revisions';backups.mkdir(exist_ok=True)
        name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite'
        source_db=sqlite3.connect(DB);backup_db=sqlite3.connect(backups/name);source_db.backup(backup_db);backup_db.close();source_db.close()
    db=sqlite3.connect(DB);db.executescript(SCHEMA);db.execute('PRAGMA user_version=1');run=datetime.datetime.now(datetime.timezone.utc).isoformat();db.execute('INSERT INTO runs VALUES(?,?,?,?)',(run,run,'rig-database parser v1 / '+digest(pathlib.Path(__file__).read_bytes()),canonical(['GLB decoding is separate from FBX import and REA archive inventory.'])))
    reports={}
    for m in models:
        if '--reuse-unchanged' in sys.argv:
            previous=db.execute('SELECT artifact_sha256 FROM models WHERE key=?',(m['key'],)).fetchone();cached=PUBLIC/(m['key']+'.json')
            if previous and cached.exists():
                current_sha=digest((CAT/m['gltf']).read_bytes());report=json.loads(cached.read_text('utf-8'))
                if current_sha!=previous[0]:raise ValueError('Artifact changed: material revisions must be separately verified '+m['key'])
                if report.get('artifact_sha256')==current_sha:
                    reports[m['key']]=report;print('REUSED '+m['key'],flush=True);continue
        reports[m['key']]=observe(m,db,run);print('INDEXED '+m['key'],flush=True)
    source=json.loads((ROOT/'sett-fbx-observation.json').read_text('utf-8'));primary=reports[PRIMARY]
    for arm in source['armatures']:
        for b in arm['bones']:db.execute('INSERT OR REPLACE INTO source_bones VALUES(?,?,?,?,?)',(PRIMARY,b['index'],b['name'],b['parent'],canonical(b)))
    for i,a in enumerate(source['actions']):db.execute('INSERT OR REPLACE INTO source_actions VALUES(?,?,?)',(PRIMARY,i,canonical(a)))
    source_names={b['name']:b for arm in source['armatures'] for b in arm['bones']};target_names={b['name']:b for b in primary['bones']}
    correlation={'source_joint_count':len(source_names),'export_joint_count':len(target_names),'source_only_names':sorted(source_names.keys()-target_names.keys()),'export_only_names':sorted(target_names.keys()-source_names.keys()),'parent_name_disagreements':[n for n in source_names.keys()&target_names.keys() if source_names[n]['parent']!=target_names[n]['parent_name']],'source_fps':source['scene_fps']/source['scene_fps_base'],'source_actions':[{'name':a['name'],'frame_range':a['frame_range'],'curve_count':a['curve_count'],'keyframe_count':a['keyframe_count']} for a in source['actions']],'limitations':['Bone positions in Blender armature space and glTF world space are not directly comparable without basis and object transforms.','Matching names and parents does not establish identical deformation or animation values.']}
    primary['fbx_correlation']=correlation;primary['fbx_observation']=source
    pose_report=ROOT/'sett-pose-verification.json'
    if pose_report.exists():
        pose_data=json.loads(pose_report.read_text('utf-8'))
        if pose_data['derived_glb_sha256']==primary['artifact_sha256'] and pose_data['source_sha256']==source['source_sha256']:primary['sampled_pose_verification']=pose_data
    snapshots=ROOT/'snapshots';snapshots.mkdir(exist_ok=True)
    for p in [pathlib.Path(source['source_path']),CAT/next(m['gltf'] for m in models if m['key']==PRIMARY),pathlib.Path(r'E:\l2-local\descarga de assets\sett.zip')]:
        raw=p.read_bytes();sha=digest(raw);dst=snapshots/(sha+p.suffix.lower())
        if not dst.exists():dst.write_bytes(raw)
        assert digest(dst.read_bytes())==sha
        db.execute('INSERT OR REPLACE INTO artifacts VALUES(?,?,?,?,?)',(sha,str(p),len(raw),p.suffix.lower()[1:],str(dst)))
    with zipfile.ZipFile(r'E:\l2-local\descarga de assets\sett.zip') as z:
        member=z.read('source/Sett-1.fbx');assert digest(member)==source['source_sha256'];correlation['fbx_matches_zip_member_sha256']=True
    rea=ROOT/'rea-sett-evidence.json';bundle=json.loads(rea.read_text('utf-8'));db.execute('INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?)',('rea-sett-bundle','shipped-artifact/archive-inventory',str(rea),digest(rea.read_bytes()),canonical(['Archive inventory does not decode rig semantics.'])))
    (PUBLIC/(PRIMARY+'.json')).write_text(json.dumps(primary,ensure_ascii=False,indent=2),encoding='utf-8')
    comparisons=[]
    for key in ['ext3_0ce679770218e2','ext3_9cb1bce8c5b96e']:
        if key in reports:comparisons.append(compare(primary,reports[key]))
    (PUBLIC/'sett-comparisons.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2),encoding='utf-8')
    index={'schema_version':1,'primary':PRIMARY,'models':[{k:r[k] for k in ['key','title','gltf','joint_count','clip_count','artifact_sha256','topology_name_signature_sha256']} for r in reports.values()],'comparisons':'sett-comparisons.json'}
    (PUBLIC/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    latest=json.loads((CAT/'gallery.json').read_text('utf-8'))
    for m in latest['models']:
        if m['key'] in reports:
            r=reports[m['key']];m['rig_analysis']={'schema_version':1,'path':'rig-data/'+m['key']+'.json','artifact_sha256':r['artifact_sha256'],'joint_count':r['joint_count'],'clip_count':r['clip_count']}
    target=CAT/'gallery.rigs.tmp';target.write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf-8');target.replace(CAT/'gallery.json')
    db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall()
    db.close();(ROOT/'sett-correlation.json').write_text(json.dumps(correlation,ensure_ascii=False,indent=2),encoding='utf-8');print('DATABASE_COMPLETE '+str(len(reports)),flush=True)

if __name__=='__main__':main()
