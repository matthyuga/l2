"""Compile data masks from the existing atlas layout; do not repaint the UV artwork."""
from pathlib import Path
import json, subprocess, shutil,struct,zlib,hashlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'exports/surface-v1'; STAGE.mkdir(exist_ok=True)
editor=ROOT/'tools/l2editor/L2Editor'
inputs=json.loads((ROOT/'reports/visual-inputs.json').read_text(encoding='utf-8'))
report=[]
for obj in inputs:
    body=obj['object']=='Body.baked'
    name='AmberBody' if body else 'AmberOutfit'
    count=len(obj['materials']); cols=4 if count<=16 else 5
    rows=(count+cols-1)//cols; cw=2048//cols; ch=2048//rows
    illumination=[]; reflection=[]
    for m in obj['materials']:
        if body:
            if m['index'] in (7,8,9): surface='eyes'; light=.30; spec=.06
            elif m['index'] in (0,11): surface='skin'; light=.18; spec=0
            else: surface='face detail'; light=.14; spec=0
        elif m['index']==0: surface='hair'; light=.08; spec=.025
        elif 'metal' in m['name'].lower(): surface='metal'; light=.03; spec=.18
        else: surface='cloth / leather'; light=.06; spec=0
        illumination.append(round(light*255));reflection.append(round(spec*255))
        report.append({'atlas':name,'index':m['index'],'source_material':m['name'],
                       'surface':surface,'self_illumination':light,'reflection':spec})
    # Pixel coordinates of the original atlas have Blender's UV origin at the bottom.
    # Sample the exact original cells at output texel centres, including the 3px unused edge.
    for suffix,values in [('LightMask',illumination),('SpecMask',reflection)]:
        image=Image.new('RGBA',(512,512)); pixels=[]
        for y in range(512):
            sy=2047-(y*4+2);row=sy//ch
            for x in range(512):
                col=(x*4+2)//cw; index=row*cols+col
                a=values[index] if col<cols and row<rows and index<count else 0
                # Both RGB and A carry the data, avoiding ambiguity between mask readers.
                pixels.append((a,a,a,a))
        image.putdata(pixels);image.save(STAGE/(name+suffix+'.tga'))
        image.save(STAGE/(name+suffix+'.png'))
(STAGE/'surface-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
classes=editor.parent/'AmberSurfaceV1/Classes';classes.mkdir(parents=True,exist_ok=True)
names=[a+b for a in ['AmberBody','AmberOutfit'] for b in ['LightMask','SpecMask']]
source='class A_SurfaceAssets extends Actor;\n'
source+='\n'.join('#exec TEXTURE IMPORT NAME='+n+' FILE="'+(STAGE/(n+'.tga')).as_posix()+'" MIPS=ON' for n in names)
source+='\ndefaultproperties\n{\n}\n'
(classes/'A_SurfaceAssets.uc').write_text(source,encoding='ascii')
(editor/'AmberSurfaceV1.ini').write_text((editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberSurfaceV1\n',encoding='latin1')
compiled=editor/'AmberSurfaceV1.u'
if compiled.exists():compiled.unlink()
run=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=AmberSurfaceV1.ini'],cwd=editor,capture_output=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
(STAGE/'compile.log').write_bytes(run.stdout+run.stderr)
assert run.returncode==0 and compiled.exists(),(run.returncode,run.stdout[-1500:])
shutil.copy2(compiled,STAGE/'AmberSurfaceV1.raw')
package=STAGE/'AmberSurfaceV1.utx';codec=ROOT.parents[1]/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
r=subprocess.run([str(codec),'-c','encode','-p','121','-f',package.name,'-o',str(package),str(compiled)],capture_output=True,input=b'\n',timeout=30)
assert r.returncode==0,r.stdout+r.stderr
data=package.read_bytes();raw=compiled.read_bytes();key=sum(package.name.lower().encode('ascii'))&255
assert data[:28].decode('utf-16le')=='Lineage2Ver121' and len(data)==len(raw)+48
assert bytes(b^key for b in data[28:-20])==raw
assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
(STAGE/'wrapper-proof.json').write_text(json.dumps({'wrapper':'Lineage2Ver121','filename':package.name,'raw_bytes':len(raw),'crc32':True,'roundtrip':True,'sha256':hashlib.sha256(data).hexdigest()},indent=2))
print('PASS: four mipmapped 512x512 surface masks; filename-dependent Lineage2Ver121, CRC32 and exact decoded package round trip. '+str(package.stat().st_size)+' bytes')
