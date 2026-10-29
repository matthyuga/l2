from pathlib import Path
import hashlib,json
s=Path(__file__).resolve().parent
m=json.loads((s/'installation.json').read_text())
for row in m['files']:
    p=Path(row['path'])
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['installed_sha256'], str(p)
b=json.loads((s/'baseline.json').read_text())['files'][0]
assert hashlib.sha256(Path(b['path']).read_bytes()).hexdigest()==b['before_sha256']
result={'status':'PASS','installed_files_verified':len(m['files']),'disk_core':'baseline, staged patch awaiting normal startup','visual_indicator':'pending user confirmation'}
(s/'final-installation-audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
