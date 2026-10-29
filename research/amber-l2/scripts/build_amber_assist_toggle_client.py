"""Append Amber's native toggle to the CURRENT client, preserving every previous row byte."""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
from contract_dat import Catalog

PROJECT = pathlib.Path(__file__).resolve().parents[3]
CLIENT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT.parent / 'l2/system-hud'
OUT = PROJECT / 'research/amber-l2/exports/contract/assist-toggle'
CODEC = PROJECT / 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
OUT.mkdir(parents=True, exist_ok=True)
report = {'skill_id': 19014, 'client': str(CLIENT), 'files': {}}

def codec(*args):
    subprocess.run([str(CODEC), *map(str, args)], check=True, capture_output=True)

for name, schema in [('skillgrp', 'skillgrp.xml'), ('skillname-e', 'skillname.xml')]:
    original = CLIENT / (name + '.dat')
    current = OUT / ('current-' + name + '.raw')
    codec('-o', current, original)
    cat = Catalog(current, schema, 'ScionsOfDestiny')
    assert not any(row['skill_id'] == 19014 for row in cat.rows), 'Toggle ID already exists; inspect before editing.'
    row = copy.deepcopy(next(row for row in cat.rows if row['skill_id'] == 337 and row['skill_level'] == 1))
    if name == 'skillgrp':
        assert row['operate_type'] == 3, 'Unexpected native toggle encoding.'
        row.update(skill_id=19014, skill_level=1, mp_consume=0, hp_consume=0,
                   hit_time=0.1, cast_range=4294967295, is_magic=2, animation='',
                   description='', icon='icon.skill0337', extra_eff=0, is_enchanted=0,
                   enchant_skill_id=0, rumble_self=4294967295, rumble_target=4294967295)
    else:
        row.update(skill_id=19014, skill_level=1, name='Asistencia de Amber',
                   desc='Activable: un clic activa la asistencia IA de Amber y otro la desactiva. Requiere Amber invocada y contrato vigente. Sin coste de MP. Seguir o Detener la apagan. No cancela una lluvia ya iniciada.',
                   enchant_name='', enchant_desc='')
    raw = OUT / (name + '.raw')
    cat.append([row], raw)
    encoded = OUT / (name + '.dat')
    codec('-c', 'encode', '-p', '413', '-o', encoded, raw)
    roundtrip = OUT / (name + '-roundtrip.raw')
    codec('-o', roundtrip, encoded)
    assert roundtrip.read_bytes() == raw.read_bytes(), 'Protocol 413 roundtrip mismatch.'
    verified = Catalog(roundtrip, schema, 'ScionsOfDestiny')
    assert verified.count == cat.count + 1
    assert verified.data[4:cat.end] == cat.data[4:cat.end], 'An existing row changed.'
    assert len([r for r in verified.rows if r['skill_id'] == 19014]) == 1
    report['files'][name] = {'original_count': cat.count, 'new_count': verified.count,
                             'existing_rows_byte_identical': True, 'roundtrip': 'PASS',
                             'original_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
                             'output_sha256': hashlib.sha256(encoded.read_bytes()).hexdigest()}

(OUT / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
