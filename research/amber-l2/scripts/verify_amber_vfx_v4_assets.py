from pathlib import Path
import struct, math
from PIL import Image
root=Path(__file__).resolve().parents[1]
export=root/'exports/vfx-v4-assets/AmberParticlesV4'
for name in ['GlowWhite','GlowFire','AmberWhite','AmberFire','AreaGold','AreaFill']:
    original=Image.open(root/'exports/contract'/f'{name}.tga').convert('RGBA')
    compiled=Image.open(export/'Texture'/f'{name}.tga').convert('RGBA')
    assert original.size==compiled.size and original.tobytes()==compiled.tobytes(),name
def points(name):
    data=(export/'StaticMesh'/f'{name}.pskx').read_bytes();offset=0
    while offset+32<=len(data):
        tag,_,size,count=struct.unpack_from('<20siii',data,offset);offset+=32
        if tag.rstrip(b'\0')==b'PNTS0000': return list(struct.iter_unpack('<fff',data[offset:offset+size*count]))
        offset+=size*count
    raise AssertionError(name)
for name,radius in [('AreaRing',200),('AreaDisk',194)]:
    p=points(name)
    assert max(abs(z) for x,y,z in p)<0.001,(name,'must lie on world XY plane')
    assert abs(max(math.hypot(x,y) for x,y,z in p)-radius)<0.001,(name,'radius')
assert max(x for x,y,z in points('ArrowShot'))==32,'fire arrow must point along local forward X'
assert min(z for x,y,z in points('ArrowWhite'))==-32,'falling arrow tip must point down'
assert max(z for x,y,z in points('ArrowSky'))==32,'ascending arrow tip must point up'
print('PASS: six compiled textures match source pixels; ground meshes are horizontal with radius 200/194; all arrow tips face their trajectory.')
