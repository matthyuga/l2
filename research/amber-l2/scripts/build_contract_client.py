import copy,json,pathlib,subprocess
from contract_dat import Catalog
ROOT=pathlib.Path(__file__).resolve().parents[1];BACKUP=ROOT.parents[1]/'backups/amber-contract-2026-10-09';OUT=ROOT/'exports/contract';OUT.mkdir(exist_ok=True)
specs={19001:(1333,'Invocar Amber','Invoca a Amber. Un summon a la vez. Reuse120s.'),19002:(1223,'Flechas de fuego','Amber: daño fisico+25% durante15s. Consume60MP. Reuse30s.'),19003:(24,'Lluvia de flechas','Amber dispara al cielo3,5s. Zona fija radio200, tres impactos.120MP y3 Beast Soulshots. Reuse45s.'),19004:(1059,'Romper contrato','Retira Amber y revoca solo las habilidades del contrato, fuera de combate.'),19005:(1223,'Flechas igneas de Amber','Daño fisico de Amber+25% durante15s.'),19006:(24,'Carga de lluvia','Disparos ascendentes durante3,5s.'),19007:(24,'Lluvia de Amber','Flechas descendentes.'),19008:(1223,'Lluvia ignea de Amber','Flechas de fuego descendentes.'),19009:(1223,'Disparo igneo de Amber','Efecto de flecha de fuego.'),19010:(1059,'Zona de lluvia','Zona fija marcada durante la preparacion.')}
grp=Catalog(BACKUP/'skillgrp.raw','skillgrp.xml','ScionsOfDestiny');rows=[]
for id,(source,name,desc) in specs.items():
    assert not any(r['skill_id']==id for r in grp.rows)
    r=copy.deepcopy(next(r for r in grp.rows if r['skill_id']==source and r['skill_level']==1));r.update(skill_id=id,skill_level=1,mp_consume=0,hit_time=0.0,cast_range=900,is_magic=2,animation='',description='',cast_style=0)
    if id==19005:r.update(operate_type=1,description='skill.su.1059')
    if id==19006:r.update(animation='S',cast_style=5,hit_time=3.5,is_magic=0,description='AmberEffects.SkyVolley')
    if id in (19007,19008,19009,19010):r.update(cast_style=12,description={19007:'AmberEffects.Rain',19008:'AmberEffects.FireRain',19009:'AmberEffects.FireShot',19010:'AmberEffects.Mark'}[id],hit_time=0.1)
    rows.append(r)
grp.append(rows,OUT/'skillgrp.raw')
names=Catalog(BACKUP/'skillname.raw','skillname.xml','ScionsOfDestiny');rows=[]
for id,(_,name,desc) in specs.items():
    r=copy.deepcopy(names.rows[0]);r.update(skill_id=id,skill_level=1,name=name,desc=desc,enchant_name='',enchant_desc='');rows.append(r)
names.append(rows,OUT/'skillname.raw')
npc=Catalog(BACKUP/'npcgrp.raw','npcgrp.xml','Interlude');r=copy.deepcopy(next(r for r in npc.rows if r['npc_id']==59001));r.update(npc_id=59002,mesh_name='L2AmberArcher.AmberNPC',quest_be=0,attack_effect='LineageEffect.p_u002_a')
r['texture_name_items']=[{'param_texture_name':'L2AmberArcher.AmberBodyShader'},{'param_texture_name':'L2AmberArcher.AmberOutfitShader'}]
marker=copy.deepcopy(r);marker.update(npc_id=59003,mesh_name='',texture_name=0,texture_name_items=[],quest_be=0)
npc.append([r,marker],OUT/'npcgrp.raw')
npcnames=Catalog(BACKUP/'npcname.raw','npcname.xml','ScionsOfDestiny');a=copy.deepcopy(next(r for r in npcnames.rows if r['id']==59001)) if any('id' in r for r in npcnames.rows) else None
if a is None:
    print('NPCNAME fields',npcnames.rows[0]);raise RuntimeError('Unknown NPC name fields')
rows=[]
for id,name in [(59002,'Amber'),(59003,'')]:
    r=copy.deepcopy(a);r.update(id=id,name=name,nick='');rows.append(r)
npcnames.append(rows,OUT/'npcname.raw')
for file,schema,pattern in [('skillgrp','skillgrp.xml','ScionsOfDestiny'),('skillname','skillname.xml','ScionsOfDestiny'),('npcgrp','npcgrp.xml','Interlude'),('npcname','npcname.xml','ScionsOfDestiny')]:
    verified=Catalog(OUT/(file+'.raw'),schema,pattern);print(file,verified.count,'parsed',verified.end)
(ROOT/'reports/contract-client-records.json').write_text(json.dumps(dict(skills=list(specs),display_ids=[59002,59003],original_records_preserved=True),indent=2))
