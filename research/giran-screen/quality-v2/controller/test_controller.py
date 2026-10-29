"""Integration checks against the running local controller and its actual output."""
import asyncio
import json
import re
import subprocess
from pathlib import Path
import aiohttp
from channel import Channel, PROGRAM

ROOT = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8796'

async def main():
    checks = {}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=35)) as session:
        html = await (await session.get(URL)).text()
        token = re.search("const token='([^']+)'", html)[1]
        async def status():
            return await (await session.get(URL + '/api/status')).json()
        async def action(name, **data):
            response = await session.post(URL + '/api/action', json=dict(action=name, **data), headers={'X-Nexus-Token': token})
            result = await response.json()
            assert response.status == 200, result
            return result
        for _ in range(100):
            if (await status())['ready']:
                break
            await asyncio.sleep(.2)
        assert (await status())['ready']
        await action('volume', value=0)
        await action('loop', value=True)
        await action('load', type='local', value='Demo Nexus TV.mp4')
        await asyncio.sleep(.8)
        first = await (await session.get(URL + '/preview.jpg')).read()
        await asyncio.sleep(.8)
        second = await (await session.get(URL + '/preview.jpg')).read()
        assert first != second
        checks['local_moving_video'] = True
        await action('pause')
        await asyncio.sleep(.7)
        a = await status()
        await asyncio.sleep(.7)
        b = await status()
        assert a['player']['paused'] and abs(a['player']['position'] - b['player']['position']) < .15
        checks['pause'] = True
        await action('seek', value=3)
        await asyncio.sleep(.7)
        assert abs((await status())['player']['position'] - 3) < .2
        checks['seek'] = True
        # Paused content should survive through the real Direct3D9 receiver exactly.
        native = ROOT.parent / 'research/giran-screen/native'
        test = await asyncio.create_subprocess_exec(str(native / 'build/relay_test.exe'), 'program', str(native / 'program/d3d9.dll'), str(native / 'program-result.json'), creationflags=subprocess.CREATE_NO_WINDOW)
        assert await test.wait() == 0
        checks['native_d3d9_receiver'] = json.loads((native / 'program-result.json').read_text())
        await action('load', type='youtube', value='https://www.youtube.com/watch?v=M7lc1UVf-VE')
        for _ in range(60):
            state = await status()
            if state['player'].get('position', 0) > 2 and not state['player'].get('paused', True):
                break
            await asyncio.sleep(.4)
        assert state['source'] == 'youtube' and state['player']['position'] > 2 and not state['error'], state
        checks['youtube_online_playback'] = state['player']
        await action('previous')
        assert (await status())['source'] == 'local'
        checks['playlist_previous'] = True
        await action('camera')
        await asyncio.sleep(.4)
        checks['camera_switch'] = (await status())['source'] == 'camera'
        await action('off')
        await asyncio.sleep(.3)
        output = Channel(PROGRAM)
        _, age = output.read()
        assert age is not None and age < 1000
        output.close()
        checks['off_publishes_waiting_card'] = True
        response = await session.post(URL + '/api/action', json={'action': 'off'})
        assert response.status == 403
        checks['requires_control_token'] = True
        response = await session.post(URL + '/api/action', json={'action': 'load', 'type': 'local', 'value': '../server.py'}, headers={'X-Nexus-Token': token})
        assert response.status == 400
        checks['rejects_path_traversal'] = True
        # Leave a looping silent demo ready for the user's first in-world check.
        await action('loop', value=True)
        await action('load', type='local', value='Demo Nexus TV.mp4')
        await action('volume', value=30)
    (ROOT / 'run/integration-tests.json').write_text(json.dumps(checks, indent=2))
    print(json.dumps(checks, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
