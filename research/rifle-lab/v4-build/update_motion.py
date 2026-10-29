import json,sys,subprocess
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R.parent/'v4-motion'));from write_multi_animation import generate
states=json.loads((R/'states.json').read_text());fitted=json.loads((R/'states-contact.json').read_text());selectors={'peace_idle':['wait_Hand','Wait_1HS'],'combat_idle':['AtkWait_Hand','AtkWait_1HS'],'walk':['walk_hand','Walk_1HS'],'run':['Run_Hand','Run_1HS'],'aim':['Social01','SpWait01'],'fire':['atk01_Hand','Atk01_1HS']}
for s,f in zip(states,fitted):s.update(psa=f['psa'],blend=f['blend'],hand_contact_max_error=f['hand_contact_max_error'])
entries=[{'psa':s['psa'],'name':n} for s in states for n in selectors[s['state']]]
report=generate(entries,R/'HGRifleMotionV4.ukx',R.parent/'v4-textures/RifleNPCV4.psk');(R/'motion-build.json').write_text(json.dumps(report,indent=2))
for s in states:generate([{'psa':s['psa'],'name':'wait_Hand'}],R/(s['package']+'.ukx'),R.parent/'v4-textures/RifleNPCV4.psk')
(R/'states.json').write_text(json.dumps(states,indent=2))
