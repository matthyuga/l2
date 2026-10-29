import pathlib,json,sys,hashlib,bpy
from io_scene_fbx import parse_fbx
ROOT=pathlib.Path(__file__).resolve().parent;MASTER=ROOT.parent/'external-assets-20261028';OUT=ROOT/'source-structure';OUT.mkdir(exist_ok=True)
keys=json.loads((ROOT/'keys.json').read_text('utf-8'))
def decode(x):return x.decode('utf-8',errors='replace').split('\0')[0] if isinstance(x,bytes) else x
for key in keys:
 job=json.loads((MASTER/'jobs'/(key+'.json')).read_text('utf-8'));path=pathlib.Path(job['input']);root,version=parse_fbx.parse(str(path));objects=next(e for e in root.elems if e.id==b'Objects');counts={};clips=[];totalkeys=0
 for e in objects.elems:
  typ=decode(e.id);counts[typ]=counts.get(typ,0)+1
  if e.id==b'AnimationStack':
   props=next((v for v in e.elems if v.id==b'Properties70'),None);times={}
   for prop in props.elems if props else []:
    if prop.id==b'P' and decode(prop.props[0]) in ['LocalStart','LocalStop','ReferenceStart','ReferenceStop']:times[decode(prop.props[0])]=int(prop.props[-1])
   clips.append({'name':decode(e.props[1]),'fbx_ticks':times,'local_duration_seconds':(times.get('LocalStop',0)-times.get('LocalStart',0))/46186158000})
  if e.id==b'AnimationCurve':
   kt=next((v for v in e.elems if v.id==b'KeyTime'),None)
   if kt is not None:totalkeys+=len(kt.props[0])
 report={'key':key,'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'authority':'original-binary-FBX-structure','binary_version':version,'object_counts':counts,'animation_stacks':clips,'scalar_key_count':totalkeys,'limitations':['Structural counts and declared stack times; no playback or skin deformation certified.']}
 (OUT/(key+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('STRUCTURE',key,len(clips),totalkeys,flush=True)
