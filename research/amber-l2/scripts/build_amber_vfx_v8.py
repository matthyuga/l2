"""Native UE2 quality pass: slender solid arrows and soft additive particles."""
from pathlib import Path
from PIL import Image
import math, struct, subprocess, json
root=Path(__file__).resolve().parents[1];editor=root/'tools/l2editor/L2Editor'
stage=root/'exports/contract/combat-vfx-v8';assets=stage/'assets';assets.mkdir(parents=True,exist_ok=True)
pkg=editor.parent/'AmberParticlesV8/Classes';pkg.mkdir(parents=True,exist_ok=True)

# Explicitly premultiply RGB against black: additive drawing cannot show the
# rectangular RGB hidden underneath transparent pixels in source images.
src=Image.open(root/'assets/external/kenney-particle-pack/source/PNG (Transparent)/flame_05.png').convert('RGBA').resize((256,256))
flame=Image.new('RGBA',src.size);p=flame.load()
for y in range(256):
 for x in range(256):
  r,g,b,a=src.getpixel((x,y));edge=max(0,min(1,x/30,(255-x)/30,y/30,(255-y)/30))
  v=(max(r,g,b)/255)*(a/255)*edge
  p[x,y]=(round(255*v),round(145*v),round(38*v),255)
flame.save(assets/'Flame.tga')
for name,kind in [('Glow','glow'),('Area','area')]:
 size=256 if kind=='glow' else 512;im=Image.new('RGBA',(size,size));pix=im.load()
 for y in range(size):
  for x in range(size):
   r=math.hypot((x+.5-size/2)/(size/2),(y+.5-size/2)/(size/2))
   if kind=='glow':v=max(0,1-r)**3;rgb=(255,240,205)
   else:
    edge=math.exp(-((r-.93)/.012)**2)*.7+math.exp(-((r-.93)/.045)**2)*.22
    fill=.055*max(0,1-(r/.94)**10) if r<.94 else 0
    inner=.08*math.exp(-((r-.60)/.008)**2)
    v=min(1,edge+fill+inner)*max(0,min(1,(1-r)/.04))**2;rgb=(255,177,42)
   pix[x,y]=tuple(round(c*v) for c in rgb)+(255,)
 im.save(assets/(name+'.tga'))
# Uniform bronze avoids dependence on unsupported LWO UV import behavior.
im=Image.new('RGBA',(8,8),(165,136,91,255))
im.save(assets/'ArrowMaterial.tga')

def chunk(tag,data):return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
def sub(tag,data):return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
def mesh(name,orientation):
 verts=[];uv=[];faces=[]
 def vertex(v,u):verts.append(v);uv.append((u,.5));return len(verts)-1
 def cylinder(z1,z2,r1,r2,u):
  start=len(verts)
  for z,r in [(z1,r1),(z2,r2)]:
   for i in range(8):
    a=i*math.tau/8;vertex((r*math.cos(a),r*math.sin(a),z),u)
  for i in range(8):
   j=(i+1)%8;faces.extend([(start+i,start+j,start+8+j),(start+i,start+8+j,start+8+i)])
 cylinder(-10,12,.24,.24,.16)
 cylinder(-18,-12,0,1.15,.50)
 for a in [0,math.tau/3,2*math.tau/3]:
  ids=[vertex((r*math.cos(a),r*math.sin(a),z),.83) for r,z in [(.24,5),(1.6,12),(.24,12)]]
  faces.extend([tuple(ids),tuple(reversed(ids))])
 def transform(v):
  x,y,z=v
  world=(x,y,-z) if orientation=='up' else (-z,y,x) if orientation=='forward' else v
  return world[0],world[2],world[1] # LWO Y-up -> imported UE Z-up
 material='ArrowMaterial';s0=(material+'\0\0').encode()
 mapping=sub(b'IMAP',b'1\0'+sub(b'CHAN',b'COLR')+sub(b'ENAB',struct.pack('>H',1)))+sub(b'PROJ',struct.pack('>H',5))+sub(b'VMAP',b'Texture\0')
 surface=s0+sub(b'COLR',struct.pack('>fffH',1,1,1,0))+sub(b'SIDE',struct.pack('>H',3))+sub(b'BLOK',mapping)
 data=b'LWO2'+chunk(b'PNTS',b''.join(struct.pack('>fff',*transform(v)) for v in verts))+chunk(b'POLS',b'FACE'+b''.join(struct.pack('>HHHH',3,*f) for f in faces))+chunk(b'TAGS',(material+'\0').encode())+chunk(b'PTAG',b'SURF'+b''.join(struct.pack('>HH',i,0) for i in range(len(faces))))+chunk(b'VMAP',b'TXUV'+struct.pack('>H',2)+b'Texture\0'+b''.join(struct.pack('>Hff',i,*v) for i,v in enumerate(uv)))+chunk(b'SURF',surface)
 (assets/(name+'.lwo')).write_bytes(b'FORM'+struct.pack('>I',len(data))+data)
