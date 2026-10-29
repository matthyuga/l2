"""A dedicated player owned by Nexus TV, using an isolated Chrome profile.

This never attaches to the user's browser. Frames are the product's video output,
not desktop capture. Only the local player document is controlled.
"""
import asyncio
import base64
import json
import hashlib
import subprocess
from pathlib import Path

class Renderer:
    def __init__(self, root, origin, session):
        self.root, self.origin, self.session = root, origin, session
        self.page_url = origin + "/player.html?v=" + hashlib.sha256((root/"public/player.html").read_bytes()).hexdigest()[:12]
        self.process = self.ws = None
        self.serial = 0
        self.pending = {}
        self.reader = None
        self.latest = None
        self.frame_id = 0
        self.frame_time = 0
        self.frame_ready = asyncio.Event()
        self.stream_enabled = False
        self.width,self.height = 1280,960

    async def start(self):
        profile = self.root / 'run' / 'player-profile-hd'
        profile.mkdir(parents=True, exist_ok=True)
        active = profile / 'DevToolsActivePort'
        if active.exists():
            active.unlink()
        choices = [Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),
                   Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')]
        executable = next((p for p in choices if p.exists()), None)
        if not executable:
            raise RuntimeError('Se necesita Chrome o Edge para el reproductor dedicado.')
        self.log = (self.root / 'run' / 'player.log').open('a', encoding='utf8')
        self.process = subprocess.Popen([
            str(executable), '--headless=new', '--remote-debugging-address=127.0.0.1',
            '--remote-debugging-port=0', '--user-data-dir=' + str(profile),
            '--no-first-run', '--no-default-browser-check', '--autoplay-policy=no-user-gesture-required',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows', '--window-size=512,384',
            self.page_url], stdout=self.log, stderr=self.log,
            creationflags=subprocess.CREATE_NO_WINDOW)
        port = None
        for _ in range(100):
            if self.process.poll() is not None:
                raise RuntimeError('El reproductor dedicado no pudo iniciar. Ver run/player.log.')
            if active.exists():
                lines = active.read_text().splitlines()
                if lines:
                    port = int(lines[0])
                    break
            await asyncio.sleep(.1)
        if not port:
            raise RuntimeError('El reproductor no respondio al iniciar.')
        target = None
        for _ in range(60):
            async with self.session.get(f'http://127.0.0.1:{port}/json/list') as response:
                pages = await response.json()
            target = next((p for p in pages if p.get('url') == self.page_url), None)
            if target:
                break
            await asyncio.sleep(.1)
        if not target:
            raise RuntimeError('No se encontro el documento del reproductor propio.')
        self.ws = await self.session.ws_connect(target['webSocketDebuggerUrl'], max_msg_size=4 * 1024**2)
        self.reader = asyncio.create_task(self.receive())
        await self.configure(1280, 960)
        for _ in range(60):
            value = await self.evaluate('typeof window.tv === "object"')
            if value:
                return
            await asyncio.sleep(.1)
        raise RuntimeError('No se cargo el reproductor.')

    async def receive(self):
        try:
            async for message in self.ws:
                if message.type.name != 'TEXT':
                    break
                data = json.loads(message.data)
                if data.get('method') == 'Page.screencastFrame':
                    self.latest = base64.b64decode(data['params']['data'])
                    self.frame_id += 1
                    self.frame_time = asyncio.get_running_loop().time()
                    self.frame_ready.set()
                    self.serial += 1
                    await self.ws.send_json(dict(id=self.serial, method='Page.screencastFrameAck', params={'sessionId':data['params']['sessionId']}))
                elif data.get('id') in self.pending:
                    future = self.pending.pop(data['id'])
                    if not future.done():
                        future.set_result(data)
        finally:
            for future in self.pending.values():
                if not future.done():
                    future.set_exception(RuntimeError('Se cerr? el reproductor'))
            self.pending.clear()

    async def call(self, method, params):
        self.serial += 1
        serial = self.serial
        future = asyncio.get_running_loop().create_future()
        self.pending[serial] = future
        try:
            await self.ws.send_json(dict(id=serial, method=method, params=params))
            data = await asyncio.wait_for(future, 20)
            if 'error' in data:
                raise RuntimeError(str(data['error']))
            return data.get('result', {})
        finally:
            self.pending.pop(serial, None)

    async def configure(self, width, height):
        await self.call('Page.stopScreencast', {})
        self.width,self.height=width,height
        await self.call('Emulation.setDeviceMetricsOverride', dict(width=width,height=height,deviceScaleFactor=1,mobile=False))
        self.latest = None
        self.frame_ready.clear()
        if self.stream_enabled:
            await self.call('Page.startScreencast', dict(format='jpeg',quality=90,maxWidth=width,maxHeight=height,everyNthFrame=1))

    async def set_stream(self,enabled):
        if enabled == self.stream_enabled:
            return
        self.stream_enabled=enabled
        if enabled:
            self.latest=None;self.frame_ready.clear()
            await self.call('Page.startScreencast',dict(format='jpeg',quality=90,maxWidth=self.width,maxHeight=self.height,everyNthFrame=1))
        else:
            await self.call('Page.stopScreencast',{})

    async def evaluate(self, expression):
        result = await self.call('Runtime.evaluate', dict(expression=expression, returnByValue=True, awaitPromise=True))
        if 'exceptionDetails' in result:
            raise RuntimeError(result['exceptionDetails'].get('text', 'Error del reproductor'))
        return result.get('result', {}).get('value')

    async def command(self, command, value=None):
        return await self.evaluate('window.tv.command(' + json.dumps(command) + ',' + json.dumps(value) + ')')

    async def frame(self):
        if self.latest is None:
            await asyncio.wait_for(self.frame_ready.wait(), 5)
        return self.latest

    async def close(self):
        if self.ws:
            try:
                await self.call('Browser.close', {})
            except Exception:
                pass
            await self.ws.close()
            if self.reader:
                await self.reader
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                await asyncio.to_thread(self.process.wait, 5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if hasattr(self, 'log'):
            self.log.close()
