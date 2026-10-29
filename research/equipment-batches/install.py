from pathlib import Path
import json,shutil,datetime,hashlib,subprocess,xml.etree.ElementTree as ET,html
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];STAGE=ROOT/'stage';CLIENT=PROJECT.parent/'l2';m=json.loads((STAGE/'manifest.json').read_text());changes=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(src,dst,expected=None):
 src=Path(src);dst=Path(dst)
 if expected:assert dst.exists() and sha(dst)==expected,('Concurrent catalog change',dst)
 changes.append({'stage':str(src),'target':str(dst),'before':sha(dst) if dst.exists() else None,'after':sha(src)})
def xmlwrite(root,p):
 p.parent.mkdir(parents=True,exist_ok=True);ET.indent(root,space='\t');ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
def button(action,label):return f'<button action="bypass -h npc_%objectId%_{action}" value="{html.escape(label,quote=True)}" width=260 height=21 back="bigbutton_over" fore="bigbutton"><br1>'
def page(title,content):return f'<html><title>{title}</title><body><center><font color=LEVEL>{title}</font><br>{content}</center></body></html>'
data=STAGE/'server/game/data'
byid={x['id']:x for x in m['items']}
for i,p in enumerate(m['packs'],1):
 if not p['items']:continue
 listid=50037000+i;p['shop_list']=listid
 root=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../xsd/multisell.xsd'});npcs=ET.SubElement(root,'npcs');ET.SubElement(npcs,'npc').text='50010'
 for iid in p['items']:
  item=ET.SubElement(root,'item');price=48800000 if byid[iid]['server_type']=='Weapon' else 1000000
  ET.SubElement(item,'ingredient',{'id':'57','count':str(price)});ET.SubElement(item,'production',{'id':str(iid),'count':'1'})
 xmlwrite(root,data/'multisell/custom'/f'{listid}.xml')
for batch in range(1,4):
 buttons=''.join(button('multisell '+str(p['shop_list']),f'{i+1:02d} {p["name"][:34]} ({len(p["items"])})') for i,p in enumerate(m['packs']) if p['batch']==batch and p['items'])
 p=data/'html/merchant'/f'50010-{80+batch}.htm';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(page(f'Equipo custom - Tanda {batch}',buttons+'<br>'+button('Chat 80','Volver')),encoding='utf-8')
index=''.join(button(f'Chat {80+b}',f'Tanda {b}') for b in range(1,4))+'<br>'+button('Chat 0','Volver al GM Shop')
(data/'html/merchant/50010-80.htm').write_text(page('Equipo custom',index),encoding='utf-8')
runtime=PROJECT/'server/game/data/html/merchant/50010.htm';beforemenu=sha(runtime);text=runtime.read_text(encoding='utf-8');assert 'Chat 80' not in text
text=text.replace('<center>','<center>\n'+button('Chat 80','Equipo custom - 3 tandas'),1)
(data/'html/merchant/50010.htm').write_text(text,encoding='utf-8')
for name,entry in m['catalogs'].items():add(STAGE/(name+'.dat'),CLIENT/'system-hud'/(name+'.dat'),entry['before'])
validprefix={l.split('\t')[2].split('.')[0].lower() for l in (STAGE/'objects.tsv').read_text().splitlines() if l.split('\t')[1]=='E'}
for line in (STAGE/'jobs.tsv').read_text().splitlines():
 key,src,dst,old,new=line.split('\t');p=Path(dst)
 if new.lower() not in validprefix:continue
 folder={'.u':'system-hud','.ukx':'Animations','.utx':'SysTextures','.usx':'StaticMeshes'}[p.suffix.lower()]
 target=CLIENT/folder/p.name;assert not target.exists(),('Asset already present',target)
 # Native L2 textures/meshes need a crypt envelope. Name-table inspection alone
 # accepts raw Unreal packages, while the game client rejects raw UTX files.
 if p.suffix.lower() in ('.utx','.ukx','.usx'):
  encoded=STAGE/'client-packages'/p.name;encoded.parent.mkdir(exist_ok=True)
  protocol=121 if p.suffix.lower()=='.utx' else 111
  subprocess.run([str(PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p',str(protocol),'-f',target.name,'-o',str(encoded),str(p)],capture_output=True,check=True,timeout=60)
  add(encoded,target)
 else:add(p,target)
for src in data.rglob('*'):
 if not src.is_file():continue
 rel=src.relative_to(data)
 for prefix in ['server/game/data','source/L2J_Mobius_CT_0_Interlude/dist/game/data','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data']:
  dst=PROJECT/prefix/rel
  if rel.as_posix()!='html/merchant/50010.htm':assert not dst.exists(),('New data collision',dst)
  add(src,dst,beforemenu if prefix=='server/game/data' and rel.as_posix()=='html/merchant/50010.htm' else None)
closed=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2,java -ErrorAction SilentlyContinue){exit 5}'],capture_output=True)
assert closed.returncode==0,'Client or Java process running; installation requires closed client/server'
backup=PROJECT/'backups'/('equipment-batches-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
assert len({c['target'].lower() for c in changes})==len(changes)
for i,c in enumerate(changes):
 dst=Path(c['target']);assert (sha(dst) if dst.exists() else None)==c['before'],('Concurrent edit',dst)
 if c['before']:
  saved=backup/f'{i}-{dst.name}';shutil.copy2(dst,saved);c['backup']=str(saved)
(backup/'files.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
written=[]
try:
 for c in changes:
  dst=Path(c['target']);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(c['stage'],dst);written.append(c)
 for c in changes:assert sha(c['target'])==c['after'],c['target']
except Exception:
 for c in reversed(written):
  dst=Path(c['target'])
  if sha(dst)!=c['after']:continue
  if c['before']:shutil.copy2(c['backup'],dst)
  else:dst.unlink()
 raise
m.update(status='installed',backup=str(backup),files=changes)
(ROOT/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('INSTALLED',len(m['items']),'items',len(changes),'files','backup',backup)
