from pathlib import Path
import subprocess,json,zipfile,hashlib,collections
ROOT=Path(__file__).resolve().parent
OUT=Path(r'E:\l2-local\descarga de assets\interfaces\2026-10-14')
UNRAR=Path(r'C:\Program Files\WinRAR\UnRAR.exe')
rows=[]
previous={x['file']:x for x in json.loads((ROOT/'archive-checks.json').read_text())} if (ROOT/'archive-checks.json').exists() else {}
for p in sorted(OUT.iterdir()):
 if p.suffix.lower() not in ('.rar','.zip'):continue
 if p.name in previous and previous[p.name]['bytes']==p.stat().st_size:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  if h.hexdigest()==previous[p.name]['sha256']:
   rows.append(previous[p.name]);continue
 if p.suffix.lower()=='.zip':
  with zipfile.ZipFile(p) as z:
   bad=z.testzip();names=z.namelist();valid=bad is None
  detail=bad
 else:
  q=subprocess.run([str(UNRAR),'t','-idq',str(p)],capture_output=True,timeout=240)
  listing=subprocess.run([str(UNRAR),'lb',str(p)],capture_output=True,timeout=30)
  names=listing.stdout.decode(errors='replace').splitlines();valid=q.returncode==0
  detail=q.stdout.decode(errors='replace')[-400:]+q.stderr.decode(errors='replace')[-400:]
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 row={'file':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest(),'archive_crc_ok':valid,'detail':detail,'entries':len(names),'extensions':dict(collections.Counter(Path(n).suffix.lower() for n in names)), 'ui_files':[n for n in names if any(s in n.lower() for s in ['interface.u','interface.xdat','nwindow.dll','engine.dll'])]}
 (ROOT/(p.stem+'-inventory.txt')).write_text('\n'.join(names),encoding='utf-8')
 rows.append(row);print(p.name,'CRC',valid,'entries',len(names),flush=True)
(ROOT/'archive-checks.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('TOTAL',len(rows),sum(r['bytes'] for r in rows),'bytes',flush=True)
