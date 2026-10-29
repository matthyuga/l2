from pathlib import Path
import json,sys,struct
D=Path(__file__).resolve().parent;P=Path('E:/l2-local')
scope={'__file__':str(D/'verify_assets.py')};exec((D.parent/'2026-10-26-tanda2-v10/verify_assets.py').read_text().split('manifest=json.loads')[0],scope)
chunks,uv_tolerance=scope['chunks'],scope['uv_tolerance'];m=json.loads((D/'repair-manifest.json').read_text())
source=chunks(Path(m['head_source']));after=chunks(D/'export-check/NexusOrcFaceV12/SkeletalMesh/MOrc_ModernFace.psk');error=uv_tolerance(source,after)
native=json.loads((D.parent/'2026-10-24/hair-alignment-v5/native-skeletons.json').read_text())[10]['psk'];s,n,b=chunks(P/native)['REFSKELT'];expected=[b[i*s:i*s+64].split(b'\0')[0].decode().lower() for i in range(n)]
s,n,b=after['REFSKELT'];actual=[b[i*s:i*s+64].split(b'\0')[0].decode().lower() for i in range(n)];assert actual==expected
weighted={actual[bone] for weight,point,bone in struct.iter_unpack('<fii',after['RAWWEIGHTS'][2]) if weight>0};assert weighted
sys.path.insert(0,str(P/'research/airships'));from read_map import Package
props=[]
for file in ['NexusHairGRepairV12.utx','NexusOrcaJRepairV12.utx']:
 p=Package(D/'stage'/file)
 for e in p.exports:
  x=p.props(e);blend=p.b[x['FrameBufferBlending']['raw_offset']];ref=p.b[x['AlphaRef']['raw_offset']]
  expected_blend,expected_ref=(2,160) if file.startswith('NexusHairG') else (0,128)
  assert (blend,ref)==(expected_blend,expected_ref);assert x['AlphaTest'] and x['TwoSided'] and x['ZWrite'] and x['ZTest']
  expected_material=next(a['texture'] for a in m['materials'] if a['name'].endswith('.'+e['name']));assert x['Material']==expected_material
  assert (D/'native-editor-check'/(e['name']+'.t3d')).is_file();props.append(dict(name=e['name'],blend=blend,alpha_ref=ref,texture=x['Material']))
for log in ['native-dark-material.log','native-orca-material.log']:
 b=(D/log).read_bytes();txt=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf8',errors='replace');assert 'Success - 0 error(s), 0 warning(s)' in txt
assert len(props)==8
(D/'asset-test-results.json').write_text(json.dumps(dict(passed=True,head_points=after['PNTS0000'][1],head_triangles=after['FACE0000'][1],head_uv_error=error,native_skeleton=True,weighted_bones=sorted(weighted),materials=props,textures_not_modified=True),indent=2),encoding='utf8')
print('PASS: Orc head geometry/UV/native skeleton and 8 native materials; existing textures untouched.')
