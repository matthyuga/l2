"""Honor opaque UE2 shaders whose diffuse alpha stores specular data."""
import json,pathlib,subprocess,re,shutil
ROOT=pathlib.Path(__file__).resolve().parents[2];CAT=ROOT/'research/model-catalog'
exe=ROOT/'research/amber-l2/tools/umodel.exe';client=ROOT/'research/airships/gracia-assets'
report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'));audit=[]
scene_path=ROOT/'research/airships/scene-meshes.json'
if scene_path.exists():report['models']+=list(json.loads(scene_path.read_text(encoding='utf-8')).values())
for m in report['models']:
 if not m['key'].startswith(('airship_','scene_','superion_')) or (m.get('preview_only') and not m['key'].startswith('superion_')):continue
 p=CAT/m['gltf'];d=json.loads(p.read_text());changed=False
 log=(CAT/'build-logs'/f"{m['key']}.log").read_text(encoding='utf-8')
 refs={name.lower():pathlib.Path(pkg).stem+'.'+name for name,pkg in re.findall(r'Loading \w+ (\S+) from package (\S+)',log)}
 for mat in d.get('materials',[]):
  if mat.get('alphaMode')!='MASK':continue
  ref=refs.get(mat['name'].lower())
  if not ref:continue
  package,name=ref.split('.',1)
  asset_root=ROOT/'research/airships/superion-assets' if package.lower().startswith('superion') else client
  proc=subprocess.run([str(exe),'-dump','-game=l2','-path='+str(asset_root),package,name],capture_output=True,text=True,errors='replace',timeout=30)
  text=proc.stdout
  if 'ClassName: Shader' in text and 'Opacity = None' in text and 'OutputBlending = OB_Normal' in text and 'AlphaRef = 0' in text:
   mat.pop('alphaMode',None);mat.pop('alphaCutoff',None);changed=True
   audit.append({'model':m['mesh'],'material':ref,'reason':'Opaque normal shader, no opacity texture, AlphaRef zero; diffuse alpha is used by SpecularityMask.'})
 if changed:
  backup=p.with_suffix('.before-alpha-fix.json')
  if not backup.exists():shutil.copy2(p,backup)
  p.write_text(json.dumps(d),encoding='utf-8')
audit_path=ROOT/'research/airships/material-fix-audit.json'
previous=json.loads(audit_path.read_text()) if audit_path.exists() else []
audit_path.write_text(json.dumps(previous+audit,indent=2),encoding='utf-8')
print('Corrected',len(audit),'material slots')
