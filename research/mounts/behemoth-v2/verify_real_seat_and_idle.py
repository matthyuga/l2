import pathlib,sys,struct,json
R=pathlib.Path(__file__).resolve().parent;LAB=R.parents[2]
sys.path.insert(0,str(LAB/'research/dust2-animation-study/native'))
from inspect_package import Package,Reader
from write_l2_animation import chunks
source=chunks(R/'BehemothTwoRiders.psk');native=chunks(R/'BehemothTwoRiders-native-3mat.psk');roundtrip=chunks(R/'real-seat-roundtrip/BHMTransport/SkeletalMesh/BehemothMesh.psk')
names=lambda c:[c[2][i*c[0]:i*c[0]+64].rstrip(b'\0').decode() for i in range(c[1])]
before=names(source['REFSKELT']);after=names(roundtrip['REFSKELT'])
assert len(after)==99 and set(after)==set(before)|{'Bone15'}
seat_index=after.index('Bone15');roundtrip_parent=struct.unpack_from('<i',roundtrip['REFSKELT'][2],seat_index*120+72)[0];assert after[roundtrip_parent]=='Bip01 Spine1'
native_names=names(native['REFSKELT']);assert native_names[:98]==before and native_names[98]=='Bone15'
parent=before.index('Bip01 Spine1')
assert native['PNTS0000']==source['PNTS0000'] and native['RAWWEIGHTS']==source['RAWWEIGHTS']
for i in range(98):
 a=bytearray(source['REFSKELT'][2][i*120:(i+1)*120]);b=bytearray(native['REFSKELT'][2][i*120:(i+1)*120])
 if i==parent:struct.pack_into('<i',a,68,struct.unpack_from('<i',a,68)[0]+1)
 assert a==b
p=Package(R/'LineageMonster-native-ride.u');original=Package(LAB.parent/'l2/system-hud/LineageMonster.u');get=lambda p:next(e for e in p.exports if p.names[e['name']]=='strider'and e['cls']==0)
e=get(p);raw=p.d[e['offset']:e['offset']+e['size']];reader=Reader(raw,get(original)['size']-1);arrays={};props={}
while True:
 name=p.names[reader.ci()]
 if name=='None':break
 flag=raw[reader.p];reader.p+=1;assert ((flag>>4)&7)==5
 size=raw[reader.p];reader.p+=1;index=0
 if flag&128:index=raw[reader.p];reader.p+=1
 end=reader.p+size
 if flag&15==5:value=p.obj(reader.ci())
 elif flag&15==6:value=p.names[reader.ci()];arrays.setdefault(name,{})[index]=value
 elif flag&15==4:value=struct.unpack_from('<f',raw,reader.p)[0];reader.p+=4
 else:raise AssertionError(flag)
 props[name]=value;assert reader.p==end
assert reader.p==len(raw) and props['Mesh']=='BHMTransport.BehemothMesh'
for name,clip in {'WaitAnimName':'atkwait','AtkWaitAnimName':'atkwait','WalkAnimName':'Walk','RunAnimName':'run','DeathAnimName':'death','DeathWaitAnimName':'deathwait'}.items():
 assert arrays[name]=={i:clip for i in range(8)}
report={'passed':True,'realSeatBone':{'name':'Bone15','sourceIndex':98,'roundtripIndex':seat_index,'parent':'Bip01 Spine1'},'original98BoneRecordsPreservedExceptParentChildCount':True,'pointsAndWeightsUnchanged':True,'nativeRoundtripBones':99,'animationTables':arrays,'nativeGameVisualVerified':False}
(R/'real-seat-idle-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('PASS: real Bone15 in native roundtrip, geometry/weights preserved, all 48 animation slots configured.')
