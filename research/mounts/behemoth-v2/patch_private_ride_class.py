"""Redirect the stock native riding class ONLY inside the dedicated test profile."""
import pathlib,sys,struct,hashlib,json,shutil
R=pathlib.Path(__file__).resolve().parent;LAB=R.parents[2]
sys.path.insert(0,str(LAB/'research/dust2-animation-study/native'))
from inspect_package import Package,Reader
from write_l2_animation import ci
source=LAB.parent/'l2/system-hud/LineageMonster.u';target=R/'LineageMonster-native-ride.u';installed=R/'client-lab/system/LineageMonster.u'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mainhash=sha(source)
backup=R/'LineageMonster-before-native-ride.u'
if not backup.exists():shutil.copy2(installed,backup)
p=Package(source);data=bytearray(p.d);names=list(p.names);imports=list(p.imports)
def nr(name):
 if name not in names:names.append(name)
 return names.index(name)
imports.append(dict(cls_pkg=nr('Core'),cls=nr('Package'),outer=0,name=nr('BHMTransport')));pkg=-len(imports)
imports.append(dict(cls_pkg=nr('Engine'),cls=nr('SkeletalMesh'),outer=pkg,name=nr('BehemothMesh')));mesh=-len(imports)
cls=next(e for e in p.exports if p.names[e['name']]=='strider'and e['cls']==0)
raw=p.d[cls['offset']:cls['offset']+cls['size']];none=ci(nr('None'));assert raw.endswith(none)
out=bytearray(raw[:-len(none)])
def prop(name,kind,value,index=0):
 return ci(nr(name))+bytes([0x50|kind|(0x80 if index else 0),len(value)])+(bytes([index]) if index else b'')+value
out+=prop('Mesh',5,ci(mesh))
for key,value in {'WaitAnimName':'atkwait','AtkWaitAnimName':'atkwait','WalkAnimName':'Walk','RunAnimName':'run','DeathAnimName':'death','DeathWaitAnimName':'deathwait'}.items():
 for index in range(8):out+=prop(key,6,ci(nr(value)),index)
out+=prop('CollisionHeight',4,struct.pack('<f',54))+prop('CollisionRadius',4,struct.pack('<f',63))+none
classoff=len(data);data+=out
nameoff=len(data);r=Reader(p.d,struct.unpack_from('<I',p.d,16)[0])
for _ in p.names:r.string();r.u()
start=struct.unpack_from('<I',p.d,16)[0];data+=p.d[start:r.p]
for name in names[len(p.names):]:v=name.encode()+b'\0';data+=ci(len(v))+v+struct.pack('<I',0x70010)
importoff=len(data)
for i in imports:data+=ci(i['cls_pkg'])+ci(i['cls'])+struct.pack('<i',i['outer'])+ci(i['name'])
exportoff=len(data)
for e in p.exports:
 size,offset=(len(out),classoff)if e is cls else(e['size'],e['offset'])
 data+=ci(e['cls'])+ci(e['super'])+struct.pack('<i',e['outer'])+ci(e['name'])+struct.pack('<I',e['flags'])+ci(size)+(ci(offset)if size else b'')
struct.pack_into('<6I',data,12,len(names),nameoff,len(p.exports),exportoff,len(imports),importoff)
target.write_bytes(data);check=Package(target);changed=[]
for before,after in zip(p.exports,check.exports):
 a=p.d[before['offset']:before['offset']+before['size']];b=check.d[after['offset']:after['offset']+after['size']]
 if a!=b:changed.append(p.names[before['name']])
assert changed==['strider']
assert check.obj(mesh)=='BHMTransport.BehemothMesh'
assert sha(source)==mainhash
report={'scope':'dedicated client-lab only; all native strider rides in this profile use Behemoth','mainClientUnchanged':True,'mainSHA256':mainhash,'stagedSHA256':sha(target),'mountPackageSHA256':sha(R/'BHMTransport.u'),'modifiedExports':changed,'allOtherExportsByteIdentical':True,'class':'LineageMonster.strider','mesh':'BHMTransport.BehemothMesh','bone':'Bone15 (real reference bone)','animationSlotsPerState':8,'collisionHeight':54,'collisionRadius':63,'nativeClientVisualVerified':False,'installed':False}
report['installed']=sha(installed)==sha(target) and sha(R/'client-lab/system/BHMTransport.u')==report['mountPackageSHA256']
if not report['installed']:report['installationPending']='Close L2 and use Open-NativeBehemoth.ps1 to install both verified packages together.'
(R/'native-ride-class-patch.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
