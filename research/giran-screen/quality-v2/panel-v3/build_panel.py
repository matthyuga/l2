"""Build an original screen mesh and marker material in an isolated UCC workspace."""
from pathlib import Path
import struct,shutil,subprocess,json,sys
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent
assets=D/'assets';assets.mkdir(exist_ok=True)
P=struct.pack
def chunk(name,size,count,raw):return P('<20s3i',name.encode(),1999801,size,count)+raw
vertices=[];wedges=[];faces=[]
def quad(points,material,uv=None):
    uv=uv or [(0,1),(1,1),(1,0),(0,0)]
    start=len(wedges)
    for pos,(u,v) in zip(points,uv):
        pi=len(vertices);vertices.append(pos);wedges.append(P('<H2xffBB2x',pi,u,v,material,0))
    faces.extend([P('<3HBBI',start,start+1,start+2,material,0,1),P('<3HBBI',start,start+2,start+3,material,0,1)])
def box(x0,x1,y0,y1,z0,z1):
    pts=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:quad([pts[i] for i in ids],1)
# Wall-mounted flat television: 648 x 498 outer frame; 600 x 450 picture.
quad([(6,-300,24),(6,300,24),(6,300,474),(6,-300,474)],0,[(0,.46875),(.625,.46875),(.625,0),(0,0)])
quad([(-14,300,24),(-14,-300,24),(-14,-300,474),(-14,300,474)],0,[(0,.46875),(.625,.46875),(.625,0),(0,0)])
for bounds in [(-12,4,-324,-300,0,498),(-12,4,300,324,0,498),(-12,4,-300,300,474,498),(-12,4,-300,300,0,24)]:box(*bounds)
materials=b''.join(P('<64s6i',n.encode(),i,0,0,0,0,0) for i,n in enumerate(['Feed','Frame']))
bone=P('<64s3i4f3ff3f',b'root',0,0,0,0,0,0,1,0,0,0,0,1,1,1)
psk=chunk('ACTRHEAD',0,0,b'')+chunk('PNTS0000',12,len(vertices),b''.join(P('<3f',*v) for v in vertices))+chunk('VTXW0000',16,len(wedges),b''.join(wedges))+chunk('FACE0000',12,len(faces),b''.join(faces))+chunk('MATT0000',88,2,materials)+chunk('REFSKELT',120,1,bone)+chunk('RAWWEIGHTS',12,len(vertices),b''.join(P('<fii',1,i,0) for i in range(len(vertices))))
(assets/'Screen.psk').write_bytes(psk)
anim=P('<64s64s4i3f3i',b'wait',b'None',1,0,0,0,0,2,30,0,0,2)
keys=P('<8f',0,0,0,0,0,0,1,1/30)*2
(assets/'Idle.psa').write_bytes(chunk('ANIMHEAD',0,0,b'')+chunk('BONENAMES',120,1,bone)+chunk('ANIMINFO',168,1,anim)+chunk('ANIMKEYS',32,2,keys))
marker=[0xff1234e0,0xffda7142,0xff28c56a,0xffa531c8,0xffe8b927,0xff347ad1,0xffcf4265,0xff71d8ac]
im=Image.new('RGBA',(512,512),(10,17,28,255));draw=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/tahomabd.ttf',36);small=ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf',21)
draw.rounded_rectangle((22,42,490,342),radius=20,outline=(45,153,195),width=2)
draw.text((256,112),'NEXUS TV',font=font,anchor='mm',fill=(120,219,244))
draw.text((256,185),'SIN SENAL',font=small,anchor='mm',fill=(230,235,245))
draw.text((256,234),'Esperando a NexusCam',font=small,anchor='mm',fill=(160,180,200))
for x,c in enumerate(marker):im.putpixel((x,0),((c>>16)&255,(c>>8)&255,c&255,255))
large=Image.new('RGBA',(2048,2048),(0,0,0,255));large.paste(im.resize((1280,1280)),(0,0));im=large
for x,c in enumerate(marker):im.putpixel((x,0),((c>>16)&255,(c>>8)&255,c&255,255))
im.putpixel((2047,2047),(0,0,0,254));im.save(assets/'Feed.tga');im.save(assets/'offline-preview.png')
Image.new('RGBA',(64,64),(65,85,110,255)).save(assets/'Frame.tga')
compiler=D/'compiler';compiler.mkdir(exist_ok=True)
editor=Path('E:/l2-local/research/amber-l2/tools/l2editor/L2Editor')
for p in editor.iterdir():
    if p.is_file() and (p.suffix.lower() in ['.dll','.int'] or p.name in ['UCC.exe','Core.u','Engine.u','Editor.u','UnrealEd.u','Fire.u','Default.ini','User.ini','DefUser.ini']):
        target=compiler/p.name
        if not target.exists():shutil.copy2(p,target)
