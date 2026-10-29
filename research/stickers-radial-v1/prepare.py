from pathlib import Path
import hashlib,json,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
current=S/'current';current.mkdir(exist_ok=True)
inputs={}
for n in ['Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat']:
    src=C/n;dest=current/n
    if dest.exists():assert sha(dest)==sha(src),'Source changed since staging: '+n
    else:shutil.copy2(src,dest)
    inputs[str(src)]=sha(src)
cfg=R/'server/game/config/Custom/WorldContent.ini'
dest=current/'WorldContent.ini'
if dest.exists():assert sha(dest)==sha(cfg),'Configuration changed since staging'
else:shutil.copy2(cfg,dest)
inputs[str(cfg)]=sha(cfg)
(S/'input-hashes.json').write_text(json.dumps(inputs,indent=2))
print('PASS: live client and server configuration snapshotted; installation guards recorded.')
