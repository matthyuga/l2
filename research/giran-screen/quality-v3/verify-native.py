from pathlib import Path
import sys,subprocess,time,json,numpy as np
sys.path.insert(0,'E:/l2-local/nexus-tv')
from channel import Channel,PROGRAM
root=Path(__file__).parent/'native';ch=Channel(PROGRAM,write=True)
reports={}
for w,h in [(640,480),(1280,960),(1920,1440),(3840,2880)]:
    data=np.full((h,w),0xff129be7,dtype=np.uint32).tobytes();report=root/f'test-{w}.json'
    ch.publish(data,w,h)
    p=subprocess.Popen([str(root/'build/hd_test.exe'),'program',str(root/'build/d3d9.dll'),str(report)],creationflags=subprocess.CREATE_NO_WINDOW)
    deadline=time.monotonic()+40
    while p.poll() is None:
        if time.monotonic()>deadline:
            p.terminate();raise TimeoutError('Native verification timed out')
        ch.publish(data,w,h);time.sleep(.033)
    reports[str(w)]={'exit':p.returncode,**json.loads(report.read_text())}
    print(w,reports[str(w)],flush=True)
ch.close()
(root/'dynamic-tests.json').write_text(json.dumps(reports,indent=2))
assert all(v['exit']==0 and v['correct_frames']>=160 for v in reports.values())
