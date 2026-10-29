from pathlib import Path
import zipfile, io, json, struct

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
assets=[]
def extract(z,dest):
    dest.mkdir(parents=True,exist_ok=True)
    for entry in z.infolist():
        if entry.is_dir():continue
        target=(dest/entry.filename).resolve()
        if not target.is_relative_to(dest.resolve()):raise ValueError('Unsafe archive path')
        if entry.file_size>300_000_000:raise ValueError('Unexpected oversized entry')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(entry))
        if target.suffix.lower()=='.zip':
            with zipfile.ZipFile(io.BytesIO(target.read_bytes())) as child:extract(child,target.with_suffix(''))

for index,p in enumerate(sorted((ROOT/'descarga de assets').glob('*cat*.zip'))):
    folder=OUT/'sources'/('cat-%02d'%(index+1))
    with zipfile.ZipFile(p) as z:extract(z,folder)
    models=[f for f in folder.rglob('*') if f.suffix.lower() in ['.glb','.fbx','.stl']]
    if len(models)!=1:raise ValueError((p.name,models))
    model=models[0];record=dict(key='web_cat_review_%02d'%(index+1),archive=p.name,source=str(model),folder=str(folder))
    if model.suffix.lower()=='.glb':
        data=model.read_bytes();n=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+n])
        record.update(triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g.get('meshes',[]) for p in m['primitives']),skins=len(g.get('skins',[])),animations=len(g.get('animations',[])))
    assets.append(record)
(OUT/'inventory.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
print('INSPECTED',len(assets))
