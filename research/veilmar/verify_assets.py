"""Check source archive, actor coverage and all referenced preview resources."""
import hashlib, json, pathlib, urllib.parse
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / 'research/veilmar'
CAT = ROOT / 'research/model-catalog'
archive = ROOT / 'descarga de assets/Veilmar Fortress, Sanctuary of the Dawn Monarch.rar'
expected = 'de305fda099ad9bb2e97fb832e278e192b78d78e2f98bd91412e5455525da688'
with archive.open('rb') as stream:
    digest = hashlib.sha256(stream.read()).hexdigest()
assert digest == expected and archive.stat().st_size == 99735612
models = json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))['models']
actors = json.loads((D/'actors.json').read_text())
mesh_refs = json.loads((D/'scene-meshes.json').read_text())
assert len(actors) == 1407 and len(mesh_refs) == 233
assert {a['StaticMesh'] for a in actors} == set(mesh_refs)
seen = set()
results = []
for key in ('veilmar_surface', 'veilmar_underground'):
    m = next(m for m in models if m['key'] == key)
    scene = CAT/m['gltf']
    gltf = json.loads(scene.read_text())
    refs = [r['uri'] for kind in ('buffers', 'images') for r in gltf.get(kind, []) if 'uri' in r]
    for ref in refs:
        if not ref.startswith('data:'):
            path = scene.parent/urllib.parse.unquote(ref)
            assert path.is_file() and path.stat().st_size > 0, path
    with Image.open(CAT/m['thumbnail']) as image:
        image.verify()
    audit = json.loads((D/(key+'-assembly-audit.json')).read_text())
    assert not audit['missing'] and not seen.intersection(audit['actors'])
    seen.update(audit['actors'])
    results.append(dict(key=key, actors=len(audit['actors']), dependencies=len(refs), resources='pass'))
assert seen == {a['actor'] for a in actors}
qa = json.loads((ROOT/'research/airships/new-structures-verification.json').read_text())
webgl = [r for r in qa['webgl'] if r['key'] in {r['key'] for r in results}]
assert len(webgl) == 2 and all(r['webgl'] == 'pass' for r in webgl)
report = dict(archive=str(archive), sha256=digest, size=archive.stat().st_size,
              archive_files=[str(p.relative_to(D/'assets')) for p in (D/'assets').rglob('*') if p.is_file()],
              static_meshes=233, actors=1407, scenes=results, webgl=webgl,
              installed_in_game=(D/'installation.json').exists() and not (D/'restored.txt').exists(), geodata_included=False)
(D/'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
