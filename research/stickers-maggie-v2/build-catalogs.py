from pathlib import Path
import copy,sys,subprocess,json,struct,zlib
S=Path(__file__).resolve().parent;R=S.parents[1]
sys.path.insert(0,str(R/'research/amber-l2/scripts'));from contract_dat import Catalog
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def run(*args):
    r=subprocess.run([str(codec),*map(str,args)],capture_output=True,input=b'\n',timeout=40);assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace')[-1000:]
labels=json.loads((S/'asset-spec.json').read_text())['labels'];proof={}
for name,schema in [('skillgrp','skillgrp.xml'),('skillname-e','skillname.xml')]:
    before=S/(name+'.before.raw');run('-o',before,S/'current'/(name+'.dat'));cat=Catalog(before,schema,'ScionsOfDestiny')
    assert not any(19728<=r['skill_id']<=19738 for r in cat.rows),'ID collision'
    template=next(r for r in cat.rows if r['skill_id']==19720 and r['skill_level']==1)
    rows=[]
    def row(i,old):
        r=copy.deepcopy(old);r.update(skill_id=19720+i,skill_level=1)
        if name=='skillgrp':r.update(description='NexusStickerEffectsV2.Sticker'+str(i),icon='NexusStickersV2.S'+str(i)+'Up')
        else:r.update(name='Sticker: '+labels[i],desc='Sticker de la lamina Maggie Fess. Duracion 3 segundos; espera compartida 5 segundos.',enchant_name='',enchant_desc='')
        return r
    # Keep every unrelated record byte-for-byte, including any concurrent extensions.
    chunks=[struct.pack('<I',cat.count+11)]
    for old in cat.rows:
        i=old['skill_id']-19720
        chunks.append(cat.encode(row(i,old)) if 0<=i<8 else cat.data[old['_start']:old['_end']])
    for i in range(8,19):chunks.append(cat.encode(row(i,template)))
    chunks.append(cat.data[cat.end:]);raw=S/(name+'.raw');raw.write_bytes(b''.join(chunks))
    run('-c','encode','-p','413','-o',S/(name+'.dat'),raw)
    rt=S/(name+'.roundtrip.raw');run('-o',rt,S/(name+'.dat'));assert rt.read_bytes()==raw.read_bytes()
    new=Catalog(rt,schema,'ScionsOfDestiny');assert new.count==cat.count+11
    for a,b in zip(cat.rows,new.rows):
        if not 19720<=a['skill_id']<=19727:assert cat.data[a['_start']:a['_end']]==new.data[b['_start']:b['_end']]
    assert cat.data[cat.end:]==new.data[new.end:]
    proof[name]={'updated_stickers':8,'added_stickers':11,'unrelated_rows_preserved':cat.count-8,'roundtrip':True}
src=S/'NexusStickersV2.u';plain=S/'NexusStickersV2.patched.raw';plain.write_bytes(src.read_bytes())
run('-c','encode','-p','121','-f',src.name,'-o',src,plain)
rt=S/'NexusStickersV2.roundtrip.raw';run('-c','decode','-f',src.name,'-o',rt,src);assert rt.read_bytes()==plain.read_bytes()
b=src.read_bytes();assert b[:28].decode('utf-16le')=='Lineage2Ver121' and struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
proof['package_wrapper']='121 CRC32 and exact roundtrip'
(S/'catalog-verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
