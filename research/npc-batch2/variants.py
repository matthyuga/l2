from pathlib import Path
import json,re,hashlib,os
ROOT=Path(r'E:\l2-local');S=ROOT/'research/npc-batch2';index={k:Path(v) for k,v in json.loads((S/'native-package-index.json').read_text()).items()};added=0
for p in (S/'packages').glob('*/plan.json'):
 j=json.loads(p.read_text(encoding='utf-8'));assets=p.parent/'assets';known={(m['mesh'].lower(),tuple(m.get('textures',[]))) for m in j['models']};src=j['source'];id=p.parent.name
 for textfile in assets.rglob('*.txt'):
  data=textfile.read_bytes();text=data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig',errors='replace')
  for line in text.splitlines():
   fields=line.split('\t')
   if len(fields)<5 or not fields[0].strip().isdigit() or not re.fullmatch(r'[A-Za-z0-9_]+\.[A-Za-z0-9_.]+',fields[2]):continue
   mesh=fields[2];pkg,obj=mesh.split('.',1);tex=fields[4:4+int(fields[3])] if fields[3].isdigit() else []
   if (mesh.lower(),tuple(tex)) in known:continue
   native=index.get(pkg.lower());local=next((f for f in assets.rglob(pkg+'.ukx')),None) or next((f for f in assets.rglob(pkg+'.u')),None)
   if not local and native and native.suffix.lower()=='.ukx':
    dep=assets/'NativeDependencies';dep.mkdir(exist_ok=True);local=dep/native.name
    if not local.exists():os.link(native,local)
   if not local:continue
   key='b2_'+hashlib.sha256((id+mesh+'|'+','.join(tex)).encode()).hexdigest()[:18]
   j['models'].append({'key':key,'mesh':mesh,'package':pkg,'extension':local.suffix,'kind':'SkeletalMesh','textures':tex,'source_id':fields[0],'archive_id':id,'archive_title':src['titulo'],'version':src['version_anunciada'],'asset_root':str(assets.relative_to(ROOT)).replace('\\','/'),'package_file':str(local),'source_archive':src['archivo']});known.add((mesh.lower(),tuple(tex)));added+=1
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
print('Texture variants/native resources',added)
