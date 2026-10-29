from pathlib import Path
import hashlib,json,shutil,subprocess,struct,zlib

root=Path(__file__).resolve().parents[3]
stage=Path(__file__).resolve().parent
texture=root.parent/'l2/systextures/AmberAssistIconsV1.utx'
backup=root/'backups/amber-ui-rain-2026-10-10'
name=texture.name
proof=json.loads((stage/'installed-client.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(texture)==proof[name],'Concurrent texture edit'
offline=subprocess.run(['powershell','-NoProfile','-Command',"if((Get-Process -Name L2 -ErrorAction SilentlyContinue) -or (Get-NetTCPConnection -LocalPort 7777 -State Established -ErrorAction SilentlyContinue)){exit 1}"],capture_output=True)
assert offline.returncode==0,'Close L2 before replacing its texture'
raw=texture.read_bytes()
assert raw[:4]==bytes.fromhex('c1832a9e'),'Expected the rejected raw UCC package'
rawfile=stage/'AmberAssistIconsV1.raw'
rawfile.write_bytes(raw)
encoded=stage/'encoded'/name
encoded.parent.mkdir(exist_ok=True)
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
subprocess.run([str(codec),'-c','encode','-p','121','-f',name,'-o',str(encoded),str(rawfile)],check=True,input=b'\n',capture_output=True,timeout=30)
b=encoded.read_bytes()
assert b[:28].decode('utf-16le')=='Lineage2Ver121'
assert len(b)==len(raw)+48
assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20]),'Texture wrapper CRC mismatch'
key=sum(name.lower().encode('ascii'))&255
assert bytes(v^key for v in b[28:-20])==raw
decoded=stage/'AmberAssistIconsV1.wrapper-roundtrip.raw'
subprocess.run([str(codec),'-c','decode','-f',name,'-o',str(decoded),str(encoded)],check=True,input=b'\n',capture_output=True,timeout=30)
assert decoded.read_bytes()==raw,'Wrapper/checksum roundtrip failed'
for n,s in proof.items():
    p=texture if n==name else root.parent/'l2/system-hud'/n
    assert sha(p)==s,'Concurrent installed client edit: '+n
shutil.copy2(texture,backup/'AmberAssistIconsV1.rejected-raw.utx')
shutil.copy2(encoded,stage/name)
shutil.copy2(encoded,texture)
proof[name]=sha(texture)
(stage/'installed-client.json').write_text(json.dumps(proof,indent=2))
report=json.loads((stage/'installed.json').read_text())
report['client']=proof
report['texture_wrapper']='Lineage2Ver121; filename key and checksum decode match raw package exactly'
report['ui_visual_review']='Awaiting client launch/playtest after texture wrapper correction'
(stage/'installed.json').write_text(json.dumps(report,indent=2))
result={'file':str(texture),'raw_sha256':sha(rawfile),'installed_sha256':sha(texture),'wrapper':'Lineage2Ver121','filename_key':key,'decoded_bytes':len(raw),'checksum_roundtrip':'PASS','other_installed_files_unchanged':True}
(stage/'texture-wrapper-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
