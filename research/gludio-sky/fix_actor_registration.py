"""Repair native actor frames/filter properties and externally imported cloud flags.

Reference: acmi/L2smr StaticMeshActorUtil.createActor/addStaticMeshActor, and
the actor export/state-frame layout of the original Coliseum map.
No server/player data is changed here.
"""
from package_tools import *
import json,hashlib,subprocess,shutil,datetime
D=pathlib.Path(__file__).resolve().parent;CLIENT=ROOT.parent/'l2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id; exit 0"],text=True).strip(),'Client must be closed'
installation=json.loads((D/'installation.json').read_text());assert 'actor_registration_v2' not in installation,'Repair already installed'
entries={e['target'].lower():e for e in installation['files']};report=[]
m=Edit(CLIENT/'maps/24_19.unr')
for e in m.exports:
    if not e['name'].startswith('HGGludio'):continue
    assert not e['flags']&0x02000000
    props=m.props(e)
    raw=change_props(m,e,{'bDynamicActorFilterState':m.boolean('bDynamicActorFilterState',True),'bIgnoredRange':m.boolean('bIgnoredRange',True)})
    frame=ci(e['cl'])*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
    e['flags']|=0x02000000;m.replace(e,frame+raw)
    report.append({'actor':e['name'],'state_frame_added':True,'dynamic_filter':True,'ignore_range':True})
assert len(report)==9
mapout=m.save(D/'stage/Maps/24_19.unr')
t=Edit(CLIENT/'textures/HGGludioSky_T.utx');published=[]
for e in t.exports:
    if e['name'].startswith('AcademyCloud'):
        e['flags']=0xf0004;published.append(e['name'])
assert len(published)==6
texout=t.save(D/'stage/Textures/HGGludioSky_T.utx')
backup=ROOT/'backups'/('gludio-actor-registration-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';changes=[]
for source,rel in [(mapout,'Maps/24_19.unr'),(texout,'Textures/HGGludioSky_T.utx')]:
    target=CLIENT/rel;entry=entries[str(target).lower()];assert sha(target)==entry['after_sha256'],'Concurrent client edit: '+str(target)
    encoded=D/'client'/rel
    subprocess.run([str(codec),'-c','encode','-p','121','-f',source.name,'-o',str(encoded),str(source)],check=True,capture_output=True,timeout=60)
    raw=source.read_bytes();enc=encoded.read_bytes();key=sum(map(ord,source.name.lower()))&255
    import zlib
    assert enc[28:-20].translate(bytes(x^key for x in range(256)))==raw and struct.unpack_from('<I',enc,len(enc)-8)[0]==zlib.crc32(enc[:-20])
    saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
    changes.append({'target':str(target),'backup':str(saved),'before_sha256':sha(target),'after_sha256':sha(encoded)})
for change in changes:
    target=pathlib.Path(change['target']);rel=target.relative_to(CLIENT);shutil.copy2(D/'client'/rel,target)
    entries[str(target).lower()]['after_sha256']=sha(target)
installation['actor_registration_v2']={'backup':str(backup),'changes':changes,'actors':report,'cloud_exports_public':published,'visual_verified':False}
data=json.dumps(installation,indent=2);(D/'installation.json').write_text(data);(pathlib.Path(installation['backup'])/'manifest.json').write_text(data)
(backup/'manifest.json').write_text(json.dumps(installation['actor_registration_v2'],indent=2));(D/'actor-registration-v2.json').write_text(json.dumps(installation['actor_registration_v2'],indent=2))
print('Repaired 9 native actor state frames/filter flags and published 6 cloud material exports. Backup:',backup)
