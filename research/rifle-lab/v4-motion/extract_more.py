import sys,json,importlib.util,re
from pathlib import Path
import UnityPy
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('existing',r'E:\l2-local\research\dust2-animation-study\studio\extract_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
bones,tos=m.extract_rig()
source=ROOT.parent/'motions/mixamo_gun_part2.unity3d';m.SOURCE=source
e=UnityPy.load(str(source))
for name in ['Rifle Idle 2','Rifle Walk In Place']:
 o=next(o for o in e.objects if o.type.name=='AnimationClip' and o.read().m_Name==name)
 d=m.decode_clip(o,bones,tos)
 d['source']['zip_member']='abdata/studio/anime/mixamo_gun_part2.unity3d'
 out=ROOT/(re.sub(r'[^A-Za-z0-9]+','_',name)+'.motion.json');out.write_text(json.dumps(d,separators=(',',':')),encoding='utf-8')
 print(out.name,len(d['frames']),d['validation'],flush=True)
