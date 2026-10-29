from pathlib import Path
import subprocess,json
from PIL import Image
D=Path(__file__).resolve().parent;out=D/'verified-roundtrip';out.mkdir(exist_ok=True)
r=subprocess.run([str(D/'compiler/UCC.exe'),'batchexport',str(D/'assets/NexusTVAssets.ukx'),'Texture','tga',str(out),'ini=NexusTV.ini','-unattended'],cwd=D/'compiler',capture_output=True,text=True,errors='replace',timeout=60)
text=r.stdout+r.stderr;(D/'asset-reload.log').write_text(text,encoding='utf-8');print(text[-1500:])
assert r.returncode==0 and 'Success - 0 error(s), 0 warning(s)' in text
a=Image.open(D/'assets/Feed.tga').convert('RGBA');b=Image.open(out/'Feed.tga').convert('RGBA')
assert a.size==b.size==(512,512)
assert all(a.getpixel((x,0))[:3]==b.getpixel((x,0))[:3] for x in range(8))
(D/'texture-verification.json').write_text(json.dumps({'native_reload':True,'size':b.size,'marker_preserved':True,'package':'assets/NexusTVAssets.ukx'},indent=2))
print('PASS native package reload and exact screen texture marker.')
