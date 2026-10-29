"""Stage thirteen cosmetic hair accessories. Preserve original DAT record bytes."""
from pathlib import Path
import sys,struct,re,json,hashlib,subprocess,copy,collections,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent; PROJECT=ROOT.parents[3]; CLIENT=Path('E:/l2'); DATA=PROJECT/'server/game/data'
sys.path.insert(0,str(PROJECT/'research/airships'));from read_map import Package,Reader
CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';ASM=PROJECT/'tools-src/L2FileEdit/data/l2asm-disasm';FOOT=b'\x0cSafePackage\0'
STAGE=ROOT/'stage';STAGE.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(a):
 p=subprocess.run(list(map(str,a)),capture_output=True,timeout=90)
 if p.returncode:raise RuntimeError(p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace'))
 return p.stdout.decode(errors='replace')
def readtext(p):
 b=p.read_bytes()
 for enc in ['utf-8-sig','utf-16','cp1252']:
  try:return b.decode(enc)
  except UnicodeError:pass
 raise ValueError(p)
def setval(item,name,value):
 node=item.find(f"set[@name='{name}']")
 if node is None:node=ET.SubElement(item,'set',{'name':name})
 node.set('val',str(value))

def main():
 assert not (ROOT/'installation.json').exists(),'Already installed: do not rerun builder over live installation'
 manifests=json.loads((ROOT.parent/'download-manifest.json').read_text(encoding='utf8'))
 items={}
 for p in (DATA/'stats/items').rglob('*.xml'):
  for x in ET.parse(p).getroot().findall('item'):items[int(x.get('id'))]=x
 catalogs={};reserved=set(items)
 for name,idx in [('armorgrp',1),('itemname-e',0)]:
  raw=ROOT/(name+'.before.raw');txt=ROOT/(name+'.before.txt');ddf=ROOT/(name+'.ddf')
  run([CODEC,'-o',raw,CLIENT/'system-hud'/(name+'.dat')])
  run([ASM/'l2disasm.exe','-d',ASM/f'DAT_defs/Interlude/{name}.ddf','-e',ddf,'-o','e',raw,txt])
  lines=readtext(txt).splitlines();rows=[x.split('\t') for x in lines[1:] if x.strip()]
  catalogs[name]={'header':lines[0],'rows':{int(x[idx]):x for x in rows},'before_sha256':sha(CLIENT/'system-hud'/(name+'.dat'))}
  reserved.update(catalogs[name]['rows'])
 assert len(catalogs['armorgrp']['header'].split('\t'))==332
 acols=catalogs['armorgrp']['header'].split('\t');ncols=catalogs['itemname-e']['header'].split('\t')
 packs=[];assets=[];dedup={};objects={};old_to_new={};asset_index=0
 for e in manifests:
  if e['status']!='downloaded':continue
  folder=ROOT/'extracted'/e['id'];mapping={};sources={}
  for p in folder.rglob('*'):
   if not p.is_file() or p.suffix.lower() not in ['.ukx','.utx']:continue
   pkg=Package(p);key=hashlib.sha256(pkg.b).hexdigest()
   if key in dedup:new=dedup[key]
   else:
    asset_index+=1;new=('H'+f'{asset_index:04d}').ljust(len(p.stem),'X');assert len(new)==len(p.stem)
    dedup[key]=new;sources[p.stem.lower()]=(p,pkg,new)
   mapping[p.stem.lower()]=new
  old_to_new[e['id']]=mapping
  packs.append((e,folder,sources))
 # Same-length name table edits retain all native payload offsets and lazy array addresses.
 for e,folder,sources in packs:
  mp=old_to_new[e['id']]
  for old,(p,pkg,new) in sources.items():
   raw=bytearray(pkg.b);rr=Reader(pkg.b,struct.unpack_from('<i',pkg.b,16)[0]);changed=[]
   for name in pkg.names:
    count=rr.compact();pos=rr.p;rr.read(abs(count)*(2 if count<0 else 1));rr.read(4)
    if name.lower() in mp:
     replace=mp[name.lower()];enc='utf-16le' if count<0 else 'latin1';replacement=(replace+'\0').encode(enc)
     assert len(replacement)==abs(count)*(2 if count<0 else 1);raw[pos:pos+len(replacement)]=replacement;changed.append(name)
   rawpath=STAGE/'raw'/f'{new}{p.suffix.lower()}';rawpath.parent.mkdir(exist_ok=True);rawpath.write_bytes(raw)
   # Keep bytes otherwise intact: filenames and root import names isolate the package.
   target=STAGE/'assets'/rawpath.name;target.parent.mkdir(exist_ok=True)
   protocol=121 if p.suffix.lower()=='.utx' else 111
   run([CODEC,'-c','encode','-p',protocol,'-f',target.name,'-o',target,rawpath])
   check=STAGE/'raw'/(target.name+'.check');run([CODEC,'-f',target.name,'-o',check,target]);assert check.read_bytes()==rawpath.read_bytes()
   pp=Package(target);assert pp.b[:len(raw)]==rawpath.read_bytes()
   objects[new.lower()]={pp.ref(i+1).lower():pp.ref(i+1) for i in range(len(pp.exports))}
   assets.append({'source':str(p),'name':target.name,'new_package':new,'source_raw_sha256':hashlib.sha256(pkg.b).hexdigest(),'sha256':sha(target),'raw_sha256':sha(rawpath),'protocol':protocol,'renamed_names':changed,'exports':len(pp.exports)})
 # Include native exports only on demand and repair unique, redundant vendor group paths.
 native={p.stem.lower():p for sub in ['Animations','SysTextures','Textures','StaticMeshes','Sounds','system-hud','system'] for p in (CLIENT/sub).glob('*') if p.is_file()}
 refs_checked=[];repairs=[]
 def resolve(value,mp):
  if not re.match(r'^[A-Za-z_][\w-]*\.[\w]',value):return value
  prefix,obj=value.split('.',1);prefix=mp.get(prefix.lower(),prefix)
  obj='.'.join(mp.get(part.lower(),part) for part in obj.split('.'));value=prefix+'.'+obj
  key=prefix.lower()
  if key not in objects:
   assert key in native,'Missing package '+value
   p=Package(native[key]);objects[key]={p.ref(i+1).lower():p.ref(i+1) for i in range(len(p.exports))}
  opts=objects[key]
  if obj.lower() not in opts:
   candidates=[v for k,v in opts.items() if k.split('.')[-1]==obj.lower().split('.')[-1]]
   assert len(candidates)==1,('Missing/ambiguous object',value,candidates)
   fixed=prefix+'.'+candidates[0];repairs.append({'from':value,'to':fixed});value=fixed
  refs_checked.append(value);return value
 rows=[];report=[];nextid=28000
 for e,folder,_ in packs:
  mp=old_to_new[e['id']];vendor=[]
  for p in folder.rglob('*.txt'):
   if 'armorgrp' not in p.name.lower():continue
   vendor += [s.split('\t') for s in readtext(p).splitlines() if re.match(r'^1\t\d+\t',s)]
  assert vendor,e['id']
  for vi,v in enumerate(vendor):
   oldid=v[1]
   if len(v)!=332:
    assert e['id']=='baium-black-hair-interlude' and len(v)==532
    # This file is a newer chronicle layout with more fields and Kamael models.
    # Transfer its first fourteen race-specific mesh/material pairs to an IL template.
    matches=[(i,x) for i,x in enumerate(v) if re.match(r'^baium\.',x,re.I)]
    assert len(matches)>=14
    base=catalogs['armorgrp']['rows'][7680].copy()
    for group,(pos,mesh) in enumerate(matches[:14]):
     off=24+group*20;tex=next(x for x in v[pos+1:pos+12] if x.startswith('ct2aicon.'))
     base[off:off+20]=['1',mesh,'','','','1',tex,'','','','0','','','','','0','','','','']
    base[13]='ct2aicon.baium_dreads';v=base
   row=v.copy();name=e['title'].replace(' [Interlude]','')
   if len(vendor)>1:name+=' '+['Green','Orange','Magenta','Yellow'][vi]
   while nextid in reserved:nextid+=1
   iid=nextid;nextid+=1;reserved.add(iid);assert iid<32768
   row[1]=str(iid)
   # Hair slot as native raccoon ears; no fake S-grade, resistance or movement boosts.
   baseline=catalogs['armorgrp']['rows'][7680]
   for j in list(range(2,13))+list(range(18,24))+list(range(316,332)):row[j]=baseline[j]
   # Preserve an accessory preview (ACC_MT) from the first supported male human model.
   row[312:316]=['1',row[25],'1',row[30]]
   # One vendor assigns a male dwarf mesh to females despite shipping its female mesh.
   if e['id']=='baium-hair-interlude':row[125]='baium.Fdwarf_baium'
   for j,val in enumerate(row):
    if '.' in val:row[j]=resolve(val,mp)
   row[13]=resolve(v[13],mp)
   # Clear secondary icons and effects, retaining the neutral native equip sounds.
   for j in range(14,18):row[j]=''
   row[316]=''
   for g in range(14):
    off=24+20*g;assert row[off]=='1' and row[off+5]=='1',(name,g,row[off:off+10])
   item=copy.deepcopy(items[7680]);item.set('id',str(iid));item.set('name',name)
   for node in list(item):
    if node.tag!='set':item.remove(node)
   setval(item,'icon',row[13]);setval(item,'price','1');setval(item,'weight','10');setval(item,'enchant_enabled','false')
   nrow=catalogs['itemname-e']['rows'][7680].copy();nrow[0]=str(iid);nrow[1]=name;nrow[2]='';nrow[3]='a,Accesorio cosmetico de cabello. Sin bonificaciones de combate.\\0'
   rows.append((row,nrow,item));report.append({'id':iid,'name':name,'source_pack':e['id'],'source_id':oldid,'bodypart':'hair','race_sex_models':14,'cosmetic':True,'icon':row[13],'meshes':[row[25+20*g] for g in range(14)],'materials':[row[30+20*g] for g in range(14)]})
 assert len(rows)==13
 xml=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../xsd/items.xsd'})
 for a,n,x in rows:xml.append(x)
 ET.indent(xml,space='\t');ET.ElementTree(xml).write(STAGE/'hair-accessories.xml',encoding='utf8',xml_declaration=True)
 catmanifest={}
 for name,idx,num in [('armorgrp',1,0),('itemname-e',0,1)]:
  header=catalogs[name]['header'];newrows=[r[num] for r in rows]
  addition=STAGE/(name+'.add.txt');addition.write_text(header+'\n'+'\n'.join('\t'.join(r) for r in newrows)+'\n',encoding='utf8')
  extra=STAGE/(name+'.add.raw');run([ASM/'l2asm.exe','-d',ROOT/(name+'.ddf'),addition,extra])
  old=(ROOT/(name+'.before.raw')).read_bytes();new=extra.read_bytes();assert old.endswith(FOOT) and new.endswith(FOOT)
  count=struct.unpack_from('<I',old)[0];assert struct.unpack_from('<I',new)[0]==13
  raw=struct.pack('<I',count+13)+old[4:-len(FOOT)]+new[4:-len(FOOT)]+FOOT
  assert raw[4:len(old)-len(FOOT)]==old[4:-len(FOOT)]
  rawpath=STAGE/(name+'.raw');rawpath.write_bytes(raw)
  verified=STAGE/(name+'.verified.txt');run([ASM/'l2disasm.exe','-d',ROOT/(name+'.ddf'),'-o','e',rawpath,verified])
  oldlines=readtext(ROOT/(name+'.before.txt')).splitlines();afterlines=readtext(verified).splitlines()
  assert afterlines[1:len(oldlines)]==oldlines[1:] and len(afterlines)==len(oldlines)+13
  out=STAGE/(name+'.dat');run([CODEC,'-c','encode','-p','413','-o',out,rawpath])
  check=STAGE/(name+'.check.raw');run([CODEC,'-o',check,out]);assert check.read_bytes()==raw
  catmanifest[name]={'before_sha256':catalogs[name]['before_sha256'],'after_sha256':sha(out),'raw_sha256':sha(rawpath),'existing_records_preserved':count,'added':13}
 manifest={'items':report,'assets':assets,'catalogs':catmanifest,'reference_repairs':repairs,'checked_references':len(refs_checked),'status':'staged','source':str(ROOT.parent/'download-manifest.json')}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({'items':len(report),'ids':[r['id'] for r in report],'packages':len(assets),'reference_repairs':repairs,'checked_refs':len(refs_checked)},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
