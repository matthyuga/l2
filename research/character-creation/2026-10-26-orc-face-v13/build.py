from pathlib import Path
import subprocess,json,re,struct,hashlib,zlib,shutil
from PIL import Image
P=Path('E:/l2-local');D=Path(__file__).resolve().parent;OLD=D.parent/'2026-10-26-appearance-v12';EDITOR=P/'research/amber-l2/tools/l2editor/L2Editor';PACKAGE='NexusOrcFaceV13'
for n in ['stage','raw','native-editor-check']:(D/n).mkdir(exist_ok=True)
shutil.copy2(OLD/'MOrc_ModernFace.psk',D/'MOrc_ModernFace.psk')
src=EDITOR.parent/PACKAGE/'Classes';src.mkdir(parents=True,exist_ok=True)
image=P/'research/character-creation/2026-10-23/downloads/donor-inspection/exports/LineageFaceTex/Texture/MOrc_m001_t03_f.tga';assert image.exists();shutil.copy2(image,D/'FaceDefault.tga')
text=(EDITOR.parent/'NexusOrcFaceV12/Classes/Assets.uc').read_text();text=text.replace(str(OLD.as_posix()),D.as_posix()).replace('YAW=192.0 PITCH=0.0 ROLL=0.0','YAW=192 PITCH=0 ROLL=0')
text=text.replace('defaultproperties',f'#exec TEXTURE IMPORT NAME=FaceDefault FILE="{(D/"FaceDefault.tga").as_posix()}" MIPS=ON\n#exec MESHMAP SETTEXTURE MESHMAP=MOrc_ModernFace NUM=0 TEXTURE=FaceDefault\ndefaultproperties')
(src/'Assets.uc').write_text(text,encoding='ascii')
ini=re.sub(r'(?im)^EditPackages=.*\n?','',(EDITOR/'UT2003.ini').read_text(encoding='latin1'))+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages='+PACKAGE+'\n';(EDITOR/(PACKAGE+'.ini')).write_text(ini,encoding='latin1')
compiled=EDITOR/(PACKAGE+'.u');assert not compiled.exists(),'Compilation already exists'
with (D/'ucc-build.log').open('w') as log:r=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini='+PACKAGE+'.ini'],cwd=EDITOR,stdout=log,stderr=subprocess.STDOUT,timeout=180)
assert r.returncode==0 and compiled.exists()
raw=D/'raw'/(PACKAGE+'.ukx');shutil.copy2(compiled,raw);target=D/'stage'/raw.name;codec=P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
r=subprocess.run([str(codec),'-c','encode','-p','121','-f',raw.name,'-o',str(target),str(raw)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0
check=D/'raw/roundtrip.ukx';r=subprocess.run([str(codec),'-f',raw.name,'-o',str(check),str(target)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0 and check.read_bytes()==raw.read_bytes();b=target.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
old_name='NexusOrcFaceV12.MOrc_ModernFace';new_name='NexusOrcFaceV13.MOrc_ModernFace';old_bytes=(old_name+'\0').encode('utf-16le');new_bytes=(new_name+'\0').encode('utf-16le');assert len(old_bytes)==len(new_bytes)
for folder,outname in [('stage','engine.dll'),('rollback-stage','rollback-engine.dll')]:
 before=(OLD/folder/'engine.dll').read_bytes();assert before.count(old_bytes)==1;after=before.replace(old_bytes,new_bytes);(D/'stage'/outname).write_bytes(after)
native=json.loads((OLD/'native-manifest.json').read_text());native['engine']['patched_sha256']=hashlib.sha256((D/'stage/engine.dll').read_bytes()).hexdigest();native['orc_face_mesh']=new_name;(D/'native-manifest.json').write_text(json.dumps(native,indent=2),encoding='utf8')
manifest=dict(package=PACKAGE,mesh=new_name,material=PACKAGE+'.FaceDefault',sha256=hashlib.sha256(b).hexdigest(),crc_and_roundtrip=True,geometry_source=str(OLD/'MOrc_ModernFace.psk'),previous_package_preserved=True,only_resource_path_changed_in_engine=True)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');print('BUILT v13: same head geometry, embedded FaceDefault material, new unique package and resource path.')
