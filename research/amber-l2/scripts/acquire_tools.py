import hashlib
import json
import pathlib
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'tools'
DEST.mkdir(exist_ok=True)

def download(url, name):
    target = DEST / name
    if not target.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'Amber-L2-Lab/1.0'})
        with urllib.request.urlopen(request, timeout=60) as response:
            target.write_bytes(response.read())
    data = target.read_bytes()
    item = {'name': name, 'source': url, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    print(json.dumps(item), flush=True)
    return target, item

manifest = []
binary, record = download('https://raw.githubusercontent.com/gildor2/UModel/master/umodel.exe', 'umodel.exe')
manifest.append(record)
request = urllib.request.Request('https://api.github.com/repos/DarklightGames/io_scene_psk_psa/releases/tags/5.0.6', headers={'User-Agent': 'Amber-L2-Lab/1.0'})
release = json.load(urllib.request.urlopen(request, timeout=60))
for asset in release['assets']:
    if asset['name'].endswith('.zip'):
        archive, record = download(asset['browser_download_url'], asset['name'])
        manifest.append(record)
        with zipfile.ZipFile(archive) as z:
            z.extractall(DEST / 'psk_addon')
        break
(ROOT / 'reports' / 'tool-sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