for n,o in [('ArrowDown','down'),('ArrowUp','up'),('ArrowForward','forward')]:mesh(n,o)
imports='\n'.join(f'#exec TEXTURE IMPORT NAME={n} FILE="{(assets/(n+".tga")).as_posix()}" MIPS=ON' for n in ['Flame','Glow','Area','ArrowMaterial'])
imports+='\n'+'\n'.join(f'#exec STATICMESH IMPORT NAME={n} FILE="{(assets/(n+".lwo")).as_posix()}"' for n in ['ArrowDown','ArrowUp','ArrowForward'])
(pkg/'A_VfxBase.uc').write_text('class A_VfxBase extends Emitter;\n'+imports+'''
defaultproperties
{
 AutoDestroy=True
 bNoDelete=False
 bHidden=False
 bDirectional=True
}
''')
spawn='AutomaticInitialSpawning=False\n InitialParticlesPerSecond=10000\n RespawnDeadParticles=False\n SecondsBeforeInactive=0.0\n CoordinateSystem=PTCS_Relative'
def actor(name,parts,life):
 text=f'class {name} extends A_VfxBase;\ndefaultproperties\n{{\n'
 for i,(kind,props) in enumerate(parts):text+=f' Begin Object Class={kind} Name=P{i}\n{props}\n End Object\n Emitters({i})={kind}\'P{i}\'\n'
 text+=f' LifeSpan={life}\n}}\n';(pkg/(name+'.uc')).write_text(text)
def loc(x,y,z):return f'(X=(Min={x},Max={x}),Y=(Min={y},Max={y}),Z=(Min={z},Max={z}))'
def arrow(mesh,x,y,z,v,life,delay=0,forward=False):
 return ('MeshEmitter',f"StaticMesh=StaticMesh'AmberParticlesV8.{mesh}'\nUseParticleColor=False\nUseCollision=False\nMaxParticles=1\nStartLocationRange={loc(x,y,z)}\nStartVelocityRange={loc(v if forward else 0,0,0 if forward else v)}\nStartSizeRange={loc(.85,.85,.85)}\nLifetimeRange=(Min={life},Max={life})\nInitialDelayRange=(Min={delay},Max={delay})\n{spawn}")
def sprite(texture,x,y,z,v,life,size,fire=False,delay=0,forward=False,projection=False):
 return ('SpriteEmitter',f"Texture=Texture'AmberParticlesV8.{texture}'\nDrawStyle=PTDS_Brighten\nMaxParticles=1\nUseColorScale=True\nColorScale(0)=(RelativeTime=0.0,Color=(R=255,G=255,B=255,A=255))\nColorScale(1)=(RelativeTime=1.0,Color=(R=255,G=255,B=255,A=0))\nFadeOut=True\nFadeOutStartTime={life*.65}\nStartLocationRange={loc(x,y,z)}\nStartVelocityRange={loc(v if forward else 0,0,0 if forward else v)}\nStartSizeRange={loc(size,size,size)}\nLifetimeRange=(Min={life},Max={life})\nInitialDelayRange=(Min={delay},Max={delay})\n"+('UseDirectionAs=PTDU_Normal\nProjectionNormal=(Z=1.0)\n' if projection else '')+spawn)
positions=[]
for radius,count in [(45,10),(110,16),(175,24)]:
 for i in range(count):a=math.tau*(i+.5)/count;positions.append((round(radius*math.cos(a),3),round(radius*math.sin(a),3)))
sky=[]
for i in range(50):
 delay=i*.04;x=(i%5-2)*3;y=(i//5%3-1)*3
 sky+=[arrow('ArrowUp',x,y,55,650,1.15,delay),sprite('Glow',x,y,45,650,1.15,2.5,delay=delay)]
actor('SkyVolley',sky,3.6)
for fire in [False,True]:
 for wave in range(3):
  parts=[];impact=[];name=('FireRain' if fire else 'Rain')+str(wave+1)
  for x,y in positions[wave::3]:
   parts+=[arrow('ArrowDown',x,y,405.3,-600,.65),sprite('Flame' if fire else 'Glow',x,y,418,-600,.65,5 if fire else 2)]
   if fire:parts+=[sprite('Flame',x,y,429,-600,.65,3.5)]
   impact+=[sprite('Glow',x,y,5,12,.28,9 if fire else 4)]
   if fire:impact+=[sprite('Flame',x,y,8,32,.42,8)]
  actor(name,parts,1);actor(name+'Impact',impact,1)
for level in range(1,17):
 life=level*50/1400
 parts=[arrow('ArrowForward',0,0,0,1400,life,forward=True)]
 for i in range(4):parts+=[sprite('Flame',-i*5,0,0,1400,life,5-i*.65,forward=True)]
 actor('FireShot'+str(level),parts,1)
area=sprite('Area',0,0,3,0,5.8,215,projection=True)
area=(area[0],area[1]+'\nUseSizeScale=True\nSizeScale(0)=(RelativeTime=0.0,RelativeSize=0.15)\nSizeScale(1)=(RelativeTime=0.06,RelativeSize=1.0)\nSizeScale(2)=(RelativeTime=1.0,RelativeSize=1.0)')
actor('Mark',[area],5.9)
(stage/'trajectory.json').write_text(json.dumps(dict(skyArrows=50,rainArrows=50,waveCounts=[17,17,16],radius=200,arrowLength=30,shaftDiameter=.48,scale=.85,impactMs=650),indent=2))
(editor/'AmberParticlesV8.ini').write_text((editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberParticlesV8\n',encoding='latin1')
out=editor/'AmberParticlesV8.u'
if out.exists():out.unlink()
r=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=AmberParticlesV8.ini'],cwd=editor,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=120)
(root/'reports/amber-particles-v8-build.log').write_bytes(r.stdout+r.stderr)
assert r.returncode==0 and out.exists(),r.stdout[-3000:]
print('PASS: native quality assets compiled; 3D arrows, premultiplied soft flame, projected soft area.')
