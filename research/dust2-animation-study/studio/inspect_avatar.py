import UnityPy,json
from pathlib import Path
p=Path(r'E:\l2-local\research\dust2-animation-study\studio')
e=UnityPy.load(r'K:\JUEGOS\KOIKATSU 22\abdata\chara\oo_base.unity3d')
for o in e.objects:
 if o.type.name in ['Avatar','Animator']:
  t=o.read_typetree();print(o.type.name,o.path_id,{k:str(v)[:250] for k,v in t.items() if k not in ['m_Avatar','m_TOS']}); print('TOS',str(t.get('m_TOS'))[:400]);(p/(str(o.path_id)+'.json')).write_text(json.dumps(t,indent=2))
