"""Package the supplied image as native splash BMPs; preserve aspect and backup."""
from pathlib import Path
from PIL import Image, ImageOps
import datetime
import hashlib
import json
import shutil
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
CLIENT = PROJECT.parent / 'l2'
SOURCE = PROJECT / 'descarga de assets' / 'hellgames.jpg'
CODEC = PROJECT / 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
STAGE = ROOT / 'stage'
STAGE.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace'))

with Image.open(SOURCE) as source:
    source_size = source.size
    artwork = ImageOps.contain(source.convert('RGB'), (640, 480), Image.Resampling.LANCZOS)
# Native splash regions use pure black as a transparent color key. JPEG shadows
# contain black pixels throughout the scene; reserve black exclusively for padding.
artwork = artwork.point(lambda value: max(1, value))
canvas = Image.new('RGB', (640, 480), (0, 0, 0))
placement = ((640 - artwork.width) // 2, (480 - artwork.height) // 2)
canvas.paste(artwork, placement)
canvas.save(ROOT / 'preview.png')
shutil.copy2(SOURCE, ROOT / 'source-hellgames.jpg')

# The client uses the fourth BI_RGB byte as alpha for its splash window.
# Keep only padding transparent; all pixels within the artwork are opaque.
pixels = canvas.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes('raw', 'BGRX')
pixels = bytearray(pixels)
pixels[3::4] = bytes(255 if any(pixels[i:i + 3]) else 0 for i in range(0, len(pixels), 4))
assert any(pixels[3::4]), 'Artwork must not be completely transparent'
bitmap32 = struct.pack('<2sIHHI', b'BM', 54 + len(pixels), 0, 0, 54)
bitmap32 += struct.pack('<IiiHHIIiiII', 40, 640, 480, 1, 32, 0, len(pixels), 0, 0, 0, 0)
bitmap32 += pixels
raw32 = STAGE / 'splash-32.raw.bmp'
raw32.write_bytes(bitmap32)
raw256 = STAGE / 'splash-256.raw.bmp'
quantized = artwork.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
# Quantize the artwork separately so padding never merges with dark scene colors.
palette = [0, 0, 0] + quantized.getpalette()[:255 * 3]
shifted = Image.frombytes('P', artwork.size, bytes(i + 1 for i in quantized.tobytes()))
shifted.putpalette(palette)
indexed = Image.new('P', canvas.size, 0)
indexed.putpalette(palette)
indexed.paste(shifted, placement)
indexed.save(raw256)
for bitmap in (canvas, indexed.convert('RGB')):
    inner = bitmap.crop((placement[0], placement[1], placement[0] + artwork.width, placement[1] + artwork.height))
    assert all(low >= 1 for low, high in inner.getextrema()), 'Transparent color key inside image'
assert indexed.getpalette()[:3] == [0, 0, 0]
for raw, expected_bits in [(raw32, 32), (raw256, 8)]:
    with Image.open(raw) as im:
        assert im.size == (640, 480)
        im.load()
    assert struct.unpack_from('<H', raw.read_bytes(), 28)[0] == expected_bits

targets = sorted((CLIENT / 'systextures').glob('sp_*.bmp'))
assert len(targets) == 22, 'Unexpected splash inventory; inspect before changing it'
changes = []
for target in targets:
    assert target.name.startswith(('sp_32b_', 'sp_256_')), target
    raw = raw32 if target.name.startswith('sp_32b_') else raw256
    packaged = STAGE / target.name
    run([CODEC, '-c', 'encode', '-p', 121, '-f', target.name, '-o', packaged, raw])
    decoded = STAGE / (target.name + '.check')
    run([CODEC, '-f', target.name, '-o', decoded, packaged])
    assert decoded.read_bytes() == raw.read_bytes(), target
    encoded = packaged.read_bytes()
    assert encoded[:28] == 'Lineage2Ver121'.encode('utf-16le')
    assert zlib.crc32(encoded[:-20]) == struct.unpack_from('<I', encoded, len(encoded) - 8)[0]
    key = sum(target.name.lower().encode('ascii')) & 255
    translation = bytes.maketrans(bytes(range(256)), bytes(v ^ key for v in range(256)))
    assert encoded[28:28 + raw.stat().st_size].translate(translation) == raw.read_bytes()
    decoded.unlink()
    changes.append({'target': str(target), 'stage': str(packaged), 'before': sha(target), 'after': sha(packaged)})

backup = PROJECT / 'backups' / ('splash-hellgames-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir()
for change in changes:
    target = Path(change['target'])
    assert sha(target) == change['before'], 'Concurrent modification: ' + str(target)
    saved = backup / target.name
    shutil.copy2(target, saved)
    change['backup'] = str(saved)
manifest = {'status': 'prepared', 'source': str(SOURCE), 'source_sha256': sha(SOURCE),
            'source_size': source_size, 'canvas_size': [640, 480], 'artwork_size': artwork.size,
            'placement': placement, 'backup': str(backup), 'files': changes,
            'transparency': 'pure black reserved for padding; image RGB minimum 1; indexed palette 0 reserved for black',
            'verification': '22 filename-specific protocol-121 roundtrips and CRC checks; BMP dimensions and bit depths',
            'in_client_check': 'pending next user launch'}
(backup / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
written = []
try:
    for change in changes:
        assert sha(change['target']) == change['before'], 'Concurrent modification'
        shutil.copy2(change['stage'], change['target'])
        written.append(change)
    for change in changes:
        assert sha(change['target']) == change['after']
except Exception:
    for change in reversed(written):
        if sha(change['target']) == change['after']:
            shutil.copy2(change['backup'], change['target'])
    raise
manifest['status'] = 'installed'
(ROOT / 'installation.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps({'status': manifest['status'], 'files': len(changes), 'backup': str(backup),
                  'preview': str(ROOT / 'preview.png'), 'artwork_size': artwork.size, 'placement': placement}))
