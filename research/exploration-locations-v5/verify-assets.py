from pathlib import Path
from PIL import Image
from decode_catalog import Reader
from extract_grid import texture
base=Path(__file__).resolve().parent
r=Reader(base/'raw/Palette1.raw');assert r.compact()==2;assert r.compact()==256
palette=[tuple(r.read('BBBB')) for _ in range(256)];assert r.pos==len(r.data)
im=Image.open(base/'textures/l2zonename/Texture/24_15.tga').convert('RGB')
indices=texture(base/'raw/24_15.raw')
assert list(im.getdata())==[palette[p][:3] for p in indices]
print('PASS original P8 bytes and orientation match independent UModel/Pillow export for all16384 Ketra pixels.')
