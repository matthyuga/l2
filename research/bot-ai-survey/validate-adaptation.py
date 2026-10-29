from pathlib import Path
import re,json,xml.etree.ElementTree as ET
r=Path(__file__).resolve().parent
local={int(n.attrib['id']):{'name':n.attrib.get('name'),'target':n.findtext('targetType'),'operate':n.findtext('operateType')} for p in Path('E:/l2-local/server/game/data/stats/skills').rglob('*.xml') for n in ET.parse(p).getroot().findall('skill')}
cross=[]
base=r/'L2jRoboto'
for p in sorted(base.rglob('*.java')):
 for line,text in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
  for kind,sid in re.findall(r'new\s+(OffensiveSpell|HealingSpell|SupportSpell)\(\s*(\d+)',text):
   sid=int(sid);cross.append({'repo':'L2jRoboto','path':str(p.relative_to(base)),'line':line,'kind':kind,'id':sid,'local':local.get(sid)})
p=r/'l2-smartbot/smartbot/SmartBotController.java';text=p.read_text(encoding='utf-8-sig')
for name,body in re.findall(r'\bint\s*\[\s*\]\s*([A-Z_]*SKILLS)\s*=\s*\{([^}]+)\}',text,re.S):
 for sid in re.findall(r'\d+',body):cross.append({'repo':'l2-smartbot','path':'smartbot/SmartBotController.java','kind':name,'id':int(sid),'local':local.get(int(sid))})
for name,body in re.findall(r'\bint\s*\[\s*\]\s*\[\s*\]\s*([A-Z_]*SKILLS)\s*=\s*\{(.*?)\n\s*\};',text,re.S):
 for sid in re.findall(r'\{\s*(\d+)\s*,',body):cross.append({'repo':'l2-smartbot','path':'smartbot/SmartBotController.java','kind':name,'id':int(sid),'local':local.get(int(sid))})
(r/'cross-engine-skills.json').write_text(json.dumps(cross,indent=2),encoding='utf-8')
catalog=json.loads((r/'class-catalog.json').read_text(encoding='utf-8'))
lines=['# Catalogo de perfiles revisados','','IDs contra XML local; existencia no equivale a habilidad aprendida ni prueba de combate. Las condiciones originales estan en class-catalog.json.','','| Perfil | Etapa | Skills distintas | Nombres en nuestro datapack |','|---|---|---:|---|']
for p in catalog:
 unique={s['id']:s for s in p['skills']}
 lines.append('|'+p['profile']+'|'+('Previa' if p['pre_class'] else 'Avanzada')+'|'+str(len(unique))+'|'+'; '.join(str(sid)+':'+s['local_skill']['name'] for sid,s in unique.items())+'|')
(r/'PERFILES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
result={'status':'PASS' if all(x['local'] for x in cross) else 'REVIEW','roboto_and_smartbot_skill_references':len(cross),'missing_local_ids':[x for x in cross if not x['local']],'coverage_note':'Static numeric constructors and named SKILLS arrays only; not a semantic proof or dynamic skill discovery.'}
(r/'cross-engine-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
