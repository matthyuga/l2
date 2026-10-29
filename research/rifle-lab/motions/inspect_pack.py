from pathlib import Path
import zipfile, UnityPy, json, csv, io,hashlib
root=Path(r'E:\l2-local\research\rifle-lab\motions'); p=next(Path(r'K:\JUEGOS\KOIKATSU 22\mods\Sideloader Modpack - Animations\AgiShark').glob('*'));z=zipfile.ZipFile(p)
rows=[]
for n in z.namelist():
 if n.endswith('.csv'):
  for r in csv.reader(io.StringIO(z.read(n).decode('utf-8-sig',errors='replace'))):
   if len(r)>6 and any(w in r[3].lower() for w in ['rifle','reload','aim','cover']): rows.append(dict(zip(['id','group','category','display_name','bundle','asset','clip'],r[:7]),csv=n))
(root/'rifle_clip_catalog.json').write_text(json.dumps(dict(zipmod=str(p),rows=rows),indent=2),encoding='utf-8')
for part in [1,2,3]:
 n=f'abdata/studio/anime/mixamo_gun_part{part}.unity3d';data=z.read(n);(root/Path(n).name).write_bytes(data);e=UnityPy.load(data);clips=[o for o in e.objects if o.type.name=='AnimationClip'];print(part,len(clips));
 o=next(o for o in clips if o.read().m_Name=={1:'Fire Rifle',2:'Reload 1',3:'Taking Cover'}[part]);d=o.read_typetree();(root/f'clip{part}.keys.json').write_text(json.dumps(d,indent=2),encoding='utf-8'); print(o.path_id,d.keys());print('bindings',d.get('m_ClipBindingConstant',{}));print('avatar',[(o.path_id,o.read().m_Name) for o in e.objects if o.type.name=='Avatar'])
