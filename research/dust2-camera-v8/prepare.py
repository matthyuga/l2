from pathlib import Path
import sys,json,hashlib,math,subprocess,struct,zlib
D=Path(__file__).resolve().parent;R=D.parents[1];V7=D.parent/'dust2-camera-v7';C=R.parent/'l2'
sys.path.insert(0,str(R/'research/gludio-sky'))
from package_tools import Edit,change_props
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=C/'Maps/24_19.unr';m=Edit(source)
assert sha(source)==json.loads((V7/'installation.json').read_text())['files'][0]['after_sha256']
grid={}
for x,y,z,h,c in json.loads((V7/'camera-ceilings.json').read_text()):grid.setdefault((x,y),[]).append(h)
audit={b['name']:b for b in json.loads((V7/'bounds-audit.json').read_text()) if b['camera_only_zero_extent']}
enabled=[];excluded=[];walls_preserved=[]
for e in m.exports:
 if e['name'] not in audit:continue
 if 'CameraWall' in e['name']:
  walls_preserved.append(e['name']);continue
 b=audit[e['name']];lo,hi=b['min'],b['max'];conflict=False
 # Leave low ceilings/joins unchanged if their swept surface could intersect a
 # standing character at another nearby walkable level (9u radius, 88u envelope).
 # Walls already follow V4 closed geodata edges, with the same footprint.
 if 'CameraWall' not in e['name']:
  for x in range(math.floor((lo[0]-9-131072)/16),math.floor((hi[0]+9-131072)/16)+1):
   for y in range(math.floor((lo[1]-9-32768)/16),math.floor((hi[1]+9-32768)/16)+1):
    if not (lo[0]-9<131072+x*16+8<hi[0]+9 and lo[1]-9<32768+y*16+8<hi[1]+9):continue
    for h in grid.get((x,y),[]):
     if lo[2]<h+88 and hi[2]>h+2:conflict=True
 if conflict:excluded.append(e['name']);continue
 m.replace(e,change_props(m,e,{'bBlockNonZeroExtentTraces':m.boolean('bBlockNonZeroExtentTraces',True)}));enabled.append(e['name'])
out=m.save(D/'stage/Maps/24_19.unr');new=Edit(out);old=Edit(source);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name'] in enabled:
  pa=old.props(a);pb=new.props(b);assert pa.pop('bBlockNonZeroExtentTraces') is False;assert pb.pop('bBlockNonZeroExtentTraces') is True;assert pa==pb
 else:
  assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([str(R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(out)],capture_output=True,check=True)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255
assert b[28:-20].translate(bytes(v^key for v in range(256)))==out.read_bytes()
assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
reload=Edit(encoded)
assert all(reload.props(e)['bBlockNonZeroExtentTraces'] for e in reload.exports if e['name'] in enabled)
report=dict(version='camera-v8',enabled=enabled,excluded_low_clearance=excluded,enabled_count=len(enabled),excluded_count=len(excluded),camera_walls_preserved=len(walls_preserved),other_payloads_preserved=preserved,source_sha256=sha(source),staged_sha256=sha(encoded),ramps_and_geodata_unchanged=True,client_camera_test_pending=True)
(D/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},indent=2))
