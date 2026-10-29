from pathlib import Path
import copy,sys,subprocess,json,struct,zlib
S=Path(__file__).resolve().parent;R=S.parents[1]
sys.path.insert(0,str(R/'research/amber-l2/scripts'));from contract_dat import Catalog
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def run(*args):
    r=subprocess.run([str(codec),*map(str,args)],capture_output=True,input=b'\n',timeout=40)
    assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace')[-1000:]
labels=json.loads((S/'asset-spec.json').read_text())['labels'];proof={}
for name,schema in [('skillgrp','skillgrp.xml'),('skillname-e','skillname.xml')]:
    raw=S/(name+'.before.raw');run('-o',raw,S/'current'/(name+'.dat'))
    cat=Catalog(raw,schema,'ScionsOfDestiny')
    assert not any(19720<=r['skill_id']<=19727 for r in cat.rows),'Sticker ID collision'
    template=next(r for r in cat.rows if r['skill_id']==19600 and r['skill_level']==1)
    rows=[]
    for i,label in enumerate(labels):
        row=copy.deepcopy(template);row.update(skill_id=19720+i,skill_level=1)
        if name=='skillgrp':row.update(operate_type=0,mp_consume=0,hp_consume=0,cast_style=0,hit_time=0.,cast_range=0,is_magic=0,animation='',description='NexusStickerEffectsV1.Sticker'+str(i),icon='NexusStickersV1.S'+str(i)+'Up',extra_eff=0,is_enchanted=0,enchant_skill_id=0)
        else:row.update(name='Sticker: '+label,desc='Reaccion visual durante 3 segundos. Recarga compartida de 5 segundos. Sin coste ni efecto de combate.',enchant_name='',enchant_desc='')
        rows.append(row)
    out=S/(name+'.raw');cat.append(rows,out)
    run('-c','encode','-p','413','-o',S/(name+'.dat'),out)
    rt=S/(name+'.roundtrip.raw');run('-o',rt,S/(name+'.dat'));assert rt.read_bytes()==out.read_bytes()
    after=Catalog(rt,schema,'ScionsOfDestiny');assert after.count==cat.count+8
    assert all(cat.data[a['_start']:a['_end']]==after.data[b['_start']:b['_end']] for a,b in zip(cat.rows,after.rows))
    assert cat.data[cat.end:]==after.data[after.end:]
    proof[name]={'added':8,'previous_rows_preserved':cat.count,'roundtrip':True}
# Script and texture package uses the same filename-sensitive wrapper as working native UI textures.
src=S/'NexusStickersV1.u';plain=S/'NexusStickersV1.patched.raw';plain.write_bytes(src.read_bytes())
run('-c','encode','-p','121','-f',src.name,'-o',src,plain)
rt=S/'NexusStickersV1.roundtrip.raw';run('-c','decode','-f',src.name,'-o',rt,src)
assert rt.read_bytes()==plain.read_bytes()
b=src.read_bytes();assert b[:28].decode('utf-16le')=='Lineage2Ver121'
assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
proof['package_wrapper']='121 CRC32 and exact roundtrip'
(S/'catalog-verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
