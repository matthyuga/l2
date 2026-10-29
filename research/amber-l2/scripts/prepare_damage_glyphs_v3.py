from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import subprocess
root=Path(__file__).resolve().parents[1];editor=root/'tools/l2editor/L2Editor'
pkg=editor.parent/'DamageGlyphsV3/Classes';pkg.mkdir(parents=True,exist_ok=True)
stage=root/'exports/contract/combat-vfx-v9';stage.mkdir(parents=True,exist_ok=True)
assets=stage/'glyphs';assets.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',50)
colors=[(255,190,100),(255,80,80),(255,130,180),(255,70,140)]
imports=[]
for color,rgb in enumerate(colors):
 for digit in range(10):
  name=f'Glyph{color}_{digit}'
  im=Image.new('RGBA',(64,64),(0,0,0,0));d=ImageDraw.Draw(im)
  bounds=d.textbbox((0,0),str(digit),font=font,stroke_width=2)
  d.text(((64-(bounds[2]-bounds[0]))/2-bounds[0],(64-(bounds[3]-bounds[1]))/2-bounds[1]),str(digit),font=font,fill=rgb+(255,),stroke_width=2,stroke_fill=(0,0,0,255))
  path=assets/(name+'.tga');ImageOps.flip(im).save(path)
  imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{path.as_posix()}" MIPS=OFF')
(pkg/'A_DamageBase.uc').write_text('''class A_DamageBase extends Emitter;
'''+ '\n'.join(imports)+'''
simulated function Tick(float DeltaTime)
{
    local PlayerController PC;
    local Rotator View;
    foreach DynamicActors(class'PlayerController',PC)
    {
        if(PC.Player!=None)
        {
            View=PC.Rotation;
            View.Pitch=0;
            View.Roll=0;
            SetRotation(View);
            break;
        }
    }
}
defaultproperties
{
    AutoDestroy=True
    bNoDelete=False
    bHidden=False
    bDirectional=False
    LifeSpan=1.45
}
''')
for color in range(4):
 for slot in range(10):
  for digit in range(10):
   name=f'Dmg_{color}_{slot}_{digit}_Fx'
   (pkg/(name+'.uc')).write_text(f'''class {name} extends A_DamageBase;
defaultproperties
{{
    Begin Object Class=SpriteEmitter Name=Glyph
        Texture=Texture'DamageGlyphsV3.Glyph{color}_{digit}'
        DrawStyle=PTDS_AlphaBlend
        CoordinateSystem=PTCS_Relative
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=10000.0
        MaxParticles=1
        RespawnDeadParticles=False
        SecondsBeforeInactive=0.0
        StartLocationRange=(Y=(Min={-slot*(16 if color%2 else 13)},Max={-slot*(16 if color%2 else 13)}),Z=(Min=0,Max=0))
        StartVelocityRange=(Z=(Min=16,Max=16))
        StartSizeRange=(X=(Min=9,Max=9),Y=(Min=12,Max=12),Z=(Min=1,Max=1))
        FadeOut=True
        FadeOutStartTime=0.50
        FadeIn=True
        FadeInEndTime=0.06
        UseSizeScale=True
        SizeScale(0)=(RelativeTime=0.0,RelativeSize=0.65)
        SizeScale(1)=(RelativeTime=0.12,RelativeSize={1.65 if color%2 else 1.22})
        SizeScale(2)=(RelativeTime=0.30,RelativeSize=0.96)
        SizeScale(3)=(RelativeTime=0.44,RelativeSize=1.0)
        SizeScale(4)=(RelativeTime=1.0,RelativeSize=0.82)
        LifetimeRange=(Min=1.3,Max=1.3)
    End Object
    Emitters(0)=SpriteEmitter'Glyph'
}}
''')
ini=(editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=DamageGlyphsV3\n'
(editor/'DamageGlyphsV3.ini').write_text(ini,encoding='latin1')
out=editor/'DamageGlyphsV3.u'
if out.exists():out.unlink()
result=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=DamageGlyphsV3.ini'],cwd=editor,capture_output=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
(root/'reports/damage-glyphs-v3-build.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0 and out.exists(),result.stdout[-3000:]
print('PASS: 400 glyph classes compiled; four colors, ten columns, all decimal digits. Native ForcedMaxParticles will be patched separately.')
