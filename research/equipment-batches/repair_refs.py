from pathlib import Path
import json,collections,re
ROOT=Path(__file__).resolve().parent;STAGE=ROOT/'stage'
packs=json.loads((STAGE/'parsed.json').read_text());jobs=[l.split('\t') for l in (STAGE/'jobs.tsv').read_text().splitlines()]
exports={};imports=collections.defaultdict(list);globalrefs=collections.defaultdict(list);prefixes={j[4].lower():j[3] for j in jobs};leafrefs=collections.defaultdict(list);owners={}
for l in (STAGE/'objects.tsv').read_text().splitlines():
 key,typ,ref,cls=l.split('\t')
 if typ=='E':
  exports[ref.lower()]=ref
  owners[ref.lower()]=key
  prefix,obj=ref.split('.',1);old=prefixes[prefix.lower()];globalrefs[(old+'.'+obj).lower()].append(ref)
  leafrefs[(prefix+'.'+obj.split('.')[-1]).lower()].append(ref)
 else:imports[key].append(ref)
existing={p.stem.lower() for sub in ['system-hud','system','animations','systextures','textures','staticmeshes','sounds'] for p in (Path('E:/l2')/sub).glob('*') if p.is_file()}
fixes=[];unresolved=[];crossmaps={}
for p in packs:
 inverse={v.lower():k for k,v in p['mapping'].items()};mp={}
 for r in p['items']:
  for idx,v in enumerate(r['fields']):
   m=re.match(r'^([A-Za-z_][A-Za-z0-9_\-]*)\.(.+)$',v)
   if not m:continue
   prefix,obj=m.groups();old=inverse.get(prefix.lower(),prefix)
   if v.lower() in exports or prefix.lower() in existing:continue
   opts=globalrefs.get((old+'.'+obj).lower(),[]) or leafrefs.get(v.lower(),[])
   if not opts and obj.lower()==old.lower():opts=leafrefs.get((prefix+'.'+prefix).lower(),[])
   if not opts:
    opts=[ref for ref in exports.values() if prefixes[ref.split('.')[0].lower()]==old and ref.split('.')[-1].lower()==obj.lower()]
   if not opts:
    local=[ref for ref in exports.values() if owners[ref.lower()]==p['key'] and ref.split('.')[-1].lower()==obj.split('.')[-1].lower()]
    if len(local)==1:opts=local
   if not opts and p['key']=='b1-13-angry-wings' and 'GiantBird_Skel_Wings' in obj:
    race=obj.split('_')[0];target=f'{race}_{race}_GiantBird_Skel_Wings'.lower()
    opts=[ref for ref in exports.values() if owners[ref.lower()]==p['key'] and ref.split('.')[-1].lower()==target]
   if opts:
    r['fields'][idx]=opts[0];fixes.append({'pack':p['key'],'from':v,'to':opts[0]})
    if opts[0].split('.')[0].lower()!=prefix.lower():mp[prefix]=opts[0].split('.')[0];mp[old]=opts[0].split('.')[0]
   else:unresolved.append({'pack':p['key'],'old_id':r['old_id'],'column':idx,'ref':v})
 # Resolve imported packages that did not arrive with the pack.
 for ref in imports[p['key']]:
  prefix=ref.split('.')[0];old=inverse.get(prefix.lower(),prefix)
  if prefix.lower() in existing or any(x.startswith(prefix.lower()+'.') for x in exports):continue
  matches=[v[0].split('.')[0] for k,v in globalrefs.items() if k.startswith(old.lower()+'.')]
  if matches:mp[prefix]=matches[0];mp[old]=matches[0]
 crossmaps[p['key']]=mp
(STAGE/'repaired.json').write_text(json.dumps(packs,indent=2))
(STAGE/'reference-repairs.json').write_text(json.dumps({'fixes':fixes,'unresolved':unresolved,'crossmaps':crossmaps},indent=2))
patchjobs=[]
for j in jobs:
 key,src,dest,old,new=j
 if key not in crossmaps or not crossmaps[key]:continue
 if any(ref.lower().startswith(new.lower()+'.') for ref in exports):patchjobs.append('\t'.join([key,dest,dest,old,new]))
for key,mp in crossmaps.items():
 for old,new in mp.items():patchjobs.append('\t'.join([key,'','',old,new]))
(STAGE/'patch-jobs.tsv').write_text('\n'.join(patchjobs),encoding='utf-8')
print('REPAIRED',len(fixes),'UNRESOLVED',len(unresolved),'PACKAGES TO PATCH',sum(bool(j.split('\t')[1]) for j in patchjobs))
counts=collections.Counter(x['pack'] for x in unresolved)
print(counts)
