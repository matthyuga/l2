import pathlib
import subprocess

ROOT=pathlib.Path(__file__).resolve().parents[1]
editor=ROOT / 'tools/l2editor/L2Editor'
package=editor.parent / 'L2AmberNPC'
(package/'Classes').mkdir(parents=True,exist_ok=True)
source=f'''class AmberActor extends Actor;
#exec MESH MODELIMPORT MESH=AmberNPC MODELFILE="{(ROOT/'exports/AmberNPC.psk').as_posix()}" LODSTYLE=0 LODSPECIFY=1
#exec MESH LODMODEL MESH=AmberNPC LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=4 COHERENCE=1
#exec MESHMAP SCALE MESHMAP=AmberNPC X=1 Y=1 Z=1
#exec TEXTURE IMPORT NAME=AmberBody FILE="{(ROOT/'exports/textures/AmberBody.tga').as_posix()}" MIPS=ON MASKED=1
#exec TEXTURE IMPORT NAME=AmberOutfit FILE="{(ROOT/'exports/textures/AmberOutfit.tga').as_posix()}" MIPS=ON MASKED=1
#exec MESHMAP SETTEXTURE MESHMAP=AmberNPC NUM=0 TEXTURE=AmberBody
#exec MESHMAP SETTEXTURE MESHMAP=AmberNPC NUM=1 TEXTURE=AmberOutfit
defaultproperties
{{
    DrawType=DT_Mesh
    Mesh=SkeletalMesh'L2AmberNPC.AmberNPC'
    bUnlit=False
}}
'''
(package/'Classes/AmberActor.uc').write_text(source,encoding='ascii')
config=(editor/'UT2003.ini').read_text(encoding='latin1')
config=config.replace('Paths=.\\*.u','Paths=.\\*.u\nPaths=E:/l2/system-hud/*.u\nPaths=E:/l2/sounds/*.uax\nPaths=E:/l2/animations/*.ukx\nPaths=E:/l2/systextures/*.utx')
config+='\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=L2AmberNPC\n'
(editor/'AmberNPC.ini').write_text(config,encoding='latin1')
compiled=editor/'L2AmberNPC.u'
if compiled.exists(): compiled.unlink()  # Regenerate this laboratory's package only.
with (ROOT/'reports/amber-ucc-make.log').open('w') as log:
    result=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=AmberNPC.ini'],cwd=editor,stdout=log,stderr=subprocess.STDOUT,timeout=300)
print('UCC exit',result.returncode)
print((ROOT/'reports/amber-ucc-make.log').read_text(errors='replace')[-3000:])
assert result.returncode==0 and compiled.exists()
