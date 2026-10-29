from pathlib import Path
import json,collections,copy,hashlib,struct,sys
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'research/model-catalog';O=Path(__file__).resolve().parent;B=ROOT/'backups/gallery-textures-20261023'
before=json.loads((B/'gallery.json').read_text(encoding='utf8'));catalog=json.loads((R/'gallery.json').read_text(encoding='utf8'))
pre={r['gltf']:r for r in json.loads((O/'audit-before.json').read_text(encoding='utf8'))['rows']}
after={r['gltf']:r for r in json.loads((O/'audit-after.json').read_text(encoding='utf8'))['rows']}
assert len(catalog['models'])==len(before['models'])
assert [m['key'] for m in catalog['models']]==[m['key'] for m in before['models']]
allowed={'note','textured_materials','material_count','material_repair','material_review'}
for old,new in zip(before['models'],catalog['models']):
 assert {k:v for k,v in old.items() if k not in allowed}=={k:v for k,v in new.items() if k not in allowed},new['key']
changed=[];recovered=0;unchanged=0
for path,row in after.items():
 assert 'error'not in row,(path,row.get('error'))
 assert not row.get('broken_images'),(path,row['broken_images'])
 delta=len(pre[path].get('missing_slots',[]))-len(row.get('missing_slots',[]))
 if delta>0:
  changed.append(path);recovered+=delta
  original=B/path;assert original.exists(),path
  g0=json.loads(original.read_text(encoding='utf8'));g1=json.loads((R/path).read_text(encoding='utf8'))
  material_keys={'materials','images','textures','samplers','extensionsUsed','extensionsRequired'}
  assert {k:v for k,v in g0.items() if k not in material_keys}=={k:v for k,v in g1.items() if k not in material_keys},('geometry changed',path)
 else:unchanged+=1
for m in catalog['models']:
 row=after.get(m.get('gltf'))
 if not row:status='unavailable';text='Vista no disponible';missing=[]
 elif row.get('authored_color_asset'):status='flat_color';text='Colores planos del recurso';missing=row.get('missing_slots',[])
 elif not row['used_materials']:status='no_material';text='Sin material declarado';missing=[]
 elif row.get('missing_slots'):status='pending';text='Texturas pendientes: '+str(len(row['missing_slots']))+' de '+str(row['used_materials'])+' materiales';missing=row['missing_slots']
 else:status='complete';text='Texturas completas';missing=[]
 m['material_review']={'status':status,'text':text,'missing_slots':missing}
 # Keep prior descriptive metadata. This field is the authoritative current
 # audit rather than stale importer counts or old material warnings.
(R/'gallery.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf8')
summary={'catalog_entries':len(catalog['models']),'unique_views_audited':len(after),'changed_views':len(changed),'changed_cards':sum(m.get('gltf')in changed for m in catalog['models']),'recovered_material_slots':recovered,'fully_recovered_views':sum(bool(pre[p].get('missing_slots')) and not after[p].get('missing_slots') for p in changed),'partially_recovered_views':sum(bool(after[p].get('missing_slots')) for p in changed),'remaining_non_color_views':sum(bool(r.get('missing_slots')) and not r.get('authored_color_asset') for r in after.values()),'intentional_color_views':sum(bool(r.get('missing_slots')) and r.get('authored_color_asset',False) for r in after.values()),'broken_image_links':0,'geometry_unchanged':True,'entry_keys_preserved':True,'changed_paths':changed,'statuses':dict(collections.Counter(m['material_review']['status'] for m in catalog['models']))}
(O/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
pending=[{'key':m['key'],'mesh':m['mesh'],'title':m['title'],'batch':m.get('batch'),'gltf':m.get('gltf'),**m['material_review']} for m in catalog['models'] if m['material_review']['status']=='pending']
(O/'pending-models.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k!='changed_paths'},ensure_ascii=False),flush=True)
