import UnityPy,json,hashlib
from collections import Counter
from pathlib import Path
out=Path(__file__).parent
rows=[]
for name in ['00.unity3d','04.unity3d']:
 p=Path(r'K:\JUEGOS\KOIKATSU 22\abdata\studio\anime')/name
 e=UnityPy.load(str(p)); clips=[]
 for o in e.objects:
  if o.type.name!='AnimationClip':continue
  d=o.read(); m=d.m_MuscleClip; c=m.m_Clip.data
  clips.append({'path_id':o.path_id,'name':d.m_Name,'fps':d.m_SampleRate,'duration_seconds':m.m_StopTime-m.m_StartTime,'legacy':d.m_Legacy,'binding_count':len(d.m_ClipBindingConstant.genericBindings),'dense_frames':c.m_DenseClip.m_FrameCount,'dense_curves':c.m_DenseClip.m_CurveCount,'stream_words':len(c.m_StreamedClip.data),'constant_values':len(c.m_ConstantClip.data)})
 rows.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'types':dict(Counter(o.type.name for o in e.objects)),'clips':clips})
(out/'studio-animation-sample.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Cataloged',sum(len(r['clips']) for r in rows),'clip records. No motion conversion performed.')
