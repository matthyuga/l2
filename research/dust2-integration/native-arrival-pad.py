"""Two stock-client arrival supports; isolate imported collision from client/map placement."""
import pathlib,sys,struct,json,hashlib,subprocess,shutil,datetime,zlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];CLIENT=ROOT.parent/'l2';OUT=D/'native-arrival';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert not subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-Process l2 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id;exit 0"],text=True).strip(),'Close client before changing map'
m=Edit(CLIENT/'Maps/24_19.unr');assert not any(e['name'].startswith('HGDust2NativeArrival') for e in m.exports)
before=sha(CLIENT/'Maps/24_19.unr');levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');newrefs=[]
geo=json.loads((D/'geodata-audit.json').read_text());placements=[]
for group in ['ct','t']:
 x,y,z=geo['spawns'][group][0];floor=z-24-43.35;loc=[x,y,floor-9.937800407409668*.5]
 mesh=m.imp('L2fortress_02_s.Fort02_medic_base');raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',loc)+m.vector('ColLocation',loc)+m.float('DrawScale',.5)
 for n in ['bDynamicActorFilterState','bIgnoredRange','bSunAffect','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']:raw+=m.boolean(n,True)
 raw+=m.boolean('bUseCylinderCollision',False)+m.nametag('Tag','StaticMeshActor')+m.end();cl=m.imp('Engine.StaticMeshActor','Core.Class');frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 newrefs.append(m.add('HGDust2NativeArrival'+group.upper(),'Engine.StaticMeshActor',frame+raw,flags=0x2070001));placements.append(dict(group=group,location=loc,scale=.5,native_surface_at_center=floor))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;count=r.num('i');assert r.num('i')==count;refs=[r.compact() for _ in range(count)];end=r.p
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',count+2,count+2)+b''.join(ci(i) for i in refs+newrefs)+m.b[end:level['offset']+level['size']]);raw=m.save(OUT/'stage/Maps/24_19.unr')
encoded=OUT/'24_19.unr';subprocess.run([str(ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(raw)],capture_output=True,check=True,timeout=30)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(x^key for x in range(256)))==raw.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
old=Edit(CLIENT/'Maps/24_19.unr');new=Edit(raw)
for a,c in zip(old.exports,new.exports):
 if a['name']=='myLevel':continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[c['offset']:c['offset']+c['size']]
backup=ROOT/'backups'/('dust2-native-arrivals-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);shutil.copy2(CLIENT/'Maps/24_19.unr',backup/'24_19.unr');assert sha(CLIENT/'Maps/24_19.unr')==before
shutil.copy2(encoded,CLIENT/'Maps/24_19.unr');assert sha(CLIENT/'Maps/24_19.unr')==sha(encoded)
report=dict(backup=str(backup),before_sha256=before,after_sha256=sha(encoded),placements=placements,native_mesh='L2fortress_02_s.Fort02_medic_base',client_verified=False,temporary_diagnostic=True)
(OUT/'installation.json').write_text(json.dumps(report,indent=2));(backup/'manifest.json').write_text(json.dumps(report,indent=2))
manifest=json.loads((D/'installation.json').read_text())
for item in manifest['files']:
 if pathlib.Path(item['target'])==CLIENT/'Maps/24_19.unr':item['after_sha256']=sha(encoded)
manifest['native_arrival_supports']=report;(D/'installation.json').write_text(json.dumps(manifest,indent=2));(pathlib.Path(manifest['backup'])/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('INSTALLED_TWO_NATIVE_ARRIVAL_SUPPORTS',json.dumps(report))
