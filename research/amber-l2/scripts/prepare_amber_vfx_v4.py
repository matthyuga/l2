"""Create a separate V4 staging build; never change loaded client packages."""
from pathlib import Path
import math, struct
from PIL import Image
root=Path(__file__).resolve().parents[1]
assets=root/'exports/contract'
def chunk(tag,data): return tag+struct.pack('>I',len(data))+data+(b'\0' if len(data)%2 else b'')
def sub(tag,data): return tag+struct.pack('>H',len(data))+data+(b'\0' if len(data)%2 else b'')
def ground_mesh(name,bands):
    vertices=[];faces=[]
    for inner,outer in bands:
        start=len(vertices)
        for i in range(96):
            angle=2*math.pi*i/96
            for radius in [inner,outer]:vertices.append((radius*math.cos(angle),0,radius*math.sin(angle)))
        for i in range(96):
            a=start+2*i;b=start+2*((i+1)%96)
            faces.extend([(a,a+1,b+1),(a,b+1,b)])
    faces+= [tuple(reversed(f)) for f in faces]
    material='AreaGold' if name=='AreaRing' else 'AreaFill'
    tags=(material+'\0').encode()
    surf=(material+'\0\0').encode()+sub(b'COLR',struct.pack('>fffH',1,.65,.08,0))+sub(b'SIDE',struct.pack('>H',3))
    data=b'LWO2'+chunk(b'PNTS',b''.join(struct.pack('>fff',*v) for v in vertices))+chunk(b'POLS',b'FACE'+b''.join(struct.pack('>HHHH',3,*f) for f in faces))+chunk(b'TAGS',tags)+chunk(b'PTAG',b'SURF'+b''.join(struct.pack('>HH',i,0) for i in range(len(faces))))+chunk(b'SURF',surf)
    (assets/(name+'.lwo')).write_bytes(b'FORM'+struct.pack('>I',len(data))+data)
