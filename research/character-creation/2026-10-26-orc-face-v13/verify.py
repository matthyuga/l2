from pathlib import Path
import json,struct,re
from PIL import Image,ImageChops
D=Path(__file__).resolve().parent;P=Path('E:/l2-local')
scope={'__file__':str(D/'verify.py')};exec((D.parent/'2026-10-26-tanda2-v10/verify_assets.py').read_text().split('manifest=json.loads')[0],scope)
source=scope['chunks'](D/'MOrc_ModernFace.psk');mesh=D/'export-check/NexusOrcFaceV13/SkeletalMesh/MOrc_ModernFace.psk';after=scope['chunks'](mesh);error=scope['uv_tolerance'](source,after)
assert source['REFSKELT']==after['REFSKELT'];assert after['FACE0000'][1]==386
dump=(D/'mesh-dump.txt').read_text(encoding='utf8');counts=list(map(int,re.findall(r'NumFaces=(\d+)',dump)));vertices=list(map(int,re.findall(r'NumVerts = (\d+)',dump)));indices=list(map(int,re.findall(r'IndexCount = (\d+)',dump)))
assert len(counts)==4 and all(c>0 for c in counts);assert indices==[3*c for c in counts];assert all(v>0 for v in vertices);assert 'Material=None' not in dump;assert dump.count("Material=Texture'FaceDefault'")==4
a=Image.open(D/'FaceDefault.tga').convert('RGBA');b=Image.open(D/'export-check/NexusOrcFaceV13/Texture/FaceDefault.png').convert('RGBA');assert a.size==b.size and not ImageChops.difference(a,b).getbbox()
raw=(D/'native-editor-check.log').read_bytes();log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf8',errors='replace');assert 'Success - 0 error(s), 0 warning(s)' in log
s,n,data=after['MATT0000'];assert n==1;assert data[:64].split(b'\0')[0]==b'FaceDefault'
(D/'asset-test-results.json').write_text(json.dumps(dict(passed=True,points=after['PNTS0000'][1],triangles=386,uv_error=error,skeleton_exact=True,all_lod_materials_nonnull=True,lod_triangles=counts,lod_vertices=vertices,texture_exact=True,native_editor_load=True),indent=2),encoding='utf8')
print('PASS: geometry/UV/skeleton; 4 LODs with non-null FaceDefault; exact texture and native editor load.')
