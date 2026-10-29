"""Export meshes referenced by authentic map placements, without adding every part to gallery."""
import sys,json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/airships'
sys.path.insert(0,str(ROOT/'research/model-catalog'));import build_gallery as b
b.OPTIONS=['-game=l2','-path='+str(D/'gracia-assets')]
original=b.run;b.run=lambda args:original([x.replace('.ukx','.usx') for x in args])
dest=D/'scene-meshes.json';meshes=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {}
scenes={
 'gludio':json.loads((D/'15_25-actors.json').read_text()),
 'keucereus':json.loads((D/'14_25-actors.json').read_text()),
 'aerial':json.loads((D/'13_25-actors.json').read_text())
}
for scene,actors in scenes.items():
 for ref in sorted({a['StaticMesh'] for a in actors}):
  if ref in meshes and meshes[ref]['textured_materials']==meshes[ref]['material_count']:continue
  m={'key':'scene_'+hashlib.sha1(ref.encode()).hexdigest()[:12],'mesh':ref,'npcs':[]}
  try:b.prepare(m);meshes[ref]=m;print('PREPARED',ref,m['textured_materials'],m['material_count'],flush=True)
  except Exception as e:print('FAILED',ref,str(e)[-300:],flush=True)
  dest.write_text(json.dumps(meshes,indent=2),encoding='utf-8')
  b.cache_file.write_text(json.dumps(b.texture_cache,indent=2),encoding='utf-8')
