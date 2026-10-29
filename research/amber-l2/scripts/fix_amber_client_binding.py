"""Stage a minimal bow-animation config and replace only the two Amber records."""
import copy, hashlib, json, pathlib, re, struct, subprocess
from contract_dat import Catalog

ROOT=pathlib.Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
CODEC=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
CLIENT=PROJECT.parent/'l2/system-hud'
OUT=ROOT/'exports/contract/motion-fix'
OUT.mkdir(parents=True,exist_ok=True)

def decode(source,dest):
    subprocess.run([str(CODEC),'-o',str(dest),str(source)],check=True,capture_output=True)
def encode(raw,dest,protocol):
    subprocess.run([str(CODEC),'-c','encode','-p',str(protocol),'-o',str(dest),str(raw)],check=True,capture_output=True)
    roundtrip=dest.with_suffix('.roundtrip.raw')
    decode(dest,roundtrip)
    assert raw.read_bytes()==roundtrip.read_bytes()
def sha(data):return hashlib.sha256(data).hexdigest()
manifest_path=ROOT/'reports/amber-motion-fix.json'
previous=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
def baseline(name,filename):
    decoded=OUT/(name+'.current.raw')
    decode(CLIENT/filename,decoded)
    data=decoded.read_bytes()
    saved=OUT/(name+'.before.raw')
    if previous:
        assert sha(data) in (previous['before'][name],previous['after'][name]), 'Integrate other client edits first'
        if sha(data)==previous['after'][name]:
            data=saved.read_bytes()
            assert sha(data)==previous['before'][name]
    saved.write_bytes(data)
    return data

original=baseline('LineageNpc','LineageNpc.int')
mapping={
    'Wait':'Wait_Hand','AtkWait':'AtkWait_Hand','Walk':'walk_hand','Run':'Run_Hand',
    'Atk01':'atk01_Hand','Atk02':'atk01_Hand','Atk03':'atk01_Hand',
    'SpAtk01':'SpAtk01_Hand','SpAtk02':'SpAtk02_Hand',
    'Death':'Death_Hand','DeathWait':'deathwait_Hand',
    'CastShort':'SpAtk01_Hand','CastMid':'SpAtk01_Hand','CastLong':'SpAtk01_Hand',
    'CastEnd':'AtkWait_Hand','MagicShot':'atk01_Hand',
    'MagicThrow':'atk01_Hand','MagicNoTarget':'atk01_Hand',
}
addition=b'\r\n'+b''.join((f'{key}AnimName[5]={value}\r\n').encode('ascii') for key,value in mapping.items())+b'\r\n'
# Match only until the next section header, not the '[' in array subscripts.
start=original.index(b'[a_traderB_FHuman]')
endmatch=re.search(rb'(?m)^\[[A-Za-z_][^\r\n]*\]',original[start+len(b'[a_traderB_FHuman]'):])
end=start+len(b'[a_traderB_FHuman]')+endmatch.start() if endmatch else len(original)
assert b'AnimName[5]' not in original[start:end]
patched=original[:end]+addition+original[end:]
(OUT/'LineageNpc.raw').write_bytes(patched)
encode(OUT/'LineageNpc.raw',OUT/'LineageNpc.int',111)
assert patched.replace(addition,b'',1)==original

baseline('npcgrp','npcgrp.dat')
catalog=Catalog(OUT/'npcgrp.before.raw','npcgrp.xml','Interlude')
parts=[struct.pack('<I',catalog.count)]
for row in catalog.rows:
    if row['npc_id'] in (59001,59002):
        new=copy.deepcopy(row)
        old='L2AmberNPCv4' if row['npc_id']==59001 else 'L2AmberArcher'
        package='L2AmberNPCv5' if row['npc_id']==59001 else 'L2AmberArcherV2'
        assert row['mesh_name']==old+'.AmberNPC'
        new['mesh_name']=package+'.AmberNPC'
        for texture in new['texture_name_items']:
            assert texture['param_texture_name'].startswith(old+'.')
            texture['param_texture_name']=texture['param_texture_name'].replace(old+'.',package+'.',1)
        parts.append(catalog.encode(new))
    else:parts.append(catalog.data[row['_start']:row['_end']])
parts.append(catalog.data[catalog.end:])
(OUT/'npcgrp.raw').write_bytes(b''.join(parts))
verified=Catalog(OUT/'npcgrp.raw','npcgrp.xml','Interlude')
assert verified.count==catalog.count
changed=[]
for old,new in zip(catalog.rows,verified.rows):
    a=catalog.data[old['_start']:old['_end']]
    b=verified.data[new['_start']:new['_end']]
    if a!=b:changed.append(old['npc_id'])
assert sorted(changed)==[59001,59002]
assert catalog.data[catalog.end:]==verified.data[verified.end:]
encode(OUT/'npcgrp.raw',OUT/'npcgrp.dat',413)
manifest={'changed_npc_records':changed,'preserved_other_records':catalog.count-2,
          'bow_animation_mapping':mapping,'mesh_origin_z':26.5,'mesh_rotation_yaw':49152,
          'before':{name:sha((OUT/(name+'.before.raw')).read_bytes()) for name in ('npcgrp','LineageNpc')},
          'after':{name:sha((OUT/(name+'.raw')).read_bytes()) for name in ('npcgrp','LineageNpc')}}
(ROOT/'reports/amber-motion-fix.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
