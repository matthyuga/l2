from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[3];s=Path(__file__).resolve().parent
assert not (s/'mirror-hashes.json').exists(),'Migration applies only to the first mirror state'
source=r/'source/L2J_Mobius_CT_0_Interlude';cloud=r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'
paths=[]
rel=Path('java/org/l2jmobius/gameserver/entity/actor/instance/SchemeBuffer.java')
before=(source/rel).read_text().replace('Magic damage against living targets identifies casters; base stats identify support summons.','Magic damage skills identify casters; base stats identify support summons.').replace('skill.isDamage()\n\t\t\t\t\t&& !skill.getTargetType().name().contains("CORPSE")','skill.isDamage()')
paths.append((cloud/rel,before))
test=r/'server/game/data/scripts/custom/SummonBuffs/SummonBuffVerification.java'
before=test.read_text().replace('14207,14251,14391','14207,14391').replace('14251,14391,14435,14619,14837','14391,14435,14575,14619,14837').replace('12 summon templates','11 summon templates')
rel=Path('dist/game/data/scripts/custom/SummonBuffs')/test.name
paths.extend((base/rel,before) for base in (source,cloud))
state={}
for target,expected in paths:
 assert target.read_text()==expected,'Concurrent mirror edit: '+str(target)
 state[str(target)]=hashlib.sha256(target.read_bytes()).hexdigest()
(s/'mirror-hashes.json').write_text(json.dumps(state,indent=2));print('PASS: reconstructed exact previous revision matches mirrors; concurrency state recovered.')
