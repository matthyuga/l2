import json
from pathlib import Path
root=Path(__file__).resolve().parent
d=json.loads((root/'inventory.json').read_text())
active=next(v for v in d['variants'] if v['directory'].endswith('system-hud'))
pattern=('Input','Keyboard','KeyState','Foreground','Focus')
summary=[]
for f in active['files']:
    pe=f['pe']
    if not pe:continue
    summary.append({'file':f['file'],'architecture':pe['architecture'],'imports':[{'module':m.get('module'),'functions':[s for s in m.get('functions',[]) if s and any(p.lower() in s.lower() for p in pattern)]} for m in pe['imports'] if any(s and any(p.lower() in s.lower() for p in pattern) for s in m.get('functions',[]))]})
(root/'active-input-imports.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
