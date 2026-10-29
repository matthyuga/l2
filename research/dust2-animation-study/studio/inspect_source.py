import UnityPy,json
from collections import Counter
from pathlib import Path
base=Path(r'K:\JUEGOS\KOIKATSU 22\abdata\chara')
for fn in ['oo_base.unity3d','mm_base.unity3d']:
 e=UnityPy.load(str(base/fn)); print(fn,Counter(o.type.name for o in e.objects))
 for o in e.objects:
  if o.type.name in ['Avatar','Animator','GameObject']:
   d=o.read();print(o.type.name,o.path_id,getattr(d,'m_Name',''))
e=UnityPy.load(r'K:\JUEGOS\KOIKATSU 22\abdata\studio\anime\00.unity3d')
o=next(o for o in e.objects if o.path_id==8950776005834115444); d=o.read();t=o.read_typetree()
Path(r'E:\l2-local\research\dust2-animation-study\studio\squat_raw.json').write_text(json.dumps(t,indent=2))
print('CLIP',d.m_Name,'bindings',t['m_ClipBindingConstant']['genericBindings'][:4]);print('STREAM',t['m_MuscleClip']['m_Clip']['data']['m_StreamedClip'].keys())
