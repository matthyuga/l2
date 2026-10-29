from pathlib import Path
import ast,json,uuid
R=Path(__file__).resolve().parent;O=R.parent/'model-catalog/exports/dion-living-v5';P=R/'projects/dion-hecatombe-v5.json'
assert not P.exists(),'Preserve existing project'
tree=ast.parse((R/'register-dion-v3.py').read_text(encoding='utf-8'));ns={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'helpers','exec'),ns)
center=ns['bounds'](ns['glb'](O/'colonies.glb'))
a={'id':'custom_dion_living_v5','title':'Dion · tejido vivo y espinas','path':'exports/dion-living-v5/colonies.glb','mesh':'Colonias orgánicas originales','category':'Escenarios','thumbnail':None,'native':False}
p=json.loads((R/'projects/dion-hecatombe-v4.json').read_text(encoding='utf-8'));p.update(name='dion-hecatombe-v5',scene='dion_hecatombe_v5');p['reference']['version']='Hecatombe V5 · tejido vivo';p['objects'].append({'id':str(uuid.uuid4()),'name':'Plaga viva · membranas, raíces y espinas','asset':a['id'],'node':'','kind':'model','base':True,'locked':False,'visible':True,'position':center.tolist(),'rotation':[0,0,0],'scale':[1,1,1],'parts':[],'surfaces':[]});p['cameras'][5]={'position':[23,7,19],'target':[14,0,8],'fov':46};P.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
dp=R/'data.json';d=json.loads(dp.read_text(encoding='utf-8'));backup=R/'backups/dion-living-v5';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'data.json').exists():(backup/'data.json').write_bytes(dp.read_bytes())
d['assets'].append(a);d['scenes'].append({'id':p['scene'],'title':'Dion · Hecatombe V5 · Plaga viva','asset':'custom_dion_plague_v4_core','project':P.name,'source':'Tejido vivo original, membranas y espinas sobre la plaga del terreno.','initialCamera':p['camera'],'actorMapping':{}});dp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
cp=R/'custom-assets.json';d=json.loads(cp.read_text(encoding='utf-8'));d.append(a);cp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print('REGISTERED V5')
