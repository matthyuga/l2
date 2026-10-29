from pathlib import Path
import copy,json,re,struct,subprocess,xml.etree.ElementTree as ET,collections,hashlib
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];STAGE=ROOT/'stage';CLIENT=PROJECT.parent/'l2/system-hud'
CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';ASM=PROJECT/'tools-src/L2FileEdit/data/l2asm-disasm';FOOT=b'\x0cSafePackage\0'
def run(args):
 p=subprocess.run([str(a) for a in args],capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def setval(item,name,value):
 node=item.find("set[@name='%s']"%name)
 if node is None:node=ET.SubElement(item,'set',{'name':name})
 node.set('val',str(value))
allitems={}
for p in (PROJECT/'server/game/data/stats/items').rglob('*.xml'):
 for x in ET.parse(p).getroot().findall('item'):allitems[int(x.get('id'))]=x
base={};defs={};headers={};originals={};reserved=set(allitems)
for name,idcol in [('weapongrp',1),('armorgrp',1),('itemname-e',0)]:
 raw=STAGE/(name+'.before.raw');ddf=STAGE/(name+'.ddf');txt=STAGE/(name+'.before.txt')
 run([CODEC,'-o',raw,CLIENT/(name+'.dat')]);run([ASM/'l2disasm.exe','-d',ASM/f'DAT_defs/Interlude/{name}.ddf','-e',ddf,'-o','e',raw,txt])
 lines=txt.read_text(encoding='utf-8').splitlines();headers[name]=lines[0];defs[name]=ddf;originals[name]=raw.read_bytes()
 base[name]={int(l.split('\t')[idcol]):l.split('\t') for l in lines[1:] if l.strip()};reserved.update(base[name])
 # Use vendor's 332-column armor and 92-column weapon text layout; actual binary arrays are identical.
 if name in ('armorgrp','weapongrp'):
  existing=ROOT/'baseline/armorgrp.ddf' if name=='armorgrp' else PROJECT/'research/fafurion-weapons/client-fix-v2/weapongrp.ddf'
  ddf.write_bytes(existing.read_bytes())
  run([ASM/'l2disasm.exe','-d',ddf,'-o','e',raw,txt]);lines=txt.read_text(encoding='utf-8').splitlines();headers[name]=lines[0];base[name]={int(l.split('\t')[1]):l.split('\t') for l in lines[1:] if l.strip()}
objects=collections.defaultdict(set)
for line in (STAGE/'objects.tsv').read_text(encoding='utf-8').splitlines():
 k,typ,ref,cls=line.split('\t');
 if typ=='E':objects[k].add(ref.lower())
available=set().union(*objects.values())
nativepackages={p.stem.lower() for sub in ['system-hud','system','animations','systextures','textures','staticmeshes','sounds'] for p in (PROJECT.parent/'l2'/sub).glob('*') if p.is_file()}
for p in (STAGE/'server/game/data/stats/items').glob('equipment-*.xml'):p.unlink()
packs=json.loads((STAGE/'repaired.json').read_text());rowsout={n:[] for n in base};manifest={'packs':[],'items':[],'blocked':[],'catalogs':{}}
nextid=25000
# Native paperdoll weapon types. Magic two-handed blunt uses Major Arcana baseline.
wmap={1:6364,2:6365,3:6367,4:6370,5:6371,6:6368,8:6580}
amap={1:858,3:920,4:889,6:6378,9:6375,12:6376,17:5808,18:6843}
for pack in packs:
 entry={'key':pack['key'],'name':pack['name'],'batch':pack['batch'],'items':[]};manifest['packs'].append(entry)
 for source in pack['items']:
  row=source['fields'].copy();kind=source['kind'];idcol=1
  # Refuse missing custom package exports: no invisible items or unsupported encrypted packages.
  missing=[];fallbackicons=[];fallbackdrops=[]
  for idx,v in enumerate(row):
   m=re.match(r'^([A-Za-z_][A-Za-z0-9_\-]*)\.[A-Za-z0-9_]',v)
   if not m or v.lower() in available or m[1].lower() in nativepackages:continue
   if idx in range(7,13):fallbackdrops.append(idx)
   elif idx in list(range(13,18))+(list(range(88,92)) if kind=='weapon' else []):fallbackicons.append(idx)
   elif v.lower()=='notexture.notexture':row[idx]=''
   else:missing.append(v)
  if missing:
   manifest['blocked'].append({'pack':pack['key'],'old_id':source['old_id'],'name':source['name'],'missing':sorted(set(missing))});continue
  while nextid in reserved:nextid+=1
  iid=nextid;nextid+=1;reserved.add(iid);row[1]=str(iid)
  if kind=='weapon':
   wt=int(row[43]);part=int(row[23])
   if wt==0 or part==8:bid=6377
   elif wt==1 and part==14:bid=6372
   elif wt==2 and part==14:bid=6366 if int(row[42])>int(row[41])*.6 else 6369
   elif wt==3 and part==14:bid=6371 # dual daggers are represented by dual-fist in Interlude; see report
   else:bid=wmap[wt]
   if wt in (1,2) and int(row[42])>int(row[41])*.6:bid=6366 if part==14 else 6579
  else:
   part=int(row[23]);at=int(row[326])
   if part in amap:bid=amap[part]
   elif part in (15,16):bid={1:6379,2:6373,3:6383}.get(at,6379)
   elif part==10:bid={1:6379,2:6373,3:6383}.get(at,6373)
   elif part==11:bid={1:6379,2:6374,3:6383}.get(at,6374)
   else:raise ValueError((pack['key'],part,at))
  item=copy.deepcopy(allitems[bid]);item.set('id',str(iid))
  if kind=='weapon' and bid in (6366,6579) and wt==1:setval(item,'weapon_type','SWORD')
  for idx in fallbackdrops:row[idx]=base['weapongrp' if kind=='weapon' else 'armorgrp'][bid][idx]
  for idx in fallbackicons:row[idx]=allitems[bid].find("set[@name='icon']").get('val') if idx==13 else ''
  # Names are visual labels only; vendor SA/enchant suffixes must not claim active bonuses.
  name=re.sub(r'\s*\([^)]*(?:Acumen|Focus|Haste|Health|Damage|Critical|Empower|Mana|Anger|Guidance|Magic|HP)[^)]*\)','',source['name'],flags=re.I)
  item.set('name',name);stats={s.get('type'):s.text for s in item.findall('stats/stat')}
  if not stats:stats={s.get('type'):s.text for s in item.find('stats')} if item.find('stats') is not None else {}
  for node in list(item):
   if node.tag in ('skills','conditions','enchant4Skill') or (node.tag=='set' and node.get('name') in ('displayId','equip_condition','is_hero_item','item_skill','handler')):item.remove(node)
  if bid==6370:
   sk=ET.SubElement(item,'skills');ET.SubElement(sk,'skill',{'id':'3599','level':'1'})
  setval(item,'icon',row[13]);setval(item,'price',48800000 if kind=='weapon' and bid!=6377 else 1000000)
  if kind=='armor' and part in (15,16):setval(item,'bodypart','onepiece');row[23]='15'
  # Normalize vendor weapon category to its actual supported native category.
  if kind=='weapon':
   native=base['weapongrp'][bid]
   for idx in [18,19,20,21,22,23,24,40,41,42,43,44,45,46,47,48,49,50,51,52,53]:row[idx]=native[idx]
   if bid in (6366,6579) and wt==1:row[43]='1'
   row[56]='-1'
  else:
   native=base['armorgrp'][bid]
   for idx in [18,19,20,21,326,327,328,329,330,331]:row[idx]=native[idx]
   # Split S light/robe totals between torso and legs; preserve vendor paperdoll slot.
   if part in (10,11) and bid in (6379,6383):
    setval(item,'bodypart','chest' if part==10 else 'legs');row[23]=str(part)
    for typ,value in [('pDef',153 if part==10 else 96)] if bid==6379 else [('pDef',102 if part==10 else 64),('maxMp',533 if part==10 else 333)]:
     item.find("stats/stat[@type='%s']"%typ).text=str(value)
     row[329 if typ=='pDef' else 331]=str(value)
    weight=(3320 if part==10 else 1420) if bid==6379 else (1715 if part==10 else 735)
    setval(item,'weight',weight);row[19]=str(weight)
   if part in (15,16) and int(source['fields'][326])==2:
    # A full heavy suit covers chest and legs; aggregate their base defense and weight.
    for typ,val in [('pDef',333)]:
     n=item.find("stats/stat[@type='%s']"%typ)
     if n is None:n=next((n for n in item.find('stats') if n.get('type')==typ),None)
     if n is not None:n.text=str(val)
    setval(item,'weight',10880);row[329]='333';row[19]='10880'
  root=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../xsd/items.xsd'});root.append(item)
  xml=STAGE/'server/game/data/stats/items'/f'equipment-{iid}.xml';xml.parent.mkdir(parents=True,exist_ok=True);ET.indent(root,space='\t');ET.ElementTree(root).write(xml,encoding='utf-8',xml_declaration=True)
  rowsout['weapongrp' if kind=='weapon' else 'armorgrp'].append(row)
  desc='Visual custom. Base Interlude; sin SA, sockets ni poderes adicionales.'
  names=[str(iid),name,'',f'a,{desc}\\0','-1','a,','a,','a,','a,','0','0','0','a,']
  rowsout['itemname-e'].append(names)
  info={'id':iid,'old_id':source['old_id'],'name':name,'pack':pack['key'],'base':bid,'kind':kind,'server_type':item.get('type'),'bodypart':item.find("set[@name='bodypart']").get('val'),'icon':row[13]};manifest['items'].append(info);entry['items'].append(iid)
for name,rows in rowsout.items():
 txt=STAGE/(name+'.add.txt');txt.write_text(headers[name]+'\n'+'\n'.join('\t'.join(r) for r in rows)+'\n',encoding='utf-8')
 added=STAGE/(name+'.add.raw');run([ASM/'l2asm.exe','-d',defs[name],txt,added]);extra=added.read_bytes();orig=originals[name]
 assert extra.endswith(FOOT) and orig.endswith(FOOT)
 assert struct.unpack_from('<I',extra)[0]==len(rows)
 final=struct.pack('<I',struct.unpack_from('<I',orig)[0]+len(rows))+orig[4:-len(FOOT)]+extra[4:-len(FOOT)]+FOOT
 raw=STAGE/(name+'.raw');raw.write_bytes(final)
 verified=STAGE/(name+'.verified.txt');run([ASM/'l2disasm.exe','-d',defs[name],'-o','e',raw,verified]);ls=verified.read_text(encoding='utf-8').splitlines()
 assert len(ls)-1==struct.unpack_from('<I',final)[0],(name,len(ls),struct.unpack_from('<I',final)[0])
 originaltxt=(STAGE/(name+'.before.txt')).read_text(encoding='utf-8').splitlines()
 assert ls[1:len(originaltxt)]==originaltxt[1:],name
 out=STAGE/(name+'.dat');run([CODEC,'-c','encode','-p','413','-o',out,raw]);check=STAGE/(name+'.check.raw');run([CODEC,'-o',check,out]);assert check.read_bytes()==final
 manifest['catalogs'][name]={'before':sha(CLIENT/(name+'.dat')),'after':sha(out),'added':len(rows),'preserved':struct.unpack_from('<I',orig)[0]}
(STAGE/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('BUILT',len(manifest['items']),'BLOCKED',len(manifest['blocked']))
for p in manifest['packs']:print(p['key'],len(p['items']))
