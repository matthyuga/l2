"""Prepare append-only labels and the matching server source; no live writes."""
from pathlib import Path
import subprocess,hashlib,json,re,struct
D=Path(__file__).resolve().parent;P=D.parents[3];stage=D/'stage';records=[]
codec=P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';asm=P/'tools-src/L2FileEdit/data/l2asm-disasm';ddf=asm/'DAT_defs/Interlude/sysstring-e.ddf'
def run(args):
 r=subprocess.run([str(a) for a in args],capture_output=True,text=True,errors='replace');assert r.returncode==0,(args,r.stdout,r.stderr)
def sha(b):return hashlib.sha256(b).hexdigest()
def record(target,staged):records.append(dict(target=str(target),stage=str(staged),before_sha256=sha(target.read_bytes()) if target.exists() else None,after_sha256=sha(staged.read_bytes())))
txt=D/'labels.txt';txt.write_text('id\tname\n28000\ta,Nuevo 1\\0\n28001\ta,Nuevo 2\\0\n',encoding='ascii');run([asm/'l2asm.exe','-d',ddf,txt,D/'labels.raw'])
footer=b'\x0cSafePackage\0';addition=(D/'labels.raw').read_bytes();assert addition.endswith(footer) and struct.unpack_from('<I',addition)[0]==2
addition=addition[4:-len(footer)]
for profile in ['system-hud','system-camera-online']:
 dest=Path('E:/l2')/profile;out=stage/profile;out.mkdir(exist_ok=True)
 for name in ['engine.dll','NWindow.dll']:
  manifest=json.loads((D/'native-manifest.json').read_text());key='engine' if name=='engine.dll' else 'ui'
  assert sha((dest/name).read_bytes())==manifest[key]['original_sha256'],('Different profile build',profile,name)
  record(dest/name,stage/name)
 target=dest/'sysstring-e.dat';raw=D/(profile+'.strings.raw');text=D/(profile+'.strings.txt')
 run([codec,'-o',raw,target]);run([asm/'l2disasm.exe','-d',ddf,raw,text])
 assert not re.search(r'(?m)^2800[01]\t',text.read_text(errors='replace')),'Labels already occupied'
 b=raw.read_bytes();assert b.endswith(footer),b[-30:]
 new=out/'sysstring.raw';new.write_bytes(struct.pack('<I',struct.unpack_from('<I',b)[0]+2)+b[4:-len(footer)]+addition+footer)
 dat=out/'sysstring-e.dat';run([codec,'-c','encode','-p','413','-o',dat,new]);check=out/'sysstring.check.raw';run([codec,'-o',check,dat]);assert check.read_bytes()==new.read_bytes()
 run([asm/'l2disasm.exe','-d',ddf,check,out/'sysstring.check.txt']);assert [s for s in (out/'sysstring.check.txt').read_text(errors='replace').splitlines() if s][-2:]==['28000\ta,Nuevo 1\\0','28001\ta,Nuevo 2\\0']
 record(target,dat)
 assert not (dest/'NexusAppearanceV1.u').exists();record(dest/'NexusAppearanceV1.u',stage/'NexusAppearanceV1.u')
rel=Path('java/org/l2jmobius/gameserver/network/clientpackets/CharacterCreate.java')
source=P/'source/L2J_Mobius_CT_0_Interlude'/rel
text=source.read_text(encoding='utf-8-sig');assert '(_face > 2)' in text and '(_hairStyle > 4)' in text
text=text.replace('(_face > 2)','(_face > 5)')
old='(_hairStyle < 0) || (!_isFemale && (_hairStyle > 4)) || (_isFemale && (_hairStyle > 6))'
new='(_hairStyle < 0) || (!_isFemale && (_hairStyle > 6)) || (_isFemale && (_hairStyle > (((_classId >= 44) && (_classId <= 48)) ? 6 : 8)))'
assert old in text;text=text.replace(old,new)
out=stage/'server-source'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text,encoding='utf-8')
record(source,out);record(P/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'/rel,out)
(D/'install-plan.json').write_text(json.dumps(records,indent=2));print('Prepared',len(records),'client/source files with baseline hash guards')
