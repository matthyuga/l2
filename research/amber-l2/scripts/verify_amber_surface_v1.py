"""Validate native package loading, texture alpha round trips and mesh export before installation."""
from pathlib import Path
import shutil, subprocess,json,hashlib,csv,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];STAGE=ROOT/'exports/surface-v1';CLIENT=ROOT.parents[2]/'l2'
reader=ROOT/'tools/umodel.exe';logs=STAGE/'verification';logs.mkdir(exist_ok=True)
def run(args,label):
    r=subprocess.run([str(reader),*args,'-game=l2','-path='+str(STAGE)],capture_output=True,text=True,errors='replace',timeout=90)
    (logs/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8')
    assert r.returncode==0,(label,r.stdout[-2000:],r.stderr[-2000:])
    assert 'WARNING: missing' not in r.stdout and 'Unable to load' not in r.stdout,(label,r.stdout)
    return r.stdout+r.stderr
for folder,names in [('systextures',['FFighter.utx','goldcubes.utx']),('animations',['L2AmberMotionv3.ukx','L2AmberArcherMotion.ukx'])]:
    for name in names:
        dest=STAGE/'dependencies'/name;dest.parent.mkdir(exist_ok=True)
        if not dest.exists():shutil.copy2(CLIENT/folder/name,dest)
run(['-export','-png','-noanim','-nomesh','-out='+str(logs/'masks'),'AmberSurfaceV1.utx'],'mask-export')
for atlas in ['AmberBody','AmberOutfit']:
    for suffix in ['LightMask','SpecMask']:
        name=atlas+suffix
        before=Image.open(STAGE/(name+'.tga')).convert('RGBA')
        after=Image.open(logs/'masks/AmberSurfaceV1/Texture'/(name+'.png')).convert('RGBA')
        assert before.size==after.size==(512,512) and before.tobytes()==after.tobytes(),name
        text=run(['-dump','-noanim','AmberSurfaceV1.utx',name],name)
        assert 'Format = TEXF_RGBA8 (5)' in text and 'USize = 512' in text and 'VSize = 512' in text,text
proof=list(csv.DictReader((STAGE/'package-proof.tsv').open(),delimiter='\t'))
for entry in proof:
    package=entry['package']
    current_hash=hashlib.sha256((CLIENT/'animations'/(package+'.ukx')).read_bytes()).hexdigest()
    assert current_hash in (entry['source_sha256'],entry['staged_sha256']),'Installed package changed concurrently'
    for atlas in ['AmberBody','AmberOutfit']:
        text=run(['-dump','-noanim',package+'.ukx',atlas+'Shader'],package+'-'+atlas+'Shader')
        for prop,value in [('SelfIlluminationMask',atlas+'LightMask'),('SpecularityMask',atlas+'SpecMask'),('Specular','LowBody.TexEnvMap0')]:
            assert re.search(r'\b'+prop+r' = \w+\x27'+re.escape(value)+r'\x27',text),(prop,text)
        assert 'OutputBlending = OB_Masked (1)' in text and 'AlphaRef = 128' in text and 'ZWrite = true' in text
    text=run(['-export','-noanim','-out='+str(logs/'staged'),package+'.ukx','AmberNPC'],package+'-export')
    # Original client and staged PSK geometry must match byte for byte.
    original=logs/'original';original.mkdir(exist_ok=True)
    source=CLIENT/'animations'/(package+'.ukx')
    if current_hash==entry['staged_sha256']:
        installation=json.loads((STAGE/'installation.json').read_text(encoding='utf-8-sig'))
        source=Path(installation['backup'])/'animations'/(package+'.ukx')
        assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['source_sha256']
    p=subprocess.run([str(reader),'-export','-noanim','-game=l2','-path='+str(CLIENT),'-out='+str(original),str(source),'AmberNPC'],capture_output=True,timeout=90)
    assert p.returncode==0,p.stdout[-2000:]
    assert (original/package/'SkeletalMesh/AmberNPC.psk').read_bytes()==(logs/'staged'/package/'SkeletalMesh/AmberNPC.psk').read_bytes()
    entry['native_shader_load']=True;entry['native_psk_unchanged']=True;entry['native_mask_roundtrip']=True
wrapper=json.loads((STAGE/'wrapper-proof.json').read_text())
assert wrapper['roundtrip'] and wrapper['crc32'] and hashlib.sha256((STAGE/'AmberSurfaceV1.utx').read_bytes()).hexdigest()==wrapper['sha256']
(STAGE/'native-proof.json').write_text(json.dumps({'packages':proof,'mask_pixels_exact':True,'texture_wrapper':wrapper,'client_runtime_tested':False},indent=2),encoding='utf-8')
print('PASS: native shaders/dependencies, four exact RGBA round trips, texture wrapper 121/CRC, unchanged native PSK geometry on both packages.')
