"""Audit all retained source files against their published origins."""
import json,pathlib,hashlib
D=pathlib.Path(__file__).resolve().parent
manifest=json.loads((D/'pride-manifest.json').read_text());expected={x[0].lower():x for x in manifest['archivos']};files=[]
for p in sorted((D/'gracia-assets').rglob('*')):
 if not p.is_file() or p.suffix=='.download':continue
 rel=p.relative_to(D/'gracia-assets').as_posix();e=expected[rel.lower()];digest=hashlib.sha256(p.read_bytes()).hexdigest()
 assert p.stat().st_size==e[1] and digest==e[2],rel
 files.append(dict(path='gracia-assets/'+rel,source='https://l2pride.us/updater/manifest.json',sha256=digest,size=p.stat().st_size,published_hash_verified=True))
for p in sorted((D/'superion-assets').rglob('*')):
 if not p.is_file() or p.suffix not in ['.usx','.utx','.unr']:continue
 rel=p.relative_to(D/'superion-assets').as_posix()
 files.append(dict(path='superion-assets/'+rel,source='https://launcher.exiliumworld.com/patch/'+rel+'.bz2',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=p.stat().st_size,published_hash_verified=False))
for p in (D/'helios-maps').rglob('*.unr'):
 files.append(dict(path=p.relative_to(D).as_posix(),source=json.loads((D/'helios-maps-source.json').read_text())['url'] if (D/'helios-maps-source.json').exists() else 'Helios remote solid 7z (extraction in progress)',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=p.stat().st_size,published_hash_verified=False))
out=dict(date='2026-10-12',file_count=len(files),total_bytes=sum(x['size'] for x in files),files=files)
(D/'all-downloads-audit.json').write_text(json.dumps(out,indent=2));print(out['file_count'],out['total_bytes'])
