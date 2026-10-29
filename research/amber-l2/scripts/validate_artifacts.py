import collections
import hashlib
import json
import math
import pathlib
import struct

ROOT=pathlib.Path(__file__).resolve().parents[1]
def psk(path):
    data=path.read_bytes()
    chunks={}
    position=0
    while position<len(data):
        name,kind,size,count=struct.unpack_from('<20siii',data,position)
        position+=32
        assert count>=0 and size>=0
        end=position+size*count
        assert end<=len(data)
        chunks[name.split(b'\0')[0].decode()]=(size,count,data[position:end])
        position=end
    assert position==len(data)
    return chunks
source=psk(ROOT/'exports/AmberNPC.psk')
roundtrip=psk(ROOT/'exports/installed-check/L2AmberNPCv4/SkeletalMesh/AmberNPC.psk')
def bones(chunks):
    size,count,data=chunks['REFSKELT']
    assert size==120
    return [data[i*size:i*size+64].split(b'\0')[0].decode('cp1252') for i in range(count)]
assert bones(source)==bones(roundtrip)
assert len(bones(source))==76
def points(chunks):
    size,count,data=chunks['PNTS0000']
    assert size==12
    values=list(struct.iter_unpack('<fff',data))
    assert all(math.isfinite(x) for point in values for x in point)
    return values
source_points=points(source)
roundtrip_points=points(roundtrip)
grid=collections.defaultdict(list)
cell=0.01
for point in roundtrip_points:
    grid[tuple(math.floor(x/cell) for x in point)].append(point)
maximum_position_error=0
welded_points=0
for point in source_points:
    key=tuple(math.floor(x/cell) for x in point)
    candidates=[candidate for dx in (-1,0,1) for dy in (-1,0,1) for dz in (-1,0,1)
                for candidate in grid[(key[0]+dx,key[1]+dy,key[2]+dz)]]
    assert candidates, ('Mesh vertex has no nearby native counterpart', point)
    error=min(math.dist(point,candidate) for candidate in candidates)
    maximum_position_error=max(maximum_position_error,error)
    welded_points+=int(error>0.00001)
print('Native welding:',len(source_points),len(roundtrip_points),welded_points,maximum_position_error)
assert welded_points<=len(source_points)-len(roundtrip_points), ('Unexpected geometry changes',welded_points)
assert maximum_position_error<0.01, ('Native vertex weld exceeds 0.01 game units',maximum_position_error)
assert source['FACE0000'][1]==roundtrip['FACE0000'][1]
assert source['MATT0000'][1]==roundtrip['MATT0000'][1]==2
size,count,data=source['RAWWEIGHTS']
assert size==12
sums=collections.defaultdict(float)
influence_counts=collections.Counter()
for weight,point,bone in struct.iter_unpack('<fii',data):
    assert math.isfinite(weight) and 0<=weight<=1.00001
    assert 0<=point<source['PNTS0000'][1] and 0<=bone<76
    sums[point]+=weight
    influence_counts[point]+=1
assert len(sums)==source['PNTS0000'][1]
max_error=max(abs(x-1) for x in sums.values())
assert max_error<0.001
# Decimation interpolates source groups; UCC reduces them to four at compilation.
native_sums=collections.defaultdict(float)
native_counts=collections.Counter()
for weight,point,bone in struct.iter_unpack('<fii',roundtrip['RAWWEIGHTS'][2]):
    assert math.isfinite(weight) and 0<=weight<=1.00001
    assert 0<=point<roundtrip['PNTS0000'][1] and 0<=bone<76
    native_sums[point]+=weight
    native_counts[point]+=1
assert len(native_sums)==roundtrip['PNTS0000'][1]
assert max(native_counts.values())<=4
native_weight_error=max(abs(value-1) for value in native_sums.values())
assert native_weight_error<0.001
original=(ROOT/'exports/npcgrp.raw').read_bytes()
patched=(ROOT/'exports/npcgrp-amber-verified.raw').read_bytes()
plain=(ROOT/'exports/npcgrp-amber.raw').read_bytes()
assert patched==plain
original_report=json.loads((ROOT/'reports/npcgrp-parsed.json').read_text(encoding='utf8'))
patched_report=json.loads((ROOT/'reports/npcgrp-amber-parsed.json').read_text(encoding='utf8'))
end=original_report['parsed_bytes']
assert patched[4:end]==original[4:end]
assert patched[-13:]==original[-13:]
assert patched_report['count']==original_report['count']+1
assert patched_report['rows'][-1]['npc_id']==59001
assert patched_report['rows'][-1]['class_name']=='LineageNPC.a_traderB_FHuman'
assert patched_report['rows'][-1]['mesh_name']=='L2AmberNPCv4.AmberNPC'
assert (ROOT/'exports/npcname-amber.raw').read_bytes()==(ROOT/'exports/npcname-amber-verified.raw').read_bytes()
files=['E:/l2/animations/L2AmberNPCv4.ukx','E:/l2/animations/L2AmberMotionv3.ukx',
       'E:/l2/system-amber/npcgrp.dat','E:/l2/system-amber/NpcName-e.dat',
       'E:/l2-local/server/game/data/stats/npcs/custom/amber_lab.xml']
report={'mesh_roundtrip':True,'vertices':source['PNTS0000'][1], 'triangles':source['FACE0000'][1],
        'bones':76,'materials':2,'maximum_skin_weight_error':max_error,'maximum_position_error':maximum_position_error,
        'maximum_native_skin_weight_error':native_weight_error,'maximum_native_influences':max(native_counts.values()),
        'native_welded_points':welded_points,
        'npcgrp_roundtrip':True,'original_rows_preserved':original_report['count'],'added_client_id':59001,
        'client_npc_class':'LineageNPC.a_traderB_FHuman','npcname_roundtrip':True,
        'visual_revision':4,'previous_in_game_result':'User screenshot: v3 geometry improved, outfit and hair too dark compared with self-illuminated face; v4 awaits restart',
        'installed_files':[{'path':p,'bytes':pathlib.Path(p).stat().st_size,
                            'sha256':hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()} for p in files],
        'in_game_visual_validation':False}
(ROOT/'reports/validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='installed_files'},indent=2))
