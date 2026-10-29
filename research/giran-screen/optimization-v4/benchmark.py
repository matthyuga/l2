"""Isolated real player benchmark; never touches the production program channel."""
import os, sys, asyncio, json, time, statistics
from pathlib import Path
os.environ['NEXUS_TV_PORT']='8798'
sys.path.insert(0, str(Path(__file__).resolve().parents[3]/'nexus-tv'))
import server as s
from aiohttp import web
if '--baseline' in sys.argv:
    import types
    base=Path('E:/l2-local/backups/nexus-tv-opt-20261017')
    dm=types.ModuleType('baseline_decoder');exec(compile((base/'decoder.py').read_text(encoding='utf8'),str(base/'decoder.py'),'exec'),dm.__dict__)
    rm=types.ModuleType('baseline_renderer');exec(compile((base/'renderer.py').read_text(encoding='utf8'),str(base/'renderer.py'),'exec'),rm.__dict__)
    sm=types.ModuleType('baseline_server');sm.__file__=s.__file__
    exec(compile((base/'server.py').read_text(encoding='utf8'),str(base/'server.py'),'exec'),sm.__dict__)
    sm.Decoder=dm.Decoder;sm.Renderer=rm.Renderer;s=sm

async def main():
    p=s.Program()
    p.hd_output=s.Channel(s.HD_PROGRAM+'_OptTest',write=True)
    p.legacy_output=s.Channel(s.LEGACY_PROGRAM+'_OptTest',write=True,legacy=True)
    app=web.Application(); app['program']=p
    app.add_routes([web.get('/player.html',lambda _:web.FileResponse(s.ROOT/'public/player.html')),web.get('/media/{name}',s.media)])
    runner=web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner,'127.0.0.1',8798).start()
    result={}
    try:
        print('starting',flush=True)
        await p.start(); assert p.ready,p.error
        print('ready',flush=True)
        p.profile='fullhd'; p.loop=True
        await p.renderer.configure(1920,1440)
        await p.renderer.command('volume',0); await p.renderer.command('loop',True)
        async with p.control_lock:
            await p.select(dict(type='local',value='Demo 1080p30.mp4'))
        print('local selected',flush=True)
        await asyncio.sleep(3)
        # Preserve all timestamps, including gaps, for interval and window analysis.
        from collections import deque
        p.emission_times=deque(maxlen=10000);p.content_times=deque(maxlen=10000);p.cost_times=deque(maxlen=10000)
        await asyncio.sleep(20)
        ts=list(p.emission_times); ct=list(p.content_times)
        intervals=[1000*(b-a) for a,b in zip(ts,ts[1:])]
        result['local']={'emission_fps':(len(ts)-1)/(ts[-1]-ts[0]),'content_fps':(len(ct)-1)/(ct[-1]-ct[0]),'mean_process_ms':statistics.mean(p.cost_times),'p95_interval_ms':sorted(intervals)[int(len(intervals)*.95)],'max_interval_ms':max(intervals),'frames':len(ts),'error':p.error}
        print(json.dumps(result),flush=True)
        Path(sys.argv[1]).write_text(json.dumps(result,indent=2),encoding='utf8')
        await p.action(dict(action='pause'));await asyncio.sleep(.6)
        a=p.cached_pixels;await asyncio.sleep(.4);assert a==p.cached_pixels
        await p.action(dict(action='seek',value=3));await asyncio.sleep(.6)
        assert abs(p.player_status['position']-3)<.15
        result['pause_seek']=True
        await p.action(dict(action='play'));await asyncio.sleep(.5)
        assert not p.player_status['paused']
        result['resume']=True
        if '--youtube' in sys.argv:
            async with p.control_lock:await p.select(dict(type='youtube',value='M7lc1UVf-VE'))
            await asyncio.sleep(10)
            p.emission_times.clear();p.content_times.clear();p.cost_times.clear()
            await asyncio.sleep(20)
            state=p.status()
            result['youtube']={k:state[k] for k in ['emission_fps','content_fps','process_ms','player','error']}
        if '--checks' in sys.argv:
            import struct,ctypes
            await p.action(dict(action='camera'));await asyncio.sleep(.3)
            await p.action(dict(action='off'));await asyncio.sleep(.5)
            for profile in ['eco','hd','uhd','fullhd']:
                await p.action(dict(action='quality',value=profile));await asyncio.sleep(.5)
                _,magic,w,h,_=struct.unpack('<IIIIQ',ctypes.string_at(p.output.ptr,24))
                assert (w,h)==(s.PROFILES[profile]['width'],s.PROFILES[profile]['height'])
                assert magic==0x3356544e
            await asyncio.sleep(.5)
            for channel in [p.hd_output,p.legacy_output]:
                raw,age=channel.read();assert raw and age<1000
            assert p.preview[:2]==b'\xff\xd8'
            p.queue=[dict(type='local',value='Demo 1080p30.mp4'),dict(type='local',value='Demo HD 720p30.mp4')]
            p.position=0
            await p.action(dict(action='next'));await asyncio.sleep(.5)
            assert p.selected==p.queue[1]
            await p.action(dict(action='previous'));await asyncio.sleep(.5)
            assert p.selected==p.queue[0]
            assert not p.error,p.error
            result['switch_quality_legacy_preview_playlist']=True
        print(json.dumps(result,indent=2))
        Path(sys.argv[1]).write_text(json.dumps(result,indent=2),encoding='utf8')
    finally:
        await p.close();await runner.cleanup()

if __name__=='__main__':
    asyncio.set_event_loop_policy(s.MediaPolicy())
    s.ctypes.WinDLL('winmm').timeBeginPeriod(1)
    try:asyncio.run(asyncio.wait_for(main(),150))
    finally:s.ctypes.WinDLL('winmm').timeEndPeriod(1)
