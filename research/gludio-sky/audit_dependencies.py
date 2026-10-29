from package_tools import *
import json
D=pathlib.Path(__file__).resolve().parent;stage=D/'stage';files={};cache={};names={}
for root in [stage,ROOT.parent/'l2']:
    for folder in ['Textures','StaticMeshes','system-hud','systextures','animations']:
        if not (root/folder).exists():continue
        for p in (root/folder).glob('*'):
            if p.suffix.lower() in ['.utx','.usx','.u','.ukx']:files.setdefault(p.stem.lower(),p)
def load(key):
    if key not in cache:
        cache[key]=Package(files[key]);names[key]={cache[key].ref(i+1).lower() for i in range(len(cache[key].exports))}
    return cache[key]
missing=[]
for path in list((stage/'Textures').glob('*'))+list((stage/'StaticMeshes').glob('*')):
    p=load(path.stem.lower())
    for i,imp in enumerate(p.imports):
        ref=p.ref(-i-1)
        if '.' not in ref:continue
        dep,obj=ref.split('.',1);dep=dep.lower()
        if ref.lower() in ['core.package','engine.staticmesh']:continue # Native classes, no script export.
        if dep not in files:missing.append([path.name,ref,'no package']);continue
        load(dep)
        if obj.lower() not in names[dep]:missing.append([path.name,ref,'no object'])
(D/'dependency-audit.json').write_text(json.dumps({'missing':missing,'packages':{k:str(files[k]) for k in cache}},indent=2))
print(json.dumps(missing,indent=2));print('Missing:',len(missing))
