from pathlib import Path
import json,shutil,hashlib
r=Path(__file__).resolve().parents[3];s=Path(__file__).resolve().parent
b=r/'backups/summon-buffs-2026-10-10';old=json.loads((b/'original-hashes.json').read_text());state=s/'mirror-hashes.json';prior=json.loads(state.read_text()) if state.exists() else {}
source=r/'source/L2J_Mobius_CT_0_Interlude';cloud=r/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pairs=[]
rel=Path('java/org/l2jmobius/gameserver/entity/actor/instance/SchemeBuffer.java');pairs.append((source/rel,cloud/rel,old[str(source/rel)]))
runtime=r/'server/game/data/html/mods/SchemeBuffer/50008.htm'
for base in (source,cloud):pairs.append((runtime,base/'dist/game/data/html/mods/SchemeBuffer/50008.htm',old[str(runtime)]))
test=r/'server/game/data/scripts/custom/SummonBuffs/SummonBuffVerification.java'
for base in (source,cloud):pairs.append((test,base/'dist/game/data/scripts/custom/SummonBuffs'/test.name,None))
for src,dst,expected in pairs:
 if dst.exists():assert sha(dst) in (expected,sha(src),prior.get(str(dst))),'Concurrent mirror edit: '+str(dst)
for src,dst,expected in pairs:
 if dst.exists():
  backup=b/'mirrors'/dst.relative_to(r);backup.parent.mkdir(parents=True,exist_ok=True)
  if not backup.exists():shutil.copy2(dst,backup)
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);prior[str(dst)]=sha(dst)
state.write_text(json.dumps(prior,indent=2))
mirror=r/'cloud-repo/research/client-comfort/summon-buffs';mirror.mkdir(parents=True,exist_ok=True)
for p in s.iterdir():
 if p.suffix in ('.py','.ps1','.json'):shutil.copy2(p,mirror/p.name)
print('PASS: buffer sources/menu and opt-in verifier mirrored; unrelated files untouched.')
