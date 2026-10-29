import pathlib,subprocess,struct
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1];EDITOR=ROOT/'tools/l2editor/L2Editor';PKG=EDITOR.parent/'AmberParticles';(PKG/'Classes').mkdir(parents=True,exist_ok=True)
ASSETS=ROOT/'exports/contract';ASSETS.mkdir(exist_ok=True)
for name,color in [('AmberWhite',(210,230,255,255)),('AmberFire',(255,90,10,255))]:Image.new('RGBA',(8,8),color).save(ASSETS/(name+'.tga'))
im=Image.new('RGBA',(128,128),(0,0,0,0));draw=ImageDraw.Draw(im);draw.ellipse((4,4,123,123),outline=(255,180,30,220),width=5);draw.ellipse((18,18,109,109),outline=(255,80,10,130),width=2);im.save(ASSETS/'Ring.tga')
verts=[(-1,0,20),(1,0,20),(1,0,-20),(-1,0,-20),(-5,0,-18),(5,0,-18),(0,0,-32),(-4,0,20),(4,0,20),(0,0,10)]
faces=[(0,1,2),(0,2,3),(4,5,6),(7,8,9)]
def lwo(name):
    def chunk(tag,data):return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
    def sub(tag,data):return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
    points=b''.join(struct.pack('>fff',x,z*(-1 if name=='AmberSky' else 1),y) for x,y,z in verts)
    points+=b''.join(struct.pack('>fff',y,z*(-1 if name=='AmberSky' else 1),x) for x,y,z in verts)
    if name=='AmberShot':
        points=b''.join(struct.pack('>fff',-z,x,y) for x,y,z in verts)
        points+=b''.join(struct.pack('>fff',-z,y,x) for x,y,z in verts)
    meshfaces=faces+[tuple(v+len(verts) for v in f) for f in faces]
    meshfaces+= [tuple(reversed(f)) for f in meshfaces]
    polys=b'FACE'+b''.join(struct.pack('>HHHH',3,*f) for f in meshfaces)
    material='AmberWhite' if name=='AmberSky' else 'AmberFire' if name=='AmberShot' else name
    tags=(material+'\0').encode()
    color=(1.0,.25,.03) if material=='AmberFire' else (.8,.9,1.0)
    surf=(material+'\0\0').encode()+sub(b'COLR',struct.pack('>fffH',*color,0))+sub(b'SIDE',struct.pack('>H',3))
    data=b'LWO2'+chunk(b'PNTS',points)+chunk(b'POLS',polys)+chunk(b'TAGS',tags)+chunk(b'PTAG',b'SURF'+b''.join(struct.pack('>HH',i,0) for i in range(len(meshfaces))))+chunk(b'SURF',surf)
    path=ASSETS/(name+'.lwo');path.write_bytes(b'FORM'+struct.pack('>I',len(data))+data);return path.as_posix()
white=lwo('AmberWhite');fire=lwo('AmberFire');sky=lwo('AmberSky');shot=lwo('AmberShot')
for name,mesh,velocity,z,count,life in [('Rain','ArrowWhite',-850,600,36,0.8),('FireRain','ArrowFire',-850,600,36,0.8),('SkyVolley','ArrowSky',950,60,12,0.7),('FireShot','ArrowShot',700,40,3,0.4)]:
    source=f'''class {name} extends Emitter;
#exec TEXTURE IMPORT NAME=AmberWhite FILE="{(ASSETS/'AmberWhite.tga').as_posix()}" MIPS=OFF
#exec TEXTURE IMPORT NAME=AmberFire FILE="{(ASSETS/'AmberFire.tga').as_posix()}" MIPS=OFF
#exec STATICMESH IMPORT NAME=ArrowWhite FILE="{white}"
#exec STATICMESH IMPORT NAME=ArrowFire FILE="{fire}"
#exec STATICMESH IMPORT NAME=ArrowSky FILE="{sky}"
#exec STATICMESH IMPORT NAME=ArrowShot FILE="{shot}"
defaultproperties
{{
    Begin Object Class=MeshEmitter Name=Arrows
        StaticMesh=StaticMesh'AmberParticles.{mesh}'
        UseParticleColor=False
        UseCollision=False
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=200.0
        MaxParticles={count}
        RespawnDeadParticles=False
        StartLocationRange=(X=(Min=-190,Max=190),Y=(Min=-190,Max=190),Z=(Min={z},Max={z+40}))
        StartVelocityRange=(Z=(Min={velocity},Max={velocity}))
        StartSizeRange=(X=(Min=1,Max=1),Y=(Min=1,Max=1),Z=(Min=1,Max=1))
        LifetimeRange=(Min={life},Max={life})
        SecondsBeforeInactive=0.0
    End Object
    Emitters(0)=MeshEmitter'Arrows'
    AutoDestroy=True
    bNoDelete=False
    bDirectional=False
    LifeSpan=1.5
}}
'''
    if name in ('SkyVolley','FireShot'):source=source.replace('Min=-190,Max=190','Min=-6,Max=6')
    if name=='SkyVolley':source=source.replace('RespawnDeadParticles=False','RespawnDeadParticles=True').replace('LifeSpan=1.5','LifeSpan=3.5').replace('InitialParticlesPerSecond=200.0','InitialParticlesPerSecond=18.0')
    if name=='FireShot':
        # Local X follows Amber's heading; Z is reserved for the upward volley.
        source=source.replace('StartVelocityRange=(Z=(Min=700,Max=700))',
            'CoordinateSystem=PTCS_Relative\n        StartVelocityRange=(X=(Min=1400,Max=1400))')
        source=source.replace('LifetimeRange=(Min=0.4,Max=0.4)', 'LifetimeRange=(Min=0.5,Max=0.5)')
    (PKG/'Classes'/(name+'.uc')).write_text(source)
source=f'''class Mark extends Emitter;
#exec TEXTURE IMPORT NAME=Ring FILE="{(ASSETS/'Ring.tga').as_posix()}" MIPS=OFF MASKED=1
defaultproperties
{{
    Begin Object Class=SpriteEmitter Name=Circle
        Texture=Texture'AmberParticles.Ring'
        DrawStyle=PTDS_AlphaBlend
        UseDirectionAs=PTDU_Normal
        ProjectionNormal=(Z=1.0)
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=100.0
        MaxParticles=1
        RespawnDeadParticles=False
        StartLocationRange=(Z=(Min=8,Max=8))
        StartSizeRange=(X=(Min=200,Max=200),Y=(Min=200,Max=200),Z=(Min=200,Max=200))
        LifetimeRange=(Min=3.5,Max=3.5)
        SecondsBeforeInactive=0.0
    End Object
    Emitters(0)=SpriteEmitter'Circle'
    AutoDestroy=True
    bNoDelete=False
    LifeSpan=3.6
}}
''';(PKG/'Classes/Mark.uc').write_text(source)
config=(EDITOR/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberParticles\n'
(EDITOR/'AmberParticles.ini').write_text(config,encoding='latin1')
compiled=EDITOR/'AmberParticles.u'
if compiled.exists():compiled.unlink()
with (ROOT/'reports/amber-particles-build.log').open('w') as log:
    result=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini=AmberParticles.ini'],cwd=EDITOR,stdout=log,stderr=subprocess.STDOUT,timeout=180)
print((ROOT/'reports/amber-particles-build.log').read_text(errors='replace')[-2200:]);assert result.returncode==0 and compiled.exists()

