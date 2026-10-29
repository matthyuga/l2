import json,urllib.request,subprocess,time
import imageio_ffmpeg
from pathlib import Path
root=Path('E:/l2-local')
url='http://127.0.0.1:8796'
token=(root/'nexus-tv/run/control-token-8796.txt').read_text()
def status():return json.load(urllib.request.urlopen(url+'/api/status',timeout=15))
def action(name,**data):
    req=urllib.request.Request(url+'/api/action',data=json.dumps(dict(action=name,**data)).encode(),headers={'Content-Type':'application/json','X-Nexus-Token':token})
    return json.load(urllib.request.urlopen(req,timeout=25))
initial=status()
for _ in range(100):
    if initial['ready']:break
    time.sleep(.2);initial=status()
assert initial['ready'],initial['error']
assert initial['version']==4 and initial['source']=='camera',initial
result={}
clip=root/'nexus-tv/media/_Verification1080p-20261017.mp4'
assert not clip.exists()
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=0x129be7:s=1920x1080:r=30','-t','2','-c:v','libx264','-pix_fmt','yuv420p',str(clip)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
try:
    action('volume',value=0)
    action('load',type='local',value=clip.name)
    time.sleep(1)
    action('pause');time.sleep(.5)
    native=root/'research/giran-screen/quality-v3/native/build/hd_test.exe'
    report=Path(__file__).with_name('installed-native.json')
    subprocess.run([str(native),'program',str(root/'research/giran-screen/quality-v3/install/d3d9.dll'),str(report)],check=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=25)
    result['receiver']=json.loads(report.read_text())
    result['version']=status()['version']
finally:
    action('camera')
    action('volume',value=initial['volume'])
    queue=status()['queue']
    for i in range(len(queue)-1,-1,-1):
        if queue[i].get('value')==clip.name:action('remove',index=i)
    clip.unlink()
    time.sleep(.5)
    state=status()
    result['restored']={k:state[k] for k in ['version','ready','source','profile','volume','error']}
    assert not state['error']
Path(__file__).with_name('installed-check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
