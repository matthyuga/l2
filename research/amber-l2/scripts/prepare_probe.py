from pathlib import Path
import json
import hashlib

root = Path(__file__).resolve().parents[1]
editor = root / 'tools/l2editor/L2Editor'
package = editor.parent / 'L2AmberProbe'
(package / 'Classes').mkdir(parents=True, exist_ok=True)
psk = root / 'exports/l2-reference/Fighter/SkeletalMesh/FFighter_m001_u.psk'
source = f'''class ProbeActor extends Actor;
#exec MESH MODELIMPORT MESH=ProbeMesh MODELFILE="{psk.as_posix()}" LODSTYLE=0
#exec ANIM IMPORT ANIM=ProbeAnim ANIMFILE="{(root / 'exports/l2-reference/Fighter/MeshAnimation/FFighter_anim.psa').as_posix()}" COMPRESS=1
#exec ANIM DIGEST ANIM=ProbeAnim VERBOSE=1
#exec MESH DEFAULTANIM MESH=ProbeMesh ANIM=ProbeAnim
defaultproperties
{{
    DrawType=DT_Mesh
    Mesh=SkeletalMesh'L2AmberProbe.ProbeMesh'
}}
'''
(package / 'Classes/ProbeActor.uc').write_text(source, encoding='ascii')
config = (editor / 'UT2003.ini').read_text(encoding='latin1')
config += '\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=L2AmberProbe\n'
(editor / 'AmberLab.ini').write_text(config, encoding='latin1')
archive = root / 'tools/L2Editor-2024.7z'
manifest = json.loads((root / 'reports/tool-sources.json').read_text())
manifest.append({'name': archive.name, 'source': 'https://drive.google.com/file/d/1Mpnfg4mPzgqHPPZ38wDqk4Il08qrvoi6/view', 'bytes': archive.stat().st_size, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'publisher': '911reg, modified lordofdest L2Editor'})
(root / 'reports/tool-sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
