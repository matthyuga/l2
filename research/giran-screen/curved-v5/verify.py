from pathlib import Path
import json,math,subprocess,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
g=json.loads((D/'geometry.json').read_text());v=np.array(g['vertices']);w=g['wedges'];faces=g['faces']
assert np.isfinite(v).all()
assert np.allclose(v[:,1].min(),-324) and np.allclose(v[:,1].max(),324)
assert (v[:,2].min(),v[:,2].max())==(0,498)
for a,b,c,material in faces:
    pts=np.array([v[w[i][0]] for i in [a,b,c]])
    normal=np.cross(pts[1]-pts[0],pts[2]-pts[0])
    assert np.linalg.norm(normal)>1e-5
    if material==0:
        assert all(0<=w[i][1]<=1 and 0<=w[i][2]<=1 for i in [a,b,c])
front=[v[i] for i in range(0,48*8) if i%8<4]
assert math.isclose(max(p[0] for p in front)-min(p[0] for p in front),48,abs_tol=1e-6)
assert math.isclose(max(p[1] for p in front)-min(p[1] for p in front),600,abs_tol=1e-6)
out=D/'roundtrip';out.mkdir(exist_ok=True)
package=D/'assets/NexusTVPanel4-linked.ukx'
# UCC verifies its mesh/texture output; the L2 pose is checked separately
# with a reader that supports Lineage's MeshAnimation version.
r=subprocess.run([str(D/'compiler/UCC.exe'),'batchexport',str(D/'assets/NexusTVPanel4.ukx'),'Texture','tga',str(out),'ini=NexusTV.ini','-unattended'],cwd=D/'compiler',capture_output=True,text=True,errors='replace',timeout=60)
(D/'native-reload.log').write_text(r.stdout+r.stderr,encoding='utf8')
assert r.returncode==0 and 'Success - 0 error(s), 0 warning(s)' in r.stdout+r.stderr
a=Image.open(D/'assets/Feed.tga').convert('RGBA');b=Image.open(out/'Feed.tga').convert('RGBA')
assert a.size==b.size==(2048,2048)
assert all(a.getpixel((x,0))==b.getpixel((x,0)) for x in range(8))
sys.path.insert(0,'E:/l2-local/research/gludio-sky')
from package_tools import Edit
p=Edit(package)
assert any(e['name']=='Screen' and p.ref(e['cl'])=='Engine.SkeletalMesh' for e in p.exports)
assert any(p.ref(-i-1)=='NexusTVMotion4.Dust2Motion' for i in range(len(p.imports)))
proof={'native_compile_and_reload':True,'texture_marker_preserved':True,'animation_import':'NexusTVMotion4.Dust2Motion','projected_outer_size':[648,498],'projected_picture_size':[600,450],'edge_advance':48,'arc_degrees':g['screen_arc_degrees'],'triangles':len(faces),'nondegenerate_triangles':True,'uv_range':[0,1]}
(D/'verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))

# Preview of the built mesh geometry, not an in-game screenshot.
from PIL import ImageDraw,ImageFont
im=Image.new('RGB',(1400,760),'#101824');draw=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf',24)
large=ImageFont.truetype('C:/Windows/Fonts/tahomabd.ttf',32)
draw.text((700,28),'Nexus TV · curva horizontal suave',font=large,anchor='mt',fill='white')
polys=[]
angle=math.radians(28)
def project(q):
    x,y,z=q
    horizontal=y*math.cos(angle)-x*math.sin(angle)
    depth=y*math.sin(angle)+x*math.cos(angle)
    return (400+horizontal*.9,625-z*.9+depth*.2)
for a,b,c,material in faces:
    pts=[v[w[i][0]] for i in [a,b,c]]
    depth=sum(q[1]*math.sin(angle)+q[0]*math.cos(angle) for q in pts)/3
    polys.append((depth,[project(q) for q in pts],'#268eae' if material==0 else '#435970'))
for _,polygon,color in sorted(polys,key=lambda item:item[0]):draw.polygon(polygon,fill=color)
draw.text((400,120),'Modelo curvo y marco',font=font,anchor='mt',fill='white')
draw.text((1070,220),'Vista desde arriba',font=font,anchor='mt',fill='white')
y=np.linspace(-300,300,200);depth=6+g['radius']-np.sqrt(g['radius']**2-y*y)
draw.line([(1070+float(a)*.8,340+float(b)*1.5) for a,b in zip(y,depth)],fill='#45c7df',width=5)
draw.line((830,349,1310,349),fill='#6c7b8c',width=1)
draw.text((1070,475),'Lado del espectador',font=font,anchor='mt',fill='white')
draw.text((1070,560),'Extremos adelantados: 48',font=font,anchor='mt',fill='#aebed0')
draw.text((700,710),'Vista previa de geometría. Comprobación dentro de Giran pendiente.',font=font,anchor='mt',fill='#aebed0')
im.save(D/'preview.png')
