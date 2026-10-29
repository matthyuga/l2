import json,time,urllib.request,urllib.error,sys
from pathlib import Path
ROOT=Path('E:/l2-local/nexus-tv');BASE='http://127.0.0.1:8797'
token=(ROOT/'run/control-token-8797.txt').read_text()
def request(path,data=None,form=False,auth=True):
    body=None if data is None else (urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode())
    headers={'Content-Type':'application/x-www-form-urlencoded' if form else 'application/json'}
    if auth:headers['X-Nexus-Token']=token
    with urllib.request.urlopen(urllib.request.Request(BASE+path,body,headers),timeout=25) as r:
        raw=r.read().decode();return raw if form else json.loads(raw)
def action(name,**kw):return request('/api/action',dict(action=name,**kw))
reports={}
action('volume',value=0);action('loop',value=True)
action('load',type='local',value='Demo 1080p30.mp4')
for quality in ['eco','balanced','hd','fullhd','uhd','fullhd']:
    action('quality',value=quality);time.sleep(5)
    s=request('/api/status');print(quality,s['canvas'],s['emission_fps'],s['content_fps'],s['process_ms'],s['error'],flush=True)
    assert not s['error'],s
    assert s['canvas']==[s['profiles'][quality]['width'],s['profiles'][quality]['height']]
    reports[quality]={k:s[k] for k in ['canvas','emission_fps','content_fps','process_ms','error']}
panel=request('/api/game',{'op':'panel'},form=True)
assert '.tv pause' in panel and '.tv quality fullhd' in panel and len(panel)<8100,len(panel)
request('/api/game',{'op':'pause'},form=True);time.sleep(.7)
assert request('/api/status')['player']['paused']
request('/api/game',{'op':'volume','arg':'10'},form=True)
assert request('/api/status')['volume']==10
request('/api/game',{'op':'seek','arg':'1'},form=True)
request('/api/game',{'op':'play'},form=True)
try:request('/api/game',{'op':'off'},form=True,auth=False);raise AssertionError('Unauthenticated mutation accepted')
except urllib.error.HTTPError as e:assert e.code==403
reports['remote']={'panel_length':len(panel),'pause_play_seek_volume':True,'unauthenticated_denied':True}
Path(__file__).with_name('benchmarks.json').write_text(json.dumps(reports,indent=2))
action('off')
print('PASS controller and game remote API',flush=True)
