import pathlib,json,struct,hashlib
ROOT=pathlib.Path(__file__).resolve().parent;MASTER=ROOT.parent/'external-assets-20261028';CAT=ROOT.parent/'model-catalog'
keys=json.loads((ROOT/'keys.json').read_text('utf-8'));catalog=json.loads((CAT/'gallery.json').read_text('utf-8'));by={m['key']:m for m in catalog['models']};rows=[]
for key in keys:
 m=by[key];assert m['status']=='ready',key+' is not ready';src=json.loads((ROOT/'source-structure'/(key+'.json')).read_text('utf-8'));assert hashlib.sha256(pathlib.Path(src['source']).read_bytes()).hexdigest()==src['source_sha256']
 with (CAT/m['gltf']).open('rb') as f:
  head=f.read(20);n=struct.unpack_from('<I',head,12)[0];g=json.loads(f.read(n))
 expected={v['name']:v for v in src['animation_stacks']};clips=[]
 for clip in g.get('animations',[]):
  parts=clip['name'].split('|');name=parts[-2] if len(parts)>2 else clip['name'];assert name in expected,(key,name)
  acc=[g['accessors'][s['input']] for s in clip['samplers']];duration=max(a['max'][0] for a in acc)-min(a['min'][0] for a in acc);wanted=expected[name]['local_duration_seconds'];error=abs(duration-wanted);assert error<.0001,(key,name,error)
  clips.append({'source_stack':name,'glb_clip':clip['name'],'source_duration_seconds':wanted,'glb_duration_seconds':duration,'absolute_error_seconds':error})
 assert len(clips)==len(expected),(key,len(clips),len(expected))
 source_materials=json.loads((ROOT.parent/'texture-audit-20261028/sources'/(key+'.json')).read_text('utf-8'));assert source_materials['status']=='inspected';missing=[v['filepath'] for v in source_materials['images'].values() if not v['size'][0]];assert not missing,(key,missing)
 rows.append({'key':key,'title':m['title'],'source_sha256_verified':True,'source_bound_images_present':True,'fbx_stack_count':len(expected),'glb_clip_count':len(clips),'clips':clips})
(ROOT/'source-export-verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print('SOURCE_EXPORT_PASS',len(rows),'models',sum(len(v['clips']) for v in rows),'clips')
