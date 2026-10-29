from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).parent;T=R/'native-export/FFighter/Texture'; names=['FFighter_m001_t01_u_ori','FFighter_m001_t01_l_ori','FFighter_m001_t01_b_ori','FFighter_m001_t01_g_ori','FFighter_m001_t00_m00_ah_ori','FFighter_m001_t00_m00_bh','FFighter_m000_t00_f'];atlas=Image.new('RGBA',(2048,1024),(0,0,0,255));report=[]
for i,n in enumerate(names):
 p=T/(n+'.tga');im=Image.open(p).convert('RGBA').resize((496,496),Image.Resampling.LANCZOS);x=(i%4)*512;y=(i//4)*512
 # 8px duplicate border prevents adjacent tile filtering. Blender UV V origin bottom; PIL y top.
 atlas.paste(im.resize((512,512),Image.Resampling.NEAREST),(x,y));atlas.paste(im,(x+8,y+8));report.append({'texture':n,'tile':i,'pixel_xy':[x+8,y+8],'uv_scale':[496/2048,496/1024],'uv_offset':[(x+8)/2048,1-(y+8+496)/1024],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
atlas.save(R/'BodyAtlas.png');atlas.save(R/'BodyAtlas.tga');(R/'atlas-tiles.json').write_text(json.dumps(report,indent=2))
