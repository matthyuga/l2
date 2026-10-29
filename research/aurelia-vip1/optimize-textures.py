from PIL import Image
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'research/model-catalog/exports/aurelia-vip1'
for f in folder.glob('*_Color.jpg'):
    name=f.name.split('_2K')[0]
    source=ROOT/'research/model-catalog/exports/cc0-textures/ambientcg'/name/f.name
    im=Image.open(source).convert('RGB');im.thumbnail((1024,1024),Image.Resampling.LANCZOS);im.save(f,'JPEG',quality=88,optimize=True)
    print(f.name,im.size,f.stat().st_size)
for name in ['presentacion','terraza-vip']:
    f=ROOT/'mapas editados/aureliavip1'/(name+'.png')
    if f.exists():Image.open(f).convert('RGB').save(f.with_suffix('.jpg'),'JPEG',quality=84,optimize=True)
