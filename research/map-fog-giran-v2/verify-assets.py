from pathlib import Path
import json
import numpy as np
from PIL import Image
base=Path(__file__).resolve().parent
names=(base/'build/texture-names.txt').read_text().splitlines()
assert names[4]=='bAlphaTexture'
for name in ['CloudTile','GiranClear']:
    im=Image.open(base/'assets'/(name+'.png')).convert('RGBA')
    raw=(base/'build'/(name+'.texture.raw')).read_bytes()
    assert raw.find(im.tobytes('raw','BGRA'))>=0, 'Compiled pixel mismatch: '+name
    assert raw[20:23]==bytes.fromhex('04d300'), 'Alpha flag mismatch: '+name
alpha=np.asarray(Image.open(base/'assets/GiranClear.png'))[:,:,3]
assert alpha.min()==0 and alpha.max()==255
assert np.any((alpha>0)&(alpha<255))
assert np.all(alpha[[0,-1],:]==255) and np.all(alpha[:,[0,-1]]==255)
print('PASS exact compiled BGRA pixels, alpha flags, transparent interior, opaque borders and graded edge.')
