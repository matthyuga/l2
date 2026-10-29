from pathlib import Path
from PIL import Image
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'reference-models/amber-web-2026-10-23';STAGE=ROOT/'exports/mmd-variants-20261023';EDITOR=ROOT/'tools/l2editor/L2Editor'
names=['FaceTex','HairTex','OutfitTex','SphereTex','ToonTex','ExpressionTex']
for label in ['v10','v14']:
 build=json.loads((STAGE/label/'build.json').read_text());report=json.loads((BASE/(label+'-analysis.json')).read_text(encoding='utf-8'));package=build['package'];classes=EDITOR.parent/package/'Classes';classes.mkdir(parents=True,exist_ok=True)
 (STAGE/label/'materials.tsv').write_text('\n'.join(m['name']+'\t'+m['texture'] for m in build['materials']),encoding='ascii')
 assets=STAGE/label/'textures';assets.mkdir(exist_ok=True)
 for name,t in zip(names,report['textures']):
  source=Path(report['path']).parent/t['name'].replace('\\','/');im=Image.open(source).convert('RGBA')
  # UE2 requires power-of-two dimensions. Main face/hair/outfit2048 stay exact.
  if any(v&(v-1) for v in im.size):im=im.resize(tuple(1<<(v-1).bit_length() for v in im.size),Image.Resampling.LANCZOS)
  im.save(assets/(name+'.tga'))
 imports='\n'.join(f'#exec TEXTURE IMPORT NAME={n} FILE="{(assets/(n+".tga")).as_posix()}" MIPS=ON MASKED=1' for n in names)
 maps='\n'.join(f'#exec MESHMAP SETTEXTURE MESHMAP=AmberNPC NUM={m["slot"]} TEXTURE={m["texture"]}' for m in build['materials'])
 text=f'''class AmberModelActor extends Actor;
#exec MESH MODELIMPORT MESH=AmberNPC MODELFILE="{(STAGE/label/'AmberNPC.psk').as_posix()}" LODSTYLE=0 LODSPECIFY=1
#exec MESH LODMODEL MESH=AmberNPC LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=4 COHERENCE=1
#exec MESHMAP SCALE MESHMAP=AmberNPC X=1 Y=1 Z=1
{imports}
{maps}
defaultproperties
{{
 DrawType=DT_Mesh
 Mesh=SkeletalMesh'{package}.AmberNPC'
 bUnlit=False
}}
'''
 (classes/'AmberModelActor.uc').write_text(text,encoding='ascii')
 ini=(EDITOR/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={package}\n';(EDITOR/(package+'.ini')).write_text(ini,encoding='latin1')
 out=EDITOR/(package+'.u')
 if out.exists():out.unlink()
 result=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini='+package+'.ini'],cwd=EDITOR,capture_output=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
 (ROOT/'reports'/('mmd-'+label+'-ucc.log')).write_bytes(result.stdout+result.stderr)
 assert result.returncode==0 and out.exists(),(result.stdout+result.stderr)[-2500:]
 print('PASS',package,'compiled; six full resolution textures, eight original material slots')
