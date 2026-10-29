from pathlib import Path
import json,re,subprocess,collections
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
STAGE=ROOT/'stage';STAGE.mkdir(exist_ok=True)
def read(p):
 b=p.read_bytes()
 if b.startswith((b'\xff\xfe',b'\xfe\xff')):return b.decode('utf-16')
 try:return b.decode('utf-8-sig')
 except UnicodeDecodeError:return b.decode('cp1252',errors='replace')
def excluded(p):return bool(re.search(r'(^|[ /_\\-])(h5|high.?five)([ /_\\.-]|$)',str(p),re.I))
packs=json.loads((ROOT/'audit.json').read_text())
jobs=[];result=[]
for pi,pack in enumerate(packs,1):
 key=pack['key'];assets={};mapping={};rows=[];names={};seen={}
 for f in pack['files']:
  p=Path(f['path'])
  if excluded(f['relative']):continue
  if p.suffix.lower() in ('.u','.ukx','.utx','.usx'):
   low=p.stem.lower()
   if low in assets:
    assert assets[low]['sha256']==f['sha256'],('Conflicting packages',key,p)
    continue
   assets[low]=f;mapping[low]=f'EB{pi:02d}_{p.stem}'
 for low,f in assets.items():
  p=Path(f['path']);dest=STAGE/'assets'/key/(mapping[low]+p.suffix.lower())
  jobs.append('\t'.join([key,str(p),str(dest),p.stem,mapping[low]]))
 for f in pack['files']:
  p=Path(f['path'])
  if p.suffix.lower() not in ('.txt','.xml','.sql') or excluded(f['relative']):continue
  for line in read(p).splitlines():
   fields=line.rstrip('\r').split('\t')
   if len(fields)>2 and fields[0].isdigit() and int(fields[0])>=3 and not fields[1].isdigit():
    names.setdefault(int(fields[0]),fields[1])
   if len(fields) not in (91,92,332) or fields[0] not in ('0','1') or not fields[1].isdigit():continue
   if fields[0]=='0' and len(fields)==91:
    assert fields[31].isdigit(),(key,'unrecognized short weapon layout')
    fields.insert(31,'')
   if (fields[0]=='0' and len(fields)!=92) or (fields[0]=='1' and len(fields)!=332):continue
   signature=tuple(fields)
   if signature in seen:continue
   seen[signature]=True
   rows.append({'kind':'weapon' if fields[0]=='0' else 'armor','old_id':int(fields[1]),'fields':fields,'source':f['relative']})
 # Multiple files can contain the same ID with alternate glow. Choose first, except distinct types.
 # Preserve different color/glow versions even when the vendor reused an ID.
 for row in rows:
  old=row['old_id'];row['name']=names.get(old,pack['name']+' '+str(old))
  row['fields']=[re.sub(r'^([A-Za-z0-9_\-]+)\.',lambda m:mapping.get(m[1].lower(),m[1])+'.',v) for v in row['fields']]
 result.append({'key':key,'name':pack['name'],'batch':pack['batch'],'mapping':mapping,'assets':len(assets),'items':rows})
 print(key,len(assets),'assets',len(rows),'items')
(STAGE/'jobs.tsv').write_text('\n'.join(jobs),encoding='utf-8')
(STAGE/'parsed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TOTAL',sum(len(p['items']) for p in result),len(jobs))
