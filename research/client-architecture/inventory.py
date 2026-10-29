from pathlib import Path
import ast, struct, hashlib, json, re, math, collections
OUT=Path(__file__).resolve().parent
tree=ast.parse(Path('E:/l2-damage/analysis/inventory.py').read_text())
exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='pe')],type_ignores=[]),'reviewed-pe-parser','exec'))
root=Path('E:/l2')
names=['L2.exe','Core.dll','Engine.dll','NWindow.dll','WinDrv.dll','Window.dll','Interface.u','Interface.xdat','l2.ini','Option.ini','clmods.dll']
variants=[]
for d in sorted(root.glob('system*')):
    if not d.is_dir():continue
    lookup={p.name.lower():p for p in d.iterdir() if p.is_file()}
    files=[]
    for name in names:
        p=lookup.get(name.lower())
        if not p:continue
        b=p.read_bytes()
        files.append({'file':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'pe':pe(b) if p.suffix.lower() in ('.exe','.dll') else None})
    variants.append({'directory':str(d),'files':files})
assets=[]
for d in sorted(root.iterdir()):
    if not d.is_dir() or d.name.startswith('system'):continue
    fs=[p for p in d.iterdir() if p.is_file()]
    assets.append({'directory':d.name,'top_level_files':len(fs),'top_level_bytes':sum(p.stat().st_size for p in fs),'extensions':dict(collections.Counter(p.suffix.lower() for p in fs))})
(OUT/'inventory.json').write_text(json.dumps({'variants':variants,'assets':assets},indent=2),encoding='utf-8')
for v in variants:
    print(v['directory'])
    for f in v['files']:
        print(' ',f['file'],f['bytes'],f['sha256'][:16])
print('Asset directories',len(assets))
