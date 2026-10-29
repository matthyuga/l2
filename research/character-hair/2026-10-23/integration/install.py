from pathlib import Path
import json, hashlib, shutil, datetime, subprocess, sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
STAGE=ROOT/'stage'
CLIENT=PROJECT.parent/'l2'
MIRRORS=[PROJECT/p for p in ['server/game/data','source/L2J_Mobius_CT_0_Interlude/dist/game/data','cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game/data']]
MENUS=['html/merchant/50010.htm','html/merchant/50010-4.htm','html/admin/gmshops.htm','html/admin/gmstore/hair.htm']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xml(root,p):
 p.parent.mkdir(parents=True,exist_ok=True);ET.indent(root,space='\t');ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
def main():
 assert not (ROOT/'installation.json').exists(),'Already installed; do not append again'
 m=json.loads((ROOT/'manifest.json').read_text(encoding='utf8'));changes=[]
 def add(src,dst,expected=None,new=False):
  assert not new or not dst.exists(),('New file collision',dst)
  before=sha(dst) if dst.exists() else None
  assert expected is None or before==expected,('Concurrent catalog edit',dst)
  changes.append(dict(stage=str(src),target=str(dst),before=before,after=sha(src)))
 data=STAGE/'data'
 shutil.copyfile(STAGE/'hair-accessories.xml',STAGE/'hair-accessories.install.xml')
 buy=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../xsd/buylist.xsd'})
 multi=ET.Element('list',{'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':'../../xsd/multisell.xsd'})
 ET.SubElement(ET.SubElement(multi,'npcs'),'npc').text='50010'
 for item in m['items']:
  iid=str(item['id']);ET.SubElement(buy,'item',id=iid,price='0')
  entry=ET.SubElement(multi,'item');ET.SubElement(entry,'ingredient',id='57',count='1');ET.SubElement(entry,'production',id=iid,count='1')
 xml(buy,data/'buylists/28000.xml');xml(multi,data/'multisell/custom/50042800.xml')
 targetxml=data/'stats/items/hair-accessories.xml';targetxml.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(STAGE/'hair-accessories.xml',targetxml)
 for mirror_index,mirror in enumerate(MIRRORS):
  for rel in ['stats/items/hair-accessories.xml','buylists/28000.xml','multisell/custom/50042800.xml']:
   add(data/rel,mirror/rel,new=True)
  for rel in MENUS:
   dst=mirror/rel;content=(dst if dst.exists() else MIRRORS[0]/rel).read_bytes();text=content.decode('utf8')
   assert 'value="Cabellos"' not in text and '<center>' in text,('Menu already patched or unsupported',dst)
   action='npc_%objectId%_multisell 50042800' if '/merchant/' in rel else 'admin_buy 28000'
   button=f'<button action="bypass -h {action}" value="Cabellos" width=240 height=21 back="bigbutton_over" fore="bigbutton"><br1>'
   text=text.replace('<center>','<center>\n'+button,1)
   src=STAGE/'menus'/str(mirror_index)/rel;src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(text.encode('utf8'));add(src,dst)
 for a in m['assets']:
  src=STAGE/'assets'/a['name'];assert sha(src)==a['sha256']
  add(src,CLIENT/('Animations' if src.suffix.lower()=='.ukx' else 'SysTextures')/src.name,new=True)
 for name,c in m['catalogs'].items():add(STAGE/(name+'.dat'),CLIENT/'system-hud'/(name+'.dat'),c['before_sha256'])
 assert len({c['target'].lower() for c in changes})==len(changes)
 (ROOT/'installation-plan.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
 if '--prepare' in sys.argv:print('PREPARED',len(changes),'files');return
 assert (ROOT/'native-verification.txt').read_text().endswith('SUCCESS\n'),'Native preflight required'
 u=json.loads((ROOT/'umodel-verification.json').read_text());assert len(u)==20 and all(r['code']==0 and not r['error'] for r in u)
 closed=subprocess.run(['powershell.exe','-NoProfile','-Command','if(Get-Process L2 -ErrorAction SilentlyContinue){exit 5}'],capture_output=True)
 assert closed.returncode==0,'Close the client before replacing DAT files'
 backup=PROJECT/'backups'/('hair-accessories-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
 for i,c in enumerate(changes):
  dst=Path(c['target']);assert (sha(dst) if dst.exists() else None)==c['before'],('Concurrent change',dst)
  if c['before']:
   saved=backup/f'{i}-{dst.name}';shutil.copy2(dst,saved);c['backup']=str(saved)
 (backup/'files.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
 written=[]
 try:
  for c in changes:
   dst=Path(c['target']);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(c['stage'],dst);written.append(c)
  for c in changes:assert sha(c['target'])==c['after'],c['target']
 except BaseException:
  for c in reversed(written):
   dst=Path(c['target'])
   if sha(dst)!=c['after']:continue
   if c['before']:shutil.copy2(c['backup'],dst)
   else:dst.unlink()
  raise
 m.update(status='installed',backup=str(backup),files=changes)
 (ROOT/'installation.json').write_text(json.dumps(m,indent=2),encoding='utf8');print('INSTALLED',len(m['items']),'items;',len(changes),'files;',backup)
if __name__=='__main__':main()
