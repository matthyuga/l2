"""Recover only fully identical body/UV/topology layouts across renamed assets."""
# Import helper definitions without executing the matching/mutation section.
from pathlib import Path
import json,copy,collections,sys,concurrent.futures
HERE=Path(__file__).resolve().parent
source=(HERE/'repair_materials.py').read_text(encoding='utf8')
namespace={'__file__':str(HERE/'repair_materials.py')}
exec(compile(source[:source.index('# Build a compact exact-material index')],str(HERE/'repair_materials.py'),'exec'),namespace)
R=namespace['R'];OUT=namespace['OUT'];BACK=namespace['BACK'];catalog=namespace['catalog'];load=namespace['load'];signature=namespace['signature'];clone_material=namespace['clone_material']
def backup(path):
 p=BACK/path;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_bytes((R/path).read_bytes())
groups=namespace['models'];paths=[path for path in groups if '/SkeletalMesh/'in path and len(load(path).get('materials',[]))>0 and groups[path][0].get('category') in ['NPC','Monstruos','Bosses'] and len(load(path).get('nodes',[]))>12]
by_signature=collections.defaultdict(list);sigs={}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for i,(path,sig) in enumerate(zip(paths,ex.map(signature,paths))):
  sigs[path]=sig
  if sig:by_signature[(sig,len(load(path)['materials']))].append(path)
  if i%400==0:print('BODY_SIGNATURE',i,'/',len(paths),flush=True)
changes=[];dirty={}
for path in paths:
 g=load(path);missing=[i for i,mat in enumerate(g['materials']) if 'baseColorTexture'not in mat.get('pbrMetallicRoughness',{})]
 if not missing:continue
 for other in by_signature[(sigs[path],len(g['materials']))]:
  if other==path:continue
  src=load(other)
  if not all('baseColorTexture'in src['materials'][i].get('pbrMetallicRoughness',{}) for i in missing):continue
  backup(path)
  for i in missing:
   g['materials'][i]=clone_material(g,src,src['materials'][i],other,path)
   changes.append({'target':path,'slot':i,'donor':other,'signature':sigs[path],'method':'identical_body_uv_topology_renamed'})
  dirty[path]=g;break
for path,g in dirty.items():
 (R/path).write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 total=len(g['materials']);count=sum('baseColorTexture'in mat.get('pbrMetallicRoughness',{}) for mat in g['materials'])
 for m in groups[path]:
  m['material_count']=total;m['textured_materials']=count
  old=m.setdefault('material_repair',{'date':'2026-10-23','recovered_slots':[],'methods':[],'representative':True})
  old['methods']=sorted(set(old['methods']+['identical_body_uv_topology_renamed']));old['recovered_slots']=sorted(set(old['recovered_slots']+[c['slot'] for c in changes if c['target']==path]))
  m['note']=m.get('note','').replace('Algunos materiales se muestran sin textura.','').strip()+' Vista representativa recuperada de un cuerpo con geometría, UV y topología idénticas.'
(R/'gallery.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'body-matches.json').write_text(json.dumps({'changes':changes},ensure_ascii=False,indent=2),encoding='utf8')
render=[m for m in catalog['models'] if m.get('gltf')in dirty]
(OUT/'render-bodies.json').write_text(json.dumps({'models':render},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'changed_views':len(dirty),'changed_cards':len(render),'slots':len(changes)}),flush=True)