classes=D/'NexusTVPanel3/Classes';classes.mkdir(parents=True,exist_ok=True)
uc=f'''class ScreenAssets extends Actor;
#exec MESH MODELIMPORT MESH=Screen MODELFILE="{(assets/'Screen.psk').as_posix()}" LODSTYLE=0 LODSPECIFY=1
#exec MESH LODMODEL MESH=Screen LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=1 COHERENCE=1
#exec MESHMAP SCALE MESHMAP=Screen X=1 Y=1 Z=1
#exec TEXTURE IMPORT NAME=Feed FILE="{(assets/'Feed.tga').as_posix()}" MIPS=OFF
#exec TEXTURE IMPORT NAME=Frame FILE="{(assets/'Frame.tga').as_posix()}" MIPS=OFF
#exec MESHMAP SETTEXTURE MESHMAP=Screen NUM=0 TEXTURE=Feed
#exec MESHMAP SETTEXTURE MESHMAP=Screen NUM=1 TEXTURE=Frame
defaultproperties
{{
 DrawType=DT_Mesh
 Mesh=SkeletalMesh'NexusTVPanel3.Screen'
 bUnlit=True
}}
'''
(classes/'ScreenAssets.uc').write_text(uc,encoding='ascii')
ini='''[URL]
Class=Engine.Pawn
[Core.System]
Paths=./*.u
[Engine.Engine]
EditorEngine=Editor.EditorEngine
GameEngine=Engine.GameEngine
RenderDevice=Engine.NullRenderDevice
[Editor.EditorEngine]
CacheSizeMegs=64
EditPackages=Core
EditPackages=Engine
EditPackages=NexusTVPanel3
'''
(compiler/'NexusTV.ini').write_text(ini,encoding='ascii')
compiled=compiler/'NexusTVPanel3.u'
if compiled.exists():shutil.move(compiled,compiler/'NexusTVPanel3.previous')
result=subprocess.run([str(compiler/'UCC.exe'),'make','-Silent','-NoBind','ini=NexusTV.ini','-unattended'],cwd=compiler,capture_output=True,text=True,errors='replace',timeout=120)
(D/'assets-build.log').write_text(result.stdout+result.stderr,encoding='utf-8');print((result.stdout+result.stderr)[-2600:])
assert result.returncode==0 and compiled.exists(),result.returncode
sys.path.insert(0,'E:/l2-local/research/gludio-sky');from package_tools import Edit
p=Edit(compiled)
texture=next(i+1 for i,e in enumerate(p.exports) if e['name']=='Feed')
shader=p.obj('Diffuse',texture)+p.obj('SelfIllumination',texture)+p.boolean('TwoSided',True)+p.end()
p.add('ScreenMaterial','Engine.Shader',shader,flags=0xf0004)
# Bytecode/class assets are not used as NPC classes; only the mesh, animation and materials.
output=assets/'NexusTVPanel3.ukx';p.save(output)
exports={p.ref(i+1):p.ref(e['cl']) for i,e in enumerate(p.exports)}
(D/'asset-build.json').write_text(json.dumps({'mesh_vertices':len(vertices),'mesh_triangles':len(faces),'dimensions':[648,26,498],'display_dimensions':[600,450],'marker':marker,'exports':exports,'package':str(output),'native_ucc_compile':True},indent=2))
print('Built',output)
