"""Append Amber to the client name catalog, preserving all existing records."""
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
data = (ROOT / 'exports/npcname.raw').read_bytes()
offset = 4

def compact_read():
    global offset
    b = data[offset]; offset += 1
    negative, value, more = b & 0x80, b & 0x3f, b & 0x40
    shift = 6
    while more:
        b = data[offset]; offset += 1
        value |= (b & 0x7f) << shift
        more = b & 0x80
        shift += 7
    return -value if negative else value

def string_read():
    global offset
    length = compact_read()
    size = length if length >= 0 else -2 * length
    assert 0 <= size <= 1000000
    raw = data[offset:offset + size]
    assert len(raw) == size
    offset += size
    return raw.decode('cp1252' if length >= 0 else 'utf-16-le').rstrip('\0')

count, = struct.unpack_from('<I', data)
ids = []
for _ in range(count):
    npc_id, = struct.unpack_from('<I', data, offset); offset += 4
    ids.append(npc_id)
    string_read(); string_read()
    offset += 4  # RGBA title color
assert 59001 not in ids
end = offset

def ascii_string(text):
    raw = text.encode('ascii') + b'\0'
    assert len(raw) < 64
    return bytes([len(raw)]) + raw

row = struct.pack('<I', 59001) + ascii_string('Amber') + ascii_string('Prueba Koikatsu') + bytes.fromhex('9ce8a9ff')
patched = struct.pack('<I', count + 1) + data[4:end] + row + data[end:]
assert patched[4:end] == data[4:end]
(ROOT / 'exports/npcname-amber.raw').write_bytes(patched)
report = {'original_rows': count, 'added_id': 59001, 'original_rows_preserved': True,
          'trailing_bytes': len(data) - end, 'original_bytes': len(data), 'patched_bytes': len(patched)}
(ROOT / 'reports/npcname-validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report))
