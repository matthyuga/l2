"""Nexus TV local program controller. Binds only to loopback; no OBS required."""
import asyncio
import contextlib
import io
import json
import logging
import re
import secrets
import signal
import time
import os
from collections import deque
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import aiohttp
from aiohttp import web
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from channel import Channel, CAMERA, PROGRAM, WIDTH, HEIGHT, k, LEGACY_PROGRAM
import ctypes
from renderer import Renderer
from decoder import Decoder
cv2.setNumThreads(2)

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / 'media'
PORT = int(os.environ.get('NEXUS_TV_PORT', '8796'))
PROFILES = {'eco': {'width':640,'height':480,'fps':15,'label':'Ligero'}, 'balanced': {'width':960,'height':720,'fps':24,'label':'Equilibrado'}, 'hd': {'width':1280,'height':960,'fps':30,'label':'HD'}}
ORIGIN = f'http://127.0.0.1:{PORT}'
EXTENSIONS = {'.mp4', '.webm', '.m4v', '.mov', '.mkv'}
log = logging.getLogger('nexus-tv')

def youtube_id(value):
    value = value.strip()
    if re.fullmatch(r'[A-Za-z0-9_-]{11}', value):
        return value
    parsed = urlparse(value)
    host = (parsed.hostname or '').lower()
    if host in {'youtu.be', 'www.youtu.be'}:
        candidate = parsed.path.strip('/').split('/')[0]
    elif host in {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'www.youtube-nocookie.com'}:
        candidate = parse_qs(parsed.query).get('v', [''])[0]
        if not candidate and parsed.path.startswith(('/embed/', '/shorts/', '/live/')):
            candidate = parsed.path.split('/')[2]
    else:
        raise ValueError('Usá un enlace de YouTube o su ID de 11 caracteres.')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', candidate):
        raise ValueError('No se pudo identificar el video de YouTube.')
    return candidate

def placeholder(title, detail):
    image = Image.new('RGB', (512, 384), '#101c2a')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('C:/Windows/Fonts/tahomabd.ttf', 29)
    small = ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf', 17)
    draw.rounded_rectangle((18, 24, 494, 360), radius=16, outline='#307d95', width=2)
    draw.text((256, 115), 'NEXUS TV', anchor='mm', fill='#83d8ed', font=font)
    draw.text((256, 184), title, anchor='mm', fill='white', font=small)
    draw.text((256, 225), detail, anchor='mm', fill='#b0c0cd', font=small)
    return cv2.cvtColor(cv2.resize(np.asarray(image), (WIDTH, HEIGHT)), cv2.COLOR_RGB2BGRA).tobytes()

