import sys,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/model-catalog'))
import build_gallery as b
b.OPTIONS=['-game=l2','-path='+str(ROOT/'research/airships/gracia-assets')]
original=b.run
b.run=lambda args:original([x.replace('.ukx','.usx') for x in args])
items=[('L2_Ship_L01_S',x) for x in ['fly_boat_body001','fly_boat_body002','fly_boat_body003','fly_boat_body004','fly_boat_steering001','fly_boat_steering002','fly_boat_cannon001']]
items += [('Glacia_kserth_S',x) for x in ['G_kserth_port_ship_obj','G_kserth_port_gr_link','G_kserth_start_walk1F','G_kserth_port_rock']]
items += [('Glacia_kserth_S',x) for x in ['G_kserth_port_gr','G_kserth_port_gr_side','G_kserth_port_bm','G_kserth_port_gg','G_kserth_port_gard','G_kserth_start_walk1FF']]
items += [('Glacia_destruction_S',x) for x in ['Glacia_destruction_Tower','Glacia_destruction_DeadTower','Glacia_destruction_FlyMini']]
items += [('Glacia_undying_S',x) for x in ['immortal_landmark_top','immortal_landmark_head','matrix_out']]
items += [('Glacia_Fieldobj_S',x) for x in ['G_Field_kserthgateway','G_Field_Astone01']]
items += [('GraC_S2',x) for x in ['E_F_tower_01','E_F_bridge_01']]
path=b.OUT/'gallery.json'
if not (ROOT/'research/airships/gallery-before-airships.json').exists():shutil.copy2(path,ROOT/'research/airships/gallery-before-airships.json')
report=json.loads(path.read_text(encoding='utf-8'))
for p,n in items:
 key='airship_'+n.lower()
 if any(x['key']==key for x in report['models']):continue
 m={'key':key,'mesh':p+'.'+n,'package':p,'category':'Personalizados','title':'Gracia · '+n,'names':['Estructuras aéreas de Gracia'],'npcs':[],'npc_count':0,'texture_variants':0,'types':['Estructura'],'external_source':True}
 b.prepare(m)
 report['models']=[x for x in report['models'] if x['key']!=key]+[m]
 print('Prepared',n,m['textured_materials'],m['material_count'],flush=True)
report['model_count']=len(report['models'])
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
