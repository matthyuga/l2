"""Follow serialized UE2 material references, including unsupported GlowModifier.

Only gallery glTF/PNG/metadata are changed. No package, DLL or script is executed.
UModel only reads and exports Texture objects; all material chains are recorded.
"""
from pathlib import Path
import sys,json,re,copy,os,subprocess,collections,hashlib
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'research/model-catalog';OUT=Path(__file__).resolve().parent;BACK=ROOT/'backups/gallery-textures-20261023'
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package
NATIVE={k.lower():Path(v) for k,v in json.loads((ROOT/'research/npc-batch2/native-package-index.json').read_text()).items()}
UMODEL=ROOT/'research/amber-l2/tools/umodel.exe';EXPORT=R/'exports/material-recovery-20261023';EXPORT.mkdir(exist_ok=True)
catalog=json.loads((R/'gallery.json').read_text(encoding='utf8'));groups=collections.defaultdict(list)
for m in catalog['models']:
 if m.get('status')=='ready' and m.get('gltf'):groups[m['gltf']].append(m)
audit=json.loads((OUT/'audit-before.json').read_text(encoding='utf8'))['rows'];package_cache={};contexts={};plans={};resolved_cache={};events=[];errors=[];changes=[];dirty={}
text_overrides=collections.defaultdict(list)
for txt in (ROOT/'research/npc-batch2/packages').glob('*/assets/**/*.txt'):
 if 'npcgrp' not in txt.name.lower():continue
 raw=txt.read_bytes();text=raw.decode('utf16' if raw[:2]in [b'\xff\xfe',b'\xfe\xff'] else 'utf-8-sig',errors='replace')
 archive=txt.relative_to(ROOT/'research/npc-batch2/packages').parts[0]
 for line_no,line in enumerate(text.splitlines(),1):
  fields=line.split('\t')
  if len(fields)<5 or not fields[0].strip().isdigit() or '.'not in fields[2] or not fields[3].isdigit():continue
  refs=fields[4:4+int(fields[3])]
  if not any(refs):continue
  text_overrides[(archive,fields[2].lower())].append({'refs':refs,'source':str(txt.relative_to(ROOT)),'line':line_no,'npc_id':fields[0]})
for p in (ROOT/'research/npc-batch2/packages').glob('*/plan.json'):
 for item in json.loads(p.read_text(encoding='utf8')).get('models',[]):plans[item['key']]=item
def packages(m):
 key=m.get('asset_root','native')
 if key not in contexts:
  local={}
  if m.get('asset_root'):
   for f in (ROOT/m['asset_root']).rglob('*'):
    if f.suffix.lower() in ['.utx','.ukx','.u','.usx']:local.setdefault(f.stem.lower(),[]).append(f)
  contexts[key]=local
 return contexts[key]
def package(path):
 key=str(path.resolve())
 if key not in package_cache:
  package_cache[key]=Package(path)
 return package_cache[key]
def find_package(name,m):
 own=packages(m).get(name.lower(),[])
 if own:return sorted(own,key=lambda p:0 if p.suffix.lower()=='.utx' else 1)[0]
 return NATIVE.get(name.lower())
def export_texture(p,e,masked):
 name=e['name'];target=EXPORT/p.path.stem/'Texture'/(name+'.png')
 if not target.exists():
  command=[str(UMODEL),'-export','-png','-noanim','-nomesh','-nostat','-game=l2','-path='+str(p.path.parent),'-out='+str(EXPORT),str(p.path),name]
  proc=subprocess.run(command,capture_output=True,timeout=60)
  (OUT/('export-'+p.path.stem+'-'+name+'.log')).write_bytes(proc.stdout+proc.stderr)
  if proc.returncode or not target.exists():raise ValueError('Texture export failed: '+str(target))
 return {'file':str(target),'masked':masked,'source_package':str(p.path),'texture_object':name}