class Program:
    def __init__(self):
        self.instance = k.CreateMutexW(None, False, 'Local\\NexusGiranTV_Controller_' + str(PORT))
        if not self.instance or ctypes.get_last_error() == 183:
            if self.instance:
                k.CloseHandle(self.instance)
            raise RuntimeError('El control de Nexus TV ya está abierto.')
        self.token = secrets.token_urlsafe(32)
        self.output = Channel(PROGRAM, write=True)
        if not self.output.ptr:
            raise RuntimeError('No se pudo crear la salida de video local.')
        self.legacy_output = Channel(LEGACY_PROGRAM, write=True, legacy=True) if PORT == 8796 else None
        self.camera = None
        self.profile = 'hd'
        self.decoder = None
        self.cached_pixels = None
        self.cached_camera_id = -1
        self.cached_browser_id = -1
        self.emission_times = deque(maxlen=240)
        self.content_times = deque(maxlen=240)
        self.cost_times = deque(maxlen=120)
        self.legacy_at = 0
        self.preview_at = 0
        self.source = 'camera'
        self.selected = None
        self.position = -1
        self.queue = []
        self.loop = False
        self.volume = 30
        self.error = ''
        self.ready = False
        self.started = time.perf_counter()
        self.frames = 0
        self.camera_age = None
        self.preview = b''
        self.player_status = {}
        self.player_updated_at = time.perf_counter()
        self.control_lock = asyncio.Lock()
        self.stop = asyncio.Event()
        self.renderer = None
        self.task = None
        self.waiting = placeholder('Esperando a NexusCam', 'Mantené la ventana de cámara visible')
        self.off_frame = placeholder('Emisión apagada', 'Elegí una fuente en el control')
        config = ROOT / 'playlist.json'
        if config.exists():
            try:
                data = json.loads(config.read_text(encoding='utf8'))
                self.queue = [x for x in data.get('queue', []) if x.get('type') in {'local', 'youtube'}]
                self.volume = int(data.get('volume', 30))
                self.loop = bool(data.get('loop', False))
                self.profile = data.get('profile', 'hd') if data.get('profile', 'hd') in PROFILES else 'hd'
            except (ValueError, TypeError):
                log.warning('Lista anterior ilegible; se inicia vacía.')

    def save(self):
        target = ROOT / 'playlist.json'
        temp = target.with_suffix('.tmp')
        temp.write_text(json.dumps(dict(queue=self.queue, volume=self.volume, loop=self.loop, profile=self.profile), ensure_ascii=False, indent=2), encoding='utf8')
        temp.replace(target)

    def local_file(self, name):
        path = (MEDIA / str(name)).resolve()
        if path.parent != MEDIA.resolve() or path.suffix.lower() not in EXTENSIONS or not path.is_file():
            raise ValueError('Archivo no disponible en la biblioteca local.')
        return path

    async def start(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        self.renderer = Renderer(ROOT, ORIGIN, self.session)
        self.task = asyncio.create_task(self.frames_loop())
        try:
            await self.renderer.start()
            await self.renderer.command('volume', self.volume)
            await self.renderer.command('loop', self.loop)
            await self.renderer.configure(PROFILES[self.profile]['width'], PROFILES[self.profile]['height'])
            self.ready = True
        except Exception as error:
            self.error = str(error)
            log.exception('Reproductor no disponible')

    async def restart_decoder(self, position=None):
        old, self.decoder = self.decoder, None
        if old:
            await old.close()
        if self.source == 'local' and self.selected:
            quality = PROFILES[self.profile]
            position = self.player_status.get('position', 0) if position is None else position
            decoder = Decoder(self.local_file(self.selected['value']), quality['width'], quality['height'], quality['fps'], position, self.loop)
            await decoder.start()
            self.decoder = decoder
        self.cached_pixels = None

    async def frames_loop(self):
        last_status = 0
        while True:
            start = time.perf_counter()
            changed = False
            try:
                pixels = self.off_frame
                if self.source == 'camera':
                    if not self.camera or not self.camera.ptr:
                        if self.camera:
                            self.camera.close()
                        self.camera = Channel(CAMERA, legacy=True)
                    camera, age = self.camera.read()
                    self.camera_age = age
                    if camera and age < 3000:
                        if self.cached_pixels is None or self.cached_camera_id != self.camera.sequence:
                            image = np.frombuffer(camera,np.uint8).reshape((384,512,4))
                            self.cached_pixels = cv2.resize(image,(WIDTH,HEIGHT),interpolation=cv2.INTER_LINEAR).tobytes()
                            self.cached_camera_id = self.camera.sequence
                            changed = True
                        pixels = self.cached_pixels
                    else:
                        pixels = self.waiting
                elif self.source in {'local', 'youtube'} and self.ready:
                    if self.source == 'local' and self.decoder:
                        decoder = self.decoder
                        paused=self.player_status.get('paused',False)
                        playhead=self.player_status.get('position',0)+(0 if paused else max(0,start-self.player_updated_at))
                        duration=self.player_status.get('duration',0)
                        if self.loop and duration:playhead%=duration
                        raw, changed = await decoder.frame(paused,playhead)
                        if raw:
                            if (decoder.width, decoder.height) == (WIDTH,HEIGHT):
                                self.cached_pixels = raw
                            else:
                                image = np.frombuffer(raw,np.uint8).reshape((decoder.height,decoder.width,4))
                                self.cached_pixels = cv2.resize(image,(WIDTH,HEIGHT),interpolation=cv2.INTER_LINEAR).tobytes()
                    elif self.source == 'youtube':
                        jpeg = await self.renderer.frame()
                        if self.cached_browser_id != self.renderer.frame_id or self.cached_pixels is None:
                            image = cv2.imdecode(np.frombuffer(jpeg,np.uint8),cv2.IMREAD_COLOR)
                            if image is None:
                                raise RuntimeError('Imagen de reproductor no v?lida')
                            if image.shape[:2] != (HEIGHT,WIDTH):
                                image = cv2.resize(image,(WIDTH,HEIGHT),interpolation=cv2.INTER_LINEAR)
                            self.cached_pixels = cv2.cvtColor(image,cv2.COLOR_BGR2BGRA).tobytes()
                            self.cached_browser_id = self.renderer.frame_id
                            changed = True
                    pixels = self.cached_pixels or self.off_frame
                    if start - last_status > .5:
                        self.player_status = await self.renderer.evaluate('window.tv.status()')
                        self.player_updated_at = time.perf_counter()
                        last_status = start
                        if self.player_status.get('ended'):
                            if self.loop and self.source == 'youtube':
                                await self.renderer.command('seek',0)
                                await self.renderer.command('play')
                            elif not self.loop and len(self.queue)>1:
                                await self.advance(1)
                self.output.publish(pixels)
                now = time.perf_counter()
                self.emission_times.append(now)
                if changed:
                    self.content_times.append(now)
                self.frames += 1
                if now-self.preview_at >= .4 or (self.legacy_output and now-self.legacy_at>=.1):
                    image = np.frombuffer(pixels,np.uint8).reshape((HEIGHT,WIDTH,4))
                    small = cv2.resize(image,(512,384),interpolation=cv2.INTER_AREA)
                    if self.legacy_output and now-self.legacy_at>=.1:
                        self.legacy_output.publish(small.tobytes())
                        self.legacy_at = now
                    if now-self.preview_at>=.4:
                        ok,data = cv2.imencode('.jpg',small[:,:,:3],[cv2.IMWRITE_JPEG_QUALITY,80])
                        if ok:
                            self.preview=data.tobytes()
                        self.preview_at=now
                self.cost_times.append((time.perf_counter()-start)*1000)
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.error=str(error)
                log.warning('Emisi?n: %s',error)
                self.output.publish(placeholder('Error de reproducci?n','Revis? el control de Nexus TV'))
                await asyncio.sleep(.3)
            fps=PROFILES[self.profile]['fps']
            await asyncio.sleep(max(.001,1/fps-(time.perf_counter()-start)))

    async def select(self, item):
        if not self.ready:
            raise ValueError('El reproductor todavía no está disponible. ' + self.error)
        await self.renderer.set_stream(item['type']=='youtube')
        if item['type'] == 'local':
            path = self.local_file(item['value'])
            from urllib.parse import quote
            await self.renderer.command('local', ORIGIN + '/media/' + quote(path.name))
        else:
            await self.renderer.command('youtube', youtube_id(item['value']))
        self.emission_times.clear(); self.content_times.clear(); self.cost_times.clear()
        self.selected = item
        self.source = item['type']
        self.error = ''
        self.player_status = await self.renderer.evaluate('window.tv.status()')
        self.player_updated_at = time.perf_counter()
        self.cached_pixels = None
        self.cached_browser_id = -1
        await self.restart_decoder()

    async def advance(self, direction):
        if not self.queue:
            raise ValueError('La lista está vacía.')
        index = (self.position + direction) % len(self.queue)
        await self.select(self.queue[index])
        self.position = index

    async def action(self, data):
        async with self.control_lock:
            name = data.get('action')
            if name in {'camera', 'off'}:
                if self.ready:
                    await self.renderer.command('pause')
                    await self.renderer.set_stream(False)
                self.source, self.selected, self.error = name, None, ''
                await self.restart_decoder()
            elif name == 'quality':
                profile = data.get('value')
                if profile not in PROFILES:
                    raise ValueError('Perfil no v?lido')
                if not self.ready:
                    raise ValueError('El reproductor a?n no est? listo')
                self.profile = profile
                self.emission_times.clear(); self.content_times.clear(); self.cost_times.clear()
                await self.renderer.configure(PROFILES[profile]['width'], PROFILES[profile]['height'])
                self.player_status = await self.renderer.evaluate('window.tv.status()')
                self.player_updated_at = time.perf_counter()
                self.cached_pixels = None
                self.cached_browser_id = -1
                await self.restart_decoder()
                self.save()
            elif name == 'load':
                kind = data.get('type')
                value = str(data.get('value', ''))
                if kind == 'youtube':
                    value = youtube_id(value)
                elif kind == 'local':
                    value = self.local_file(value).name
                else:
                    raise ValueError('Fuente no válida.')
                item = dict(type=kind, value=value, label=str(data.get('label') or value)[:120])
                if item not in self.queue:
                    self.queue.append(item)
                    self.save()
                if data.get('play', True):
                    await self.select(item)
                    self.position = self.queue.index(item)
            elif name == 'select':
                index = int(data['index'])
                if not 0 <= index < len(self.queue):
                    raise ValueError('Elemento no válido.')
                await self.select(self.queue[index])
                self.position = index
            elif name in {'next', 'previous'}:
                await self.advance(1 if name == 'next' else -1)
            elif name in {'play', 'pause', 'seek', 'volume', 'loop'}:
                if not self.ready:
                    raise ValueError('El reproductor no está disponible.')
                if name in {'play', 'pause', 'seek'} and self.source not in {'local', 'youtube'}:
                    raise ValueError('Primero elegí un video local o YouTube.')
                value = data.get('value')
                if name == 'volume':
                    value = self.volume = max(0, min(100, int(value)))
                elif name == 'loop':
                    value = self.loop = bool(value)
                elif name == 'seek':
                    value = max(0, float(value))
                self.player_status = await self.renderer.command(name, value)
                self.player_updated_at = time.perf_counter()
                if self.source == 'local' and name in {'seek','loop'}:
                    await self.restart_decoder(value if name == 'seek' else None)
                self.save()
            elif name == 'remove':
                index = int(data['index'])
                if not 0 <= index < len(self.queue):
                    raise ValueError('Elemento no válido.')
                self.queue.pop(index)
                if self.position == index:
                    self.position = -1
                elif self.position > index:
                    self.position -= 1
                self.save()
            elif name == 'shutdown':
                self.stop.set()
            else:
                raise ValueError('Acción no válida.')

    def status(self):
        now=time.perf_counter()
        emission=[t for t in self.emission_times if now-t<4]
        content=[t for t in self.content_times if now-t<4]
        emission_fps=(len(emission)-1)/(emission[-1]-emission[0]) if len(emission)>1 else 0
        content_fps=(len(content)-1)/(content[-1]-content[0]) if len(content)>1 else 0
        return dict(profile=self.profile, profiles=PROFILES, canvas=[WIDTH,HEIGHT], emission_fps=round(emission_fps,1), content_fps=round(content_fps,1), process_ms=round(sum(self.cost_times)/len(self.cost_times),2) if self.cost_times else 0, decoder='direct' if self.source=='local' else 'browser-stream' if self.source=='youtube' else 'camera-legacy', source=self.source, selected=self.selected, queue=self.queue, index=self.position,
                    ready=self.ready, error=self.error or self.player_status.get('error', ''),
                    player=self.player_status, volume=self.volume, loop=self.loop,
                    camera_age_ms=self.camera_age, frames=self.frames,
                    uptime=round(time.perf_counter() - self.started, 1),
                    media=[p.name for p in sorted(MEDIA.iterdir()) if p.is_file() and p.suffix.lower() in EXTENSIONS],
                    program_channel=PROGRAM, audio='local-browser', version=2)

    async def close(self):
        if self.task:
            self.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.task
        if self.decoder:
            await self.decoder.close()
        if self.renderer:
            await self.renderer.close()
        if hasattr(self, 'session'):
            await self.session.close()
        self.output.close()
        if self.legacy_output:
            self.legacy_output.close()
        if self.camera:
            self.camera.close()
        if self.instance:
            k.CloseHandle(self.instance)
            self.instance = None

@web.middleware
async def errors(request, handler):
    try:
        # Refuse DNS rebinding and cross-origin control requests.
        if request.host not in {f'127.0.0.1:{PORT}', f'localhost:{PORT}'}:
            raise web.HTTPForbidden(text='Host no permitido')
        if request.method != 'GET':
            if request.headers.get('X-Nexus-Token') != request.app['program'].token:
                raise web.HTTPForbidden(text='Control no autorizado')
            if request.headers.get('Origin', ORIGIN) not in {ORIGIN, f'http://localhost:{PORT}'}:
                raise web.HTTPForbidden(text='Origen no permitido')
        return await handler(request)
    except (ValueError, KeyError, TypeError) as error:
        return web.json_response(dict(error=str(error)), status=400)
    except web.HTTPException:
        raise
    except Exception as error:
        log.exception('Solicitud fallida')
        return web.json_response(dict(error=str(error)), status=500)

async def index(request):
    text = (ROOT / 'public/index.html').read_text(encoding='utf8')
    return web.Response(text=text.replace('__TOKEN__', request.app['program'].token), content_type='text/html', headers={'Cache-Control': 'no-store'})

async def status(request):
    return web.json_response(request.app['program'].status(), headers={'Cache-Control': 'no-store'})

async def action(request):
    data = await request.json()
    await request.app['program'].action(data)
    return web.json_response(request.app['program'].status())

async def preview(request):
    return web.Response(body=request.app['program'].preview, content_type='image/jpeg', headers={'Cache-Control': 'no-store'})

async def media(request):
    return web.FileResponse(request.app['program'].local_file(request.match_info['name']))

async def upload(request):
    reader = await request.multipart()
    count = 0
    while field := await reader.next():
        if not field.filename:
            continue
        name = Path(field.filename.replace('\\', '/')).name
        name = re.sub(r'[^\w. ()-]', '_', name)[:140]
        if Path(name).suffix.lower() not in EXTENSIONS:
            raise ValueError('Elegí un archivo de video MP4, WebM, MOV, M4V o MKV.')
        target = MEDIA / name
        if target.exists():
            raise ValueError('Ya existe un archivo con ese nombre.')
        temp = MEDIA / ('.upload-' + secrets.token_hex(8))
        size = 0
        try:
            with temp.open('xb') as stream:
                while chunk := await field.read_chunk(1024 * 256):
                    size += len(chunk)
                    if size > 4 * 1024**3:
                        raise ValueError('El archivo supera los 4 GB. Copialo directamente a la carpeta media.')
                    stream.write(chunk)
            temp.replace(target)
            count += 1
        finally:
            if temp.exists():
                temp.unlink()
    return web.json_response(dict(imported=count))

async def main():
    (ROOT / 'run').mkdir(exist_ok=True)
    MEDIA.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.FileHandler(ROOT / 'run/controller.log', encoding='utf8')])
    program = Program()
    app = web.Application(middlewares=[errors], client_max_size=4 * 1024**3)
    app['program'] = program
    app.add_routes([web.get('/', index), web.get('/api/status', status), web.post('/api/action', action),
                    web.post('/api/upload', upload), web.get('/preview.jpg', preview), web.get('/media/{name}', media),
                    web.get('/player.html', lambda _: web.FileResponse(ROOT / 'public/player.html'))])
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    try:
        await web.TCPSite(runner, '127.0.0.1', PORT).start()
        (ROOT / 'run/controller.pid').write_text(str(__import__('os').getpid()))
        await program.start()
        await program.stop.wait()
        await asyncio.sleep(.2)
    finally:
        await program.close()
        await runner.cleanup()

class MediaLoop(asyncio.ProactorEventLoop):
    def __init__(self):
        super().__init__()
        self._clock_resolution = time.get_clock_info('perf_counter').resolution

    def time(self):
        return time.perf_counter()

class MediaPolicy(asyncio.WindowsProactorEventLoopPolicy):
    def new_event_loop(self):
        return MediaLoop()

if __name__ == '__main__':
    asyncio.set_event_loop_policy(MediaPolicy())
    ctypes.WinDLL('winmm').timeBeginPeriod(1)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        ctypes.WinDLL("winmm").timeEndPeriod(1)
