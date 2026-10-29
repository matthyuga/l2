from pathlib import Path
from PIL import Image
import subprocess
R=Path(r'E:\l2-local\research\dust2-animation-study\npc');E=Path(r'E:\l2-local\research\amber-l2\tools\l2editor\L2Editor')
C=E.parent/'Dust2DemoNPC/Classes';C.mkdir(parents=True,exist_ok=True)
Image.new('RGB',(32,32),(90,148,185)).save(R/'DemoClay.tga')
s=f'''class DemoActor extends Actor;
#exec MESH MODELIMPORT MESH=DemoMesh MODELFILE="{(R/'Dust2Demo.psk').as_posix()}" LODSTYLE=0 LODSPECIFY=1
#exec MESH LODMODEL MESH=DemoMesh LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=4 COHERENCE=1
#exec MESHMAP SCALE MESHMAP=DemoMesh X=1 Y=1 Z=1
#exec TEXTURE IMPORT NAME=DemoClay FILE="{(R/'DemoClay.tga').as_posix()}" MIPS=ON
#exec MESHMAP SETTEXTURE MESHMAP=DemoMesh NUM=0 TEXTURE=DemoClay
'''
(C/'DemoActor.uc').write_text(s)
ini=(E/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=Dust2DemoNPC\n'
(E/'Dust2DemoNPC.ini').write_text(ini,encoding='latin1')
p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini=Dust2DemoNPC.ini'],cwd=E,capture_output=True,text=True,timeout=120)
(R/'ucc-build.log').write_text(p.stdout+p.stderr);print(p.returncode,(p.stdout+p.stderr)[-1800:]);assert p.returncode==0
