import json
from pathlib import Path
r=Path(r'E:\l2-local\research\rifle-lab\motions');rows=[]
for p in r.glob('*.motion.json'):
 d=json.loads(p.read_text());rows.append(dict(file=p.name,clip=d['source']['clip_name'],duration=d['duration_seconds'],fps=d['fps'],bone_count=len(d['bones']),samples=len(d['frames']),matched=d['validation']['matched_bindings'],unmatched=len(d['validation']['unmatched_bindings']),rig_sha256=d['source']['rig_sha256']))
(r/'extraction_summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
