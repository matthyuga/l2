from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,struct,zlib,json,hashlib,copy,sys
root=Path(__file__).resolve().parents[3];stage=Path(__file__).resolve().parent
editor=root/'research/amber-l2/tools/l2editor/L2Editor'
package='SkillGroupsV3';codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size)
imports=[]
def asset(name,im):
    file=stage/(name+'.tga');im.save(file)
    imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{file.as_posix()}" MIPS=OFF')
labels=['PRINCIPAL','SUBCLASE 1','SUBCLASE 2','SUBCLASE 3','COMUNES','AMBER','ESPECIALES']
for group,label in enumerate(labels):
    row=Image.new('RGB',(192,32),(18,25,34));d=ImageDraw.Draw(row)
    d.rectangle((0,24,191,30),fill=(255,212,103));d.line((0,23,191,23),fill=(145,110,47),width=1)
    d.text((6,3),label,font=font(13),fill=(255,232,172))
    row.save(stage/('header-'+str(group)+'.png'))
    for tile in range(6):asset(f'H{group}_{tile}',row.crop((tile*32,0,tile*32+32,32)))
asset('Blank',Image.new('RGB',(32,32),(18,25,34)))
buttons={'ClassMain':('Principal',64),'ClassSub1':('Sub 1',64),'ClassSub2':('Sub 2',64),'ClassSub3':('Sub 3',64),
         'ClassCommon':('Comunes',128),'ClassAmber':('Amber',128),'ClassAll':('Todas',128),
         'ClassNext':('Siguiente clase >',256),'ClassesButton':('Nombres / indice',256)}
for name,(label,width) in buttons.items():
    for state,background in [('Up',(29,36,47)),('Down',(19,27,38)),('Over',(57,59,48))]:
        im=Image.new('RGB',(width,32),background);d=ImageDraw.Draw(im)
        d.rectangle((0,0,width-1,31),outline=(174,143,76),width=2)
        size=14 if width==64 else 16 if width==128 else 24
        f=font(size);box=d.textbbox((0,0),label,font=f);tw=box[2]-box[0];th=box[3]-box[1]
        d.text(((width-tw)//2,(32-th)//2-box[1]),label,font=f,fill=(255,237,181))
        asset(name+state,im)
classes=editor.parent/package/'Classes';classes.mkdir(parents=True,exist_ok=True)
(classes/'Assets.uc').write_text('class Assets extends Object;\n'+'\n'.join(imports)+'\n',encoding='ascii')
(editor/(package+'.ini')).write_text((editor/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={package}\n',encoding='latin1')
assert not (editor/(package+'.u')).exists(),'Do not reuse an old compiled package'
with (stage/'ucc-build.log').open('w') as log:
    result=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini='+package+'.ini'],cwd=editor,stdout=log,stderr=subprocess.STDOUT,timeout=120)
assert result.returncode==0 and (editor/(package+'.u')).exists(),(stage/'ucc-build.log').read_text(errors='replace')[-2000:]
raw=(editor/(package+'.u')).read_bytes();rawfile=stage/(package+'.raw');rawfile.write_bytes(raw)
filename=package+'.utx';encoded=stage/filename
def run(*args):subprocess.run([str(codec),*map(str,args)],check=True,capture_output=True,input=b'\n',timeout=30)
run('-c','encode','-p','121','-f',filename,'-o',encoded,rawfile)
b=encoded.read_bytes();assert b[:28].decode('utf-16le')=='Lineage2Ver121'
assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
run('-c','decode','-f',filename,'-o',stage/(package+'.roundtrip.raw'),encoded)
assert (stage/(package+'.roundtrip.raw')).read_bytes()==raw
sys.path.insert(0,str(root/'research/amber-l2/scripts'));from contract_dat import Catalog
proof={'texture_wrapper':'121 checksum and decode PASS','texture_count':len(imports)}
for name,schema in [('skillgrp','skillgrp.xml'),('skillname-e','skillname.xml')]:
    before=stage/(name+'.before.raw');run('-o',before,root.parent/'l2/system-hud'/(name+'.dat'))
    cat=Catalog(before,schema,'ScionsOfDestiny')
    assert not any(19100<=r['skill_id']<=19199 for r in cat.rows),'Reserved decorative IDs conflict'
    template=next(r for r in cat.rows if r['skill_id']==19014 and r['skill_level']==1)
    rows=[]
    for id in [*range(19100,19142),19199]:
        r=copy.deepcopy(template);r['skill_id']=id;r['skill_level']=1
        group=(id-19100)//6;tile=(id-19100)%6
        if name=='skillgrp':
            r['icon']=package+('.Blank' if id==19199 else f'.H{group}_{tile}')
            # These entries only supply an icon/name to the native list, never a cast.
        else:
            r['name']='' if id==19199 else labels[group]
            r['desc']='Separador del catalogo de habilidades. No es una habilidad.' if id!=19199 else ''
        rows.append(r)
    out=stage/(name+'.raw');cat.append(rows,out)
    run('-c','encode','-p','413','-o',stage/(name+'.dat'),out)
    rt=stage/(name+'.roundtrip.raw');run('-o',rt,stage/(name+'.dat'));assert rt.read_bytes()==out.read_bytes()
    new=Catalog(rt,schema,'ScionsOfDestiny');assert new.count==cat.count+43
    assert all(new.data[n['_start']:n['_end']]==cat.data[o['_start']:o['_end']] for o,n in zip(cat.rows,new.rows))
    proof[name]={'added_decorations':43,'all_existing_rows_identical':True,'roundtrip':True}
(stage/'assets-verification.json').write_text(json.dumps(proof,indent=2))
print('PASS:',json.dumps(proof))
