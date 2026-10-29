from pathlib import Path
import json,hashlib,struct,subprocess,datetime,shutil
D=Path(__file__).resolve().parent;P=D.parents[3];old=D.parent/'integration';sha=lambda b:hashlib.sha256(b).hexdigest();codec=P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';items=[]
assert not (D/'installation.json').exists()
assert not subprocess.check_output(['powershell','-NoProfile','-Command',"if(Get-Process L2 -ErrorAction SilentlyContinue){'OPEN'}"],text=True).strip(),'Client still open'
assert json.loads((D/'native-test-results.json').read_text())['passed']==2179
prior=json.loads((old/'installation.json').read_text());guard={x['target']:x['after_sha256'] for x in prior['files']}
def add(target,data):
 assert sha(target.read_bytes())==guard[str(target)],('Baseline changed',target)
 items.append((target,data))
for profile in ['system-hud','system-camera-online']:
 client=Path('E:/l2')/profile
 for name in ['engine.dll','NWindow.dll']:add(client/name,(D/'stage'/name).read_bytes())
 # Reuse two pre-existing empty localized entries; no sparse high IDs.
 raw=(old/(profile+'.strings.raw')).read_bytes();count=struct.unpack_from('<I',raw)[0];offset=4;out=bytearray(raw[:4]);changed=[]
 for i in range(count):
  start=offset;id=struct.unpack_from('<I',raw,offset)[0];offset+=4
  first=raw[offset];offset+=1;length=first&63;shift=6;more=first&64
  while more:
   v=raw[offset];offset+=1;length|=(v&127)<<shift;shift+=7;more=v&128
  offset+=length*(2 if first&128 else 1)
  if id in [2133,2134]:
   assert length==0,(id,length)
   text=('Nuevo '+str(id-2132)).encode('ascii')+b'\0';out+=struct.pack('<I',id)+bytes([len(text)])+text;changed.append(id)
  else:out+=raw[start:offset]
 assert changed==[2133,2134];out+=raw[offset:]
 output=D/'stage'/profile;output.mkdir(exist_ok=True);src=output/'sysstring.raw';src.write_bytes(out);dat=output/'sysstring-e.dat'
 subprocess.run([str(codec),'-c','encode','-p','413','-o',str(dat),str(src)],capture_output=True,check=True)
 check=output/'check.raw';subprocess.run([str(codec),'-o',str(check),str(dat)],capture_output=True,check=True);assert check.read_bytes()==out
 add(client/'sysstring-e.dat',dat.read_bytes())
backup=P/'backups'/('hair-fix-v2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True);m=dict(backup=str(backup),files=[],visual_verified=False)
for i,(target,data) in enumerate(items):
 saved=backup/(str(i)+'-'+target.name);shutil.copy2(target,saved)
 m['files'].append(dict(target=str(target),backup=str(saved),before_sha256=sha(target.read_bytes()),after_sha256=sha(data)))
 (D/'installation.json').write_text(json.dumps(m,indent=2));(backup/'manifest.json').write_text(json.dumps(m,indent=2));target.write_bytes(data);assert sha(target.read_bytes())==sha(data)
print('INSTALLED hair correction in both profiles; backup:',backup)
