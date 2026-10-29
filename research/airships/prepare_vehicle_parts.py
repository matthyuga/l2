"""Use the actual VehiclePartsGrp recipe rather than guessing from names."""
import sys,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2];CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(CAT));import build_gallery as b
b.OPTIONS=['-game=l2','-path='+str(ROOT/'research/airships/gracia-assets')]
rows=json.loads((ROOT/'research/airships/vehicle-parts-decoded.json').read_text())
report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
for row in rows:
 if row['id'] not in (2,3):continue
 mesh=row['mesh_items'][0]['mesh0'];name=mesh.split('.')[1];key='airship_animated_'+name
 textures=[x['texture0'] for x in row['texture_items']]
 m={'key':key,'mesh':mesh,'package':'LineageVehicles','category':'Personalizados','title':'Gracia · '+name+' (pieza animada)','names':['Gracia','Pieza de vehículo'],'npcs':[{'textures':textures}],'npc_count':0,'types':['Estructura'],'external_source':True,'preview_only':True}
 b.prepare(m);m['npcs']=[]
 p=CAT/m['gltf'];d=json.loads(p.read_text())
 for i,mat in enumerate(d.get('materials',[])):
  ref=textures[i];pkg=ref.split('.')[0];obj=ref.split('.')[-1]
  proc=subprocess.run([str(b.UMODEL),'-dump',*b.OPTIONS,pkg,obj],capture_output=True,text=True,errors='replace',timeout=30)
  if 'ClassName: Shader' in proc.stdout and 'Opacity = None' in proc.stdout and 'OutputBlending = OB_Normal' in proc.stdout and 'AlphaRef = 0' in proc.stdout:
   mat.pop('alphaMode',None);mat.pop('alphaCutoff',None)
 p.write_text(json.dumps(d),encoding='utf-8')
 report['models']=[x for x in report['models'] if x['key']!=key]+[m]
 print('Prepared actual vehicle part',mesh,flush=True)
report['model_count']=len(report['models']);(CAT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
