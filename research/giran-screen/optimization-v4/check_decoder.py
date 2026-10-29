import sys,types,asyncio,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'nexus-tv'))
from decoder import Decoder
old=types.ModuleType('old')
exec(Path('E:/l2-local/backups/nexus-tv-opt-20261017/decoder.py').read_text(encoding='utf8'),old.__dict__)
root=Path('E:/l2-local/nexus-tv/media')
checks=[]
for name,w,h in [('Demo 1080p30.mp4',1920,1440),('Demo HD 720p30.mp4',960,720),('Demo 4K15.mp4',3840,2880)]:
    a=old.Decoder(root/name,w,h,30,loop=True);b=Decoder(root/name,w,h,30,loop=True)
    a.open();b.open()
    for pos in [0,.1,.5,2,1,0]:
        x,xc=a.read(pos);y,yc=b.read(pos)
        assert x==bytes(y) and xc==yc,(name,pos)
        image=np.frombuffer(y,np.uint8).reshape(h,w,4)
        assert np.all(image[:,:,3]==255)
    a.cap.release();b.cap.release()
    checks.append({'source':name,'canvas':[w,h],'byte_identical':True,'seek_backward':True,'alpha_opaque':True})
print(json.dumps(checks,indent=2))
Path(__file__).with_name('decoder-checks.json').write_text(json.dumps(checks,indent=2))
