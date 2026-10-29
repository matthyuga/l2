import sys,json,importlib.util,hashlib,re
from pathlib import Path
import UnityPy
root=Path(r'E:\l2-local\research\rifle-lab\motions');spec=importlib.util.spec_from_file_location('existing',r'E:\l2-local\research\dust2-animation-study\studio\extract_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
bones,tos=m.extract_rig()
for part,names in [(1,['Idle Aiming','Fire Rifle']),(2,['Rifle Idle 1','Reload 1','Rifle Run In Place']),(3,['Taking Cover'])]:
 source=root/f'mixamo_gun_part{part}.unity3d';m.SOURCE=source;e=UnityPy.load(str(source))
 for name in names:
  o=next(o for o in e.objects if o.type.name=='AnimationClip' and o.read().m_Name==name)
  d=m.decode_clip(o,bones,tos);d['source']['zipmod']=r'K:\JUEGOS\KOIKATSU 22\mods\Sideloader Modpack - Animations\AgiShark\[AgiShark] Mixamo animations for CharaStudio v3.1.2.zipmod';d['source']['zip_member']=f'abdata/studio/anime/mixamo_gun_part{part}.unity3d';d['validation']['limitations']=['No runtime CharaStudio IK, constraints or look-at evaluated.','Generic Mixamo firearm animation; no AK-47/M16 weapon-specific association is encoded in Studio CSV.','Requires artistic L2 retargeting and hand/weapon contact verification.'];out=root/(re.sub(r'[^A-Za-z0-9]+','_',name)+'.motion.json');out.write_text(json.dumps(d,separators=(',',':')),encoding='utf-8'); print(out.name,json.dumps({k:v for k,v in d['validation'].items() if k!='unmatched_bindings'}), 'unmatched',len(d['validation']['unmatched_bindings']),flush=True)
