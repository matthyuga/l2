import UnityPy,json
from pathlib import Path
out=[]
e=UnityPy.load(r'K:\JUEGOS\KOIKATSU 22\abdata\studio\info\00.unity3d')
for o in e.objects:
 if o.type.name=='MonoBehaviour':
  d=o.read()
  if d.m_Name.startswith('Anime_'):
   t=o.read_typetree();out.append(t)
Path(r'E:\l2-local\research\dust2-animation-study\studio\animation_ui_metadata.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for t in out:
 for r in t.get('list',[]):
  a=r['list']
  if len(a)>=7 and ('suwari' in a[-1] or 'squat' in a[-1] or 'm_action' in a[-1]): print(json.dumps(a,ensure_ascii=False))
