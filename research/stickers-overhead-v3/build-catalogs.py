from pathlib import Path
import json,subprocess,sys,struct,zlib,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];sys.path.insert(0,str(R/'research/amber-l2/scripts'));from contract_dat import Catalog
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def run(*args):
 p=subprocess.run([str(codec),*map(str,args)],capture_output=True,input=b'\n',timeout=40);assert p.returncode==0,(p.stdout+p.stderr).decode(errors='replace')[-1000:]
before=S/'skillgrp.before.raw';run('-o',before,S/'current/skillgrp.dat');cat=Catalog(before,'skillgrp.xml','ScionsOfDestiny')
parts=[struct.pack('<I',cat.count)];changed=[]
for old in cat.rows:
 if 19720<=old['skill_id']<=19738:
  row=dict(old);i=old['skill_id']-19720;row.update(description='NexusStickerEffectsV3.Sticker'+str(i),icon='NexusStickersV3.S'+str(i)+'Up',cast_range=4294967295)
  parts.append(cat.encode(row));changed.append(i)
 else:parts.append(cat.data[old['_start']:old['_end']])
assert sorted(changed)==list(range(19));parts.append(cat.data[cat.end:]);raw=S/'skillgrp.raw';raw.write_bytes(b''.join(parts))
run('-c','encode','-p','413','-o',S/'skillgrp.dat',raw)
rt=S/'skillgrp.roundtrip.raw';run('-o',rt,S/'skillgrp.dat');assert rt.read_bytes()==raw.read_bytes()
new=Catalog(rt,'skillgrp.xml','ScionsOfDestiny');assert new.count==cat.count
for a,b in zip(cat.rows,new.rows):
 if not 19720<=a['skill_id']<=19738:assert cat.data[a['_start']:a['_end']]==new.data[b['_start']:b['_end']]
assert cat.data[cat.end:]==new.data[new.end:]
shutil.copy2(S/'current/skillname-e.dat',S/'skillname-e.dat')
src=S/'NexusStickersV3.u';plain=S/'NexusStickersV3.patched.raw';plain.write_bytes(src.read_bytes())
run('-c','encode','-p','121','-f',src.name,'-o',src,plain)
rt=S/'NexusStickersV3.roundtrip.raw';run('-c','decode','-f',src.name,'-o',rt,src);assert rt.read_bytes()==plain.read_bytes()
b=src.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
proof={'updated_stickers':19,'unrelated_rows_preserved':cat.count-19,'roundtrip':True,'skillnames_unchanged':True,'wrapper':'121 CRC and exact roundtrip'}
(S/'catalog-verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
