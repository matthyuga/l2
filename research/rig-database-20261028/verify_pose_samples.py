import pathlib,json,math,bisect,statistics,sqlite3
from build_database import ROOT,CAT,PRIMARY,GLB,mul,matrix

def interpolate(a,b,t,rotation=False):
    if not rotation:return [(1-t)*x+t*y for x,y in zip(a,b)]
    dot=sum(x*y for x,y in zip(a,b))
    if dot<0:b=[-x for x in b];dot=-dot
    dot=max(-1,min(1,dot))
    if dot>.9995:
        q=[(1-t)*x+t*y for x,y in zip(a,b)];n=math.sqrt(sum(x*x for x in q));return [x/n for x in q]
    angle=math.acos(dot);den=math.sin(angle)
    return [(math.sin((1-t)*angle)*x+math.sin(t*angle)*y)/den for x,y in zip(a,b)]

def main():
    catalog=json.loads((CAT/'gallery.json').read_text('utf-8'));m=next(m for m in catalog['models'] if m['key']==PRIMARY);obj=GLB(CAT/m['gltf']);g=obj.g
    source=json.loads((ROOT/'sett-fbx-pose-samples.json').read_text('utf-8'));clip=g['animations'][0]
    tracks=[]
    for c in clip['channels']:
        if c['target']['path'] not in ['translation','rotation','scale']:continue
        s=clip['samplers'][c['sampler']];assert s.get('interpolation','LINEAR') in ['LINEAR','STEP']
        tracks.append((c['target'],[v[0] for v in obj.rows(s['input'])],list(obj.rows(s['output'])),s.get('interpolation','LINEAR')))
    parents={ch:i for i,n in enumerate(g['nodes']) for ch in n.get('children',[])};by_name={n.get('name'):i for i,n in enumerate(g['nodes'])}
    samples=[];all_diffs=[]
    for sample in source['samples']:
        t=sample['seconds'];nodes=[dict(n) for n in g['nodes']]
        for target,times,values,interpolation in tracks:
            i=max(0,min(bisect.bisect_right(times,t)-1,len(times)-1));j=min(i+1,len(times)-1)
            factor=0 if i==j or interpolation=='STEP' else max(0,min(1,(t-times[i])/(times[j]-times[i])))
            nodes[target['node']][target['path']]=interpolate(values[i],values[j],factor,target['path']=='rotation')
        worlds={}
        def world(i):
            if i not in worlds:worlds[i]=mul(world(parents[i]),matrix(nodes[i])) if i in parents else matrix(nodes[i])
            return worlds[i]
        errors=[]
        for name,expected in sample['joint_world_glTF_basis'].items():
            if name not in by_name:continue
            got=world(by_name[name])[12:15];distance=math.dist(expected,got);errors.append({'bone':name,'distance_world_units':distance})
        errors.sort(key=lambda v:v['distance_world_units'],reverse=True);diffs=[e['distance_world_units'] for e in errors];all_diffs+=diffs
        samples.append({'seconds':t,'compared_joints':len(diffs),'max_error_world_units':max(diffs),'mean_error_world_units':statistics.mean(diffs),'largest_errors':errors[:3]})
    report={'schema_version':1,'authority':'cross-parser-sampled-observation','source_sha256':source['source_sha256'],'derived_glb_sha256':m['rig_analysis']['artifact_sha256'],'samples':samples,'compared_joint_positions':len(all_diffs),'max_error_world_units':max(all_diffs),'tolerance_world_units':1e-4,'within_tolerance':max(all_diffs)<=1e-4,'limitations':['Only joint world positions at the listed 11 timestamps were compared.','This does not establish equality of all frames, orientations, mesh deformation, root motion, contacts or gameplay events.','Interpolation is decoded glTF LINEAR/STEP; quaternion LINEAR uses spherical interpolation.']}
    (ROOT/'sett-pose-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    path=CAT/'rig-data'/ (PRIMARY+'.json');data=json.loads(path.read_text('utf-8'));data['sampled_pose_verification']=report;path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    db=sqlite3.connect(ROOT/'rig-catalog.sqlite');db.execute('INSERT OR REPLACE INTO validations VALUES(?,?,?,?)',(PRIMARY,'FBX-vs-GLB-sampled-joint-world-positions','pass' if report['within_tolerance'] else 'review',json.dumps(report)));db.commit();db.close()
    print(json.dumps({'samples':len(samples),'positions':len(all_diffs),'max_error':max(all_diffs),'within_tolerance':report['within_tolerance']}))

if __name__=='__main__':main()
