import pathlib,json,numpy as np
CAT=pathlib.Path(__file__).resolve().parents[1]/'model-catalog'
for ref in ['Superion_S/StaticMesh/superion_statue_01','Superion_Du_S/StaticMesh/superion_boss_main01','Superion_S/StaticMesh/superion_20_landmark_01_vc1']:
 p=CAT/'exports'/(ref+'.gltf');d=json.loads(p.read_text());buffers=[(p.parent/b['uri']).read_bytes() for b in d['buffers']]
 def accessor(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];typ={5126:'f4',5123:'u2',5125:'u4'}[a['componentType']];components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  return np.frombuffer(buffers[v['buffer']],dtype=typ,count=a['count']*components,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,components)
 pr=d['meshes'][0]['primitives'][0];pos=accessor(pr['attributes']['POSITION']);norm=accessor(pr['attributes']['NORMAL']);ind=accessor(pr['indices']).ravel().reshape(-1,3)
 geometric=np.cross(pos[ind[:,1]]-pos[ind[:,0]],pos[ind[:,2]]-pos[ind[:,0]]);nlength=np.linalg.norm(geometric,axis=1);geometric/=np.maximum(nlength[:,None],1e-15)
 dot=(geometric*norm[ind[:,0]]).sum(axis=1)
 print(ref,'norm-length',np.percentile(np.linalg.norm(norm,axis=1),[0,50,100]),'agreement',np.percentile(dot[nlength>1e-6],[0,50,100]),'uv',accessor(pr['attributes']['TEXCOORD_0']).min(axis=0),accessor(pr['attributes']['TEXCOORD_0']).max(axis=0))
