"""Compare full evaluated PSA motion after UKX export, not just parser success."""
import argparse, pathlib, json, hashlib
from write_l2_animation import psa
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('exported');ap.add_argument('package');ap.add_argument('--report',default='roundtrip-validation.json');a=ap.parse_args()
s,r=psa(a.source),psa(a.exported)
assert [b['name'] for b in s['bones']]==[b['name'] for b in r['bones']], 'Bone order differs'
assert len(s['frames'])==len(r['frames']) and abs(s['fps']-r['fps'])<1e-6,'Timing differs'
report=dict(source=str(pathlib.Path(a.source).resolve()),source_sequence=s['name'],exported_sequence=r['name'],bones=len(r['bones']),frames=len(r['frames']),fps=r['fps'])
for key in ['positions','rotations']:
    report['max_'+key+'_error']=max(abs(x-y) for sf,rf in zip(s['frames'],r['frames']) for sb,rb in zip(sf[key],rf[key]) for x,y in zip(sb,rb))
    assert report['max_'+key+'_error']<1e-6, key+' mismatch'
for key,path in [('source',a.source),('package',a.package),('exported',a.exported)]:
    report[key+'_sha256']=hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
report['runtime_validated']=False
pathlib.Path(a.report).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
