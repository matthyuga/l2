"""Package the original generated illustration for the native UE2 loading control."""
from pathlib import Path
import subprocess,shutil,json,hashlib,struct,zlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
editor=ROOT/'research/amber-l2/tools/l2editor/L2Editor'
classes=editor.parent/'L2EpicLoadingV1/Classes';classes.mkdir(parents=True,exist_ok=True)
source='class A_LoadingAsset extends Actor;\n'
source+='#exec TEXTURE IMPORT NAME=LoadingBackground01 GROUP=Skins FILE="'+(D/'loading-square-v1.tga').as_posix()+'" MIPS=OFF\n'
source+='defaultproperties\n{\n}\n'
(classes/'A_LoadingAsset.uc').write_text(source,encoding='ascii')
ini=(editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=L2EpicLoadingV1\n'
(editor/'L2EpicLoadingV1.ini').write_text(ini,encoding='latin1')
compiled=editor/'L2EpicLoadingV1.u'
assert not compiled.exists(),'Staged package already exists; review it before rebuilding.'
r=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=L2EpicLoadingV1.ini'],cwd=editor,capture_output=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
(D/'compile.log').write_bytes(r.stdout+r.stderr)
assert r.returncode==0 and compiled.exists(),r.stdout[-1500:]+r.stderr[-1500:]
shutil.copy2(compiled,D/'L2EpicLoadingV1.raw')
package=D/'L2EpicLoadingV1-e.utx';codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
r=subprocess.run([str(codec),'-c','encode','-p','121','-f',package.name,'-o',str(package),str(compiled)],capture_output=True,input=b'\n',timeout=30)
assert r.returncode==0,r.stdout+r.stderr
data=package.read_bytes();raw=compiled.read_bytes();key=sum(package.name.lower().encode('ascii'))&255
assert data[:28].decode('utf-16le')=='Lineage2Ver121'
assert bytes(b^key for b in data[28:-20])==raw
assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
(D/'package-proof.json').write_text(json.dumps(dict(filename=package.name,reference='L2EpicLoadingV1-e.Skins.LoadingBackground01',wrapper='Lineage2Ver121',roundtrip=True,crc32=True,sha256=hashlib.sha256(data).hexdigest()),indent=2))
print('PASS: native loading package compiled, filename-bound wrapper and checksum verified.')
