from pathlib import Path
from PIL import Image
import subprocess
root=Path(__file__).resolve().parents[1];editor=root/'tools/l2editor/L2Editor'
stage=root/'exports/contract/combat-vfx-v5';stage.mkdir(parents=True,exist_ok=True)
source=root/'assets/external/kenney-particle-pack/source/PNG (Black background)/fire_02.png'
image=Image.open(source).convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
path=stage/'KenneyFire.tga';image.save(path)
pkg=editor.parent/'AmberFireTexturesV1/Classes';pkg.mkdir(parents=True,exist_ok=True)
(pkg/'A_FireAssets.uc').write_text(f'''class A_FireAssets extends Emitter;
#exec TEXTURE IMPORT NAME=KenneyFire FILE="{path.as_posix()}" MIPS=OFF
defaultproperties
{{
    Begin Object Class=SpriteEmitter Name=Keeper
        Texture=Texture'AmberFireTexturesV1.KenneyFire'
    End Object
    Emitters(0)=SpriteEmitter'Keeper'
}}
''')
(editor/'AmberFireTexturesV1.ini').write_text((editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberFireTexturesV1\n',encoding='latin1')
out=editor/'AmberFireTexturesV1.u'
if out.exists():out.unlink()
r=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=AmberFireTexturesV1.ini'],cwd=editor,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
(root/'reports/amber-fire-textures-build.log').write_bytes(r.stdout+r.stderr)
assert r.returncode==0 and out.exists()
(stage/'AmberFireTexturesV1.u').write_bytes(out.read_bytes())
print('PASS: Kenney fire_02 CC0 texture adapted to 64x64 and compiled into client particle texture package.')