ground_mesh('AreaRing',[(194,200),(130,132)])
ground_mesh('AreaDisk',[(0,194)])
Image.new('RGBA',(8,8),(255,185,35,255)).save(assets/'AreaGold.tga')
Image.new('RGBA',(8,8),(255,135,15,45)).save(assets/'AreaFill.tga')
source=(root/'scripts/build_amber_vfx_v3.js').read_text().replace('V3','V4').replace('v3','v4')
source=source.replace("[[50,6],[115,10],[175,14]]","[[45,10],[110,16],[175,24]]")
source=source.replace("positions.map((p,i)=>arrow(i,fire?'ArrowFire':'ArrowWhite',p.x,p.y,430,-600,.650,1.25))", "positions.flatMap((p,i)=>[arrow(i*2,fire?'ArrowFire':'ArrowWhite',p.x,p.y,430,-600,.650,1.25),glow(i*2+1,fire,p.x,p.y,430,.650,8,1).replace('StartVelocityRange=(X=(Min=-15,Max=15),Y=(Min=-15,Max=15),Z=(Min=10,Max=45))','StartVelocityRange=(Z=(Min=-600,Max=-600))')])")
source=source.replace('#exec STATICMESH IMPORT NAME=ArrowWhite', '#exec TEXTURE IMPORT NAME=AreaGold FILE="${asset}/AreaGold.tga" MIPS=OFF\n#exec TEXTURE IMPORT NAME=AreaFill FILE="${asset}/AreaFill.tga" MIPS=OFF\n#exec STATICMESH IMPORT NAME=AreaRing FILE="${asset}/AreaRing.lwo"\n#exec STATICMESH IMPORT NAME=AreaDisk FILE="${asset}/AreaDisk.lwo"\n#exec STATICMESH IMPORT NAME=ArrowWhite')
start=source.index('const sky=');end=source.index("fs.writeFileSync(path.join(pkg,'ShotCharge",start)
source=source[:start]+'''// Sixty independently scheduled arrows: exact total, no recycled particle count.
const sky=Array.from({length:60},(_,i)=>[arrow(i*2,'ArrowSky',(i%5-2)*5,(Math.floor(i/5)%3-1)*5,55,650,1.15,1.6),glow(i*2+1,false,(i%5-2)*5,(Math.floor(i/5)%3-1)*5,55,1.15,8,1).replace('StartVelocityRange=(X=(Min=-15,Max=15),Y=(Min=-15,Max=15),Z=(Min=10,Max=45))','StartVelocityRange=(Z=(Min=650,Max=650))')].map(c=>c.replace('LifetimeRange=',`InitialDelayRange=(Min=${(i*.04).toFixed(3)},Max=${(i*.04).toFixed(3)})\\n        LifetimeRange=`))).flat();
fs.writeFileSync(path.join(pkg,'SkyVolley.uc'),actor('SkyVolley',sky,3.6));
'''+source[end:]
source=source.replace("[component],1)","[component,glow(1,true,-12,0,0,Number(life),9,8,true).replace('StartVelocityRange=(X=(Min=-15,Max=15),Y=(Min=-15,Max=15),Z=(Min=10,Max=45))','StartVelocityRange=(X=(Min=1400,Max=1400))')],1)")
start=source.index('const mark=');end=source.index('const manifest=',start)
source=source[:start]+'''// Real horizontal geometry rather than camera-facing sprite projection.
const mark=['AreaRing','AreaDisk'].map((mesh,i)=>`    Begin Object Class=MeshEmitter Name=P${i}
        StaticMesh=StaticMesh'AmberParticlesV4.${mesh}'
        UseMeshBlendMode=False
        DrawStyle=PTDS_AlphaBlend
        UseParticleColor=True
        UseColorScale=True
        ColorScale(0)=(RelativeTime=0.0,Color=(R=255,G=190,B=45,A=${i===0?255:45}))
        ColorScale(1)=(RelativeTime=0.92,Color=(R=255,G=150,B=20,A=${i===0?255:45}))
        ColorScale(2)=(RelativeTime=1.0,Color=(R=255,G=100,B=10,A=0))
        UseSizeScale=True
        SizeScale(0)=(RelativeTime=0.0,RelativeSize=0.15)
        SizeScale(1)=(RelativeTime=0.06,RelativeSize=1.0)
        SizeScale(2)=(RelativeTime=1.0,RelativeSize=1.0)
        CoordinateSystem=PTCS_Absolute
        MaxParticles=1
        StartLocationRange=(Z=(Min=${8+i},Max=${8+i}))
        StartSizeRange=(X=(Min=1,Max=1),Y=(Min=1,Max=1),Z=(Min=1,Max=1))
        LifetimeRange=(Min=5.8,Max=5.8)
        ${spawning}
    End Object`);
fs.writeFileSync(path.join(pkg,'Mark.uc'),actor('Mark',mark,5.9));
'''+source[end:]
source=source.replace('rainRadius:200,positions','skyArrows:60,skyReleaseIntervalMs:40,rainRadius:200,positions')
(root/'scripts/build_amber_vfx_v4.js').write_text(source)
stage=root/'exports/contract/combat-vfx-v4/server/custom/AmberContract'
stage.mkdir(parents=True,exist_ok=True)
project=root.parents[1]
for filename in ['AmberContract.java','AmberServitor.java']:
    baseline=project/'backups/amber-vfx-v4-2026-10-10/server/game/data/scripts/custom/AmberContract'/filename
    if not baseline.exists(): baseline=project/'server/game/data/scripts/custom/AmberContract'/filename
    source=baseline.read_text()
    source=source.replace('import org.l2jmobius.gameserver.network.serverpackets.MagicSkillUse;', 'import org.l2jmobius.gameserver.network.serverpackets.MagicSkillUse;\nimport org.l2jmobius.gameserver.network.serverpackets.MagicSkillLaunched;')
    if filename=='AmberContract.java':
        source=source.replace('a.broadcastPacket(new MagicSkillUse(s.marker,s.marker,19010,1,100,0));','a.broadcastPacket(new MagicSkillUse(a,s.marker,19010,1,0,0));\n        a.broadcastPacket(new MagicSkillLaunched(a,19010,1,s.marker));')
        source=source.replace('a.broadcastPacket(new MagicSkillUse(a,a,19006,1,3500,0));','a.broadcastPacket(new MagicSkillUse(a,a,19006,1,3500,0));\n        a.broadcastPacket(new MagicSkillLaunched(a,19006,1,a));')
        source=source.replace('a.broadcastPacket(new MagicSkillUse(anchor,anchor,visual,1,0,0));','a.broadcastPacket(new MagicSkillUse(a,anchor,visual,1,0,0));\n                        a.broadcastPacket(new MagicSkillLaunched(a,visual,1,anchor));')
    else:
        source=source.replace('broadcastPacket(new MagicSkillUse(this,target,19009,level,0,0));','{\n                    broadcastPacket(new MagicSkillUse(this,target,19009,level,0,0));\n                    broadcastPacket(new MagicSkillLaunched(this,19009,level,target));\n                }')
    (stage/filename).write_text(source)
print('V4 staging sources generated: 60 ascending arrows, 50 descending per wave, horizontal area meshes, fire glow.')