def resolve(ref,m,parent=None,chain=None,seen=None,masked=False):
 chain=[] if chain is None else chain;seen=set() if seen is None else seen
 if not ref or ref=='None':return None
 parts=ref.split('.')
 if parent and not find_package(parts[0],m):p=parent;name=parts[-1]
 else:
  path=find_package(parts[0],m)
  if not path:return None
  p=package(path);name=parts[-1]
 key=(str(p.path),name.lower())
 if key in seen:return None
 seen.add(key)
 e=next((e for e in p.exports if e['name'].lower()==name.lower()),None)
 if e is None:return None
 cl=p.ref(e['cl']).split('.')[-1];step={'package':str(p.path),'object':p.ref(p.exports.index(e)+1),'class':cl,'offset':e['offset'],'size':e['size']};chain=chain+[step]
 if cl=='Texture':
  props=p.props(e);masked=masked or props.get('bMasked',False)
  result=export_texture(p,e,masked);result['chain']=chain;return result
 props=p.props(e);step['properties']={k:v for k,v in props.items() if isinstance(v,(str,bool,int,float))}
 # Prefer actual color-bearing references. Normal/specular/opacity maps alone
 # must never be mistaken for the diffuse map.
 preferred=['Diffuse','Material','Material1','FallbackMaterial']
 for prop in preferred:
  child=props.get(prop)
  if not isinstance(child,str) or child=='None':continue
  result=resolve(child,m,p,chain,seen.copy(),masked or props.get('AlphaTest',False))
  if result:return result
 return None
def candidate_refs(m,g,slot):
 plan=plans.get(m['key'],{});overrides=plan.get('textures') or (m.get('npcs') or [{}])[0].get('textures',[])
 if not overrides:
  matches=text_overrides.get((m.get('archive_id'),m['mesh'].lower()),[])
  preferred=next((entry for entry in matches if str(m.get('source_npc_id'))==entry['npc_id']),None) or (matches[0] if matches else None)
  if preferred:overrides=preferred['refs']
 refs=[]
 matname=g['materials'][slot].get('name','');dummy=re.fullmatch(r'dummy_material_(\d+)',matname);index=int(dummy[1]) if dummy else slot
 if index<len(overrides) and overrides[index]:refs.append(overrides[index])
 log=ROOT/'research/npc-batch2/packages'/m.get('archive_id','')/'export-logs'/(m['key']+'.log') if m.get('archive_id') else R/'build-logs'/(m['key']+'.log')
 text=log.read_text(encoding='utf8',errors='replace') if log.exists() else ''
 missing=list(dict.fromkeys(pkg+'.'+obj for kind,obj,pkg in re.findall(r"WARNING: Import\((\w+)'([^']+)'\): package (\S+) was not found",text)))
 if dummy and len(missing)==len(g['materials']):refs.append(missing[index])
 loaded={name.lower():Path(path.strip()).stem+'.'+name for kind,name,path in re.findall(r'Loading (Texture|Shader|FinalBlend|Combiner|TexPanner|TexScaler|GlowModifier) (\S+) from package ([^\r\n]+)',text)}
 if matname.lower()in loaded:refs.append(loaded[matname.lower()])
 # No fuzzy texture-name guessing. Native shader names may be directly found
 # in one of the texture packages already declared by the model's overrides.
 if not dummy:
  for prefix in dict.fromkeys(ref.split('.')[0] for ref in overrides if '.'in ref):refs.append(prefix+'.'+matname)
 return list(dict.fromkeys(refs))


traces=[]
for path,entries in groups.items():
 m=entries[0]
 if 'serialized_native_material_chain' not in m.get('material_repair',{}).get('methods',[]):continue
 g=json.loads((R/path).read_text(encoding='utf8'))
 for slot,mat in enumerate(g.get('materials',[])):
  try:
   texture=g['textures'][mat['pbrMetallicRoughness']['baseColorTexture']['index']];uri=g['images'][texture['source']]['uri']
  except Exception:continue
  if 'material-recovery-20261023' not in uri:continue
  for ref in candidate_refs(m,g,slot):
   try:result=resolve(ref,m)
   except Exception:continue
   if result:
    traces.append({'gltf':path,'key':m['key'],'slot':slot,'reference':ref,**result});break
(OUT/'native-evidence-retraced.json').write_text(json.dumps({'traces':traces},ensure_ascii=False,indent=2),encoding='utf8')
print('Native serialized chains verified',len(traces),flush=True)
