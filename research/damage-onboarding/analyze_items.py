"""Read-only extraction of client item labels, not a remote shop inventory."""
from pathlib import Path
import csv
import hashlib
import json
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent / 'items'
ROOT = Path('E:/l2-damage')
sys.path.insert(0, 'E:/l2-local/research/airships')
from read_map import Reader

SCHEMA = Path('E:/l2-local/research/amber-l2/tools/L2ClientDat/dist/data/structure/dats/itemname.xml')
FIELDS = list(next(x for x in ET.parse(SCHEMA).getroot() if x.get('pattern') == 'Interlude').find('for'))

def parse(path):
    data = path.read_bytes()
    r = Reader(data)
    count = r.num('I')
    assert 0 < count < 100000, count
    rows = []
    for _ in range(count):
        row = {}
        for field in FIELDS:
            kind = field.get('reader')
            if kind == 'UNICODE':
                size = r.num('i')
                assert 0 <= size <= 1000000 and size % 2 == 0, (r.p, size)
                value = r.read(size).decode('utf-16le').rstrip('\0')
            elif kind == 'ASCF':
                size = r.compact()
                assert abs(size) < 1000000
                raw = r.read(abs(size) * (2 if size < 0 else 1))
                value = raw.decode('utf-16le' if size < 0 else 'cp1252', errors='replace').rstrip('\0')
            else:
                value = r.num({'UINT': 'I', 'INT': 'i', 'UBYTE': 'B'}[kind])
            row[field.get('name')] = value
        rows.append(row)
    trailing = data[r.p:]
    assert trailing == b'\x0cSafePackage\x00' or (not trailing.strip(b'\0') and len(trailing) <= 4), (r.p, len(data), trailing[:20])
    return rows, {'rows': count, 'bytes': len(data), 'consumed': r.p, 'trailing_hex': trailing.hex()}

def write_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inventories, manifest = {}, {}
    for label, source in {
        'damage': ROOT / 'client/Lineage II/system/itemname-e.dat',
        'baseline': ROOT / 'analysis/baseline-interlude/Lineage II/system/itemname-e.dat',
    }.items():
        dest = OUT / (label + '-itemname-e.decoded.dat')
        subprocess.run(['E:/l2-local/tools/node-v24.22.0-win-x64/node.exe',
                        str(ROOT / 'analysis/decode413.cjs'), str(source), str(dest)], check=True, capture_output=True)
        rows, stats = parse(dest)
        inventories[label] = rows
        manifest[label] = dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                               decoded_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(), **stats)
        write_csv(label + '-items.csv', rows)
    base = {x['id']: x for x in inventories['baseline']}
    added = [x for x in inventories['damage'] if x['id'] not in base]
    changed = [x for x in inventories['damage'] if x['id'] in base and x != base[x['id']]]
    keywords = re.compile(r'vote|donat|festival|damage coin|event coin|tattoo|noblesse|hero|blessed|crystal scroll|life stone', re.I)
    candidates = [x for x in inventories['damage'] if keywords.search(x['name'] + ' ' + x['additionalname'])]
    write_csv('added-items.csv', added)
    write_csv('changed-items.csv', changed)
    write_csv('keyword-candidates.csv', candidates)
    manifest.update(added=len(added), changed=len(changed), keyword_candidates=len(candidates),
                    scope='Client labels and advertised descriptions only. Shop membership, prices, server effects and availability are not established.')
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
    print(json.dumps(manifest, indent=2))
    print('Changed/added labels:', json.dumps([{'id': x['id'], 'name': x['name'], 'additionalname': x['additionalname']} for x in added + changed][:65]))

if __name__ == '__main__':
    main()
