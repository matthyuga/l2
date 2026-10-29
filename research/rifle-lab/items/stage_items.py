"""Append rifle prototype catalogs to staging. No installation or live writes.

Input JSON: {"items":[{"id":32580,"name":"M4A1 - Prototipo",
"mesh":"HGRifleM4A1.M4A1","textures":["HGRifleM4A1.RifleTex00"],
"icon":"icon.weapon_short_bow_i00"}]}
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from catalog_weapon import Catalog

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
CODEC = PROJECT / 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--client-system', type=Path, default=PROJECT / 'research/dust2-animation-study/client-lab/system')
    parser.add_argument('--server-items', type=Path, default=PROJECT / 'server/game/data/stats/items')
    parser.add_argument('--output', type=Path, default=ROOT / 'stage')
    args = parser.parse_args()
    out = args.output.resolve()
    # Every generated file must stay within this task's owned staging directory.
    assert out.is_relative_to(ROOT), 'Output must be under rifle-lab/items'
    assert args.client_system.resolve() != out
    out.mkdir(parents=True, exist_ok=True)
    items = json.loads(args.assets.read_text(encoding='utf-8-sig'))['items']
    ids = [x['id'] for x in items]
    assert ids and len(ids) == len(set(ids))
    assert all(isinstance(x, int) and 0 < x < 32767 for x in ids)
    for item in items:
        assert item['mesh'].startswith('HGRifle') and '.' in item['mesh']
        assert item['textures'] and all(x.startswith('HGRifle') and '.' in x for x in item['textures'])
        assert all(x not in item['name'] for x in '\r\n\0')
    templates = {}
    for path in args.server_items.rglob('*.xml'):
        for item in ET.parse(path).getroot().findall('item'):
            iid = int(item.get('id'))
            if iid not in templates or path.parent.name != 'custom':
                templates[iid] = item
    assert not set(ids) & templates.keys(), 'IDs already in server templates'
    baseline = templates[13]
    assert baseline.find("set[@name='weapon_type']").get('val') == 'BOW'
    server_root = ET.Element('list', {'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
                                    'xsi:noNamespaceSchemaLocation':'../../xsd/items.xsd'})
    for spec in items:
        item = copy.deepcopy(baseline)
        item.set('id', str(spec['id']))
        item.set('name', spec['name'])
        settings = {'icon':spec.get('icon', 'icon.weapon_short_bow_i00'), 'price':'0',
                    'is_tradable':'false', 'is_dropable':'false', 'is_sellable':'false'}
        for name, value in settings.items():
            node = item.find(f"set[@name='{name}']")
            if node is None:
                node = ET.Element('set', {'name':name})
                item.insert(list(item).index(item.find('stats')), node)
            node.set('val', value)
        server_root.append(item)
    ET.indent(server_root, space='\t')
    server_file = out / '32580-rifle-prototypes.xml'
    ET.ElementTree(server_root).write(server_file, encoding='utf-8', xml_declaration=True)
    manifest = {'items':items, 'baseline_id':13, 'type':'BOW', 'server_xml':str(server_file),
                'server_xml_sha256':sha(server_file), 'installed':False, 'catalogs':{},
                'limitations':['Bow mechanics, ammunition, projectile and animation remain unchanged.',
                               'No rifle combat, custom bullet or automatic fire implemented.',
                               'Model orientation and grip require in-game verification.']}
    for name, schema, key in [('weapongrp','weapongrp.xml','object_id'), ('itemname-e','itemname.xml','id')]:
        source = args.client_system / (name + '.dat')
        before = out / (name + '.before.raw')
        run([CODEC, '-o', before, source])
        cat = Catalog(before, schema, 'Interlude')
        assert not set(ids) & {x[key] for x in cat.rows}, 'IDs already in client catalog'
        base = next(x for x in cat.rows if x[key] == 13)
        assert cat.encode(base) == cat.data[base['_start']:base['_end']], 'Baseline codec mismatch'
        additions = []
        for spec in items:
            row = copy.deepcopy(base)
            row[key] = spec['id']
            if name == 'weapongrp':
                row.update(drop_mesh1=spec['mesh'], drop_mesh2='', drop_mesh3='',
                           drop_tex1=spec['textures'][0], drop_tex2='', drop_tex3='',
                           icon1=spec.get('icon', 'icon.weapon_short_bow_i00'), wp_mesh=1,
                           mesh_0__items=[{'mesh0':spec['mesh']}], texture=len(spec['textures']),
                           texture_items=[{'texture0':x} for x in spec['textures']], curvature=0,
                           rangeA='', junk2A1=1.0, junk2A2=1.0, junk2A3=1.0,
                           junk2A4=0.0, junk2A5=0.0, junk2A6=0.0)
            else:
                row.update(name=spec['name'], additionalname='Laboratorio',
                           description='Prototipo visual de rifle. Usa mecanica de arco; disparos propios pendientes.')
            additions.append(row)
        raw = out / (name + '.raw')
        cat.append(additions, raw)
        check = Catalog(raw, schema, 'Interlude')
        assert check.count == cat.count + len(items)
        assert check.data[4:cat.end] == cat.data[4:cat.end]
        assert check.data[check.end:] == cat.data[cat.end:], 'Original catalog footer changed'
        assert [x[key] for x in check.rows[-len(items):]] == ids
        dat = out / (name + '.dat')
        run([CODEC, '-c', 'encode', '-p', '413', '-o', dat, raw])
        roundtrip = out / (name + '.roundtrip.raw')
        run([CODEC, '-o', roundtrip, dat])
        assert raw.read_bytes() == roundtrip.read_bytes()
        manifest['catalogs'][name] = {'input':str(source), 'input_sha256':sha(source),
                                    'output':str(dat), 'output_sha256':sha(dat),
                                    'old_records_preserved':cat.count, 'added':len(items),
                                    'old_record_bytes_preserved':True, 'roundtrip_verified':True}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
