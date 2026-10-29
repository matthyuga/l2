from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent;b=r/'backups/giran-orders-v5-2026-10-11/GiranSiegeLab'
state={'GiranSiegeLab/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.glob('*.java')}
state['GameServer.jar']=hashlib.sha256((r/'backups/giran-orders-v5-2026-10-11/GameServer-before.jar').read_bytes()).hexdigest()
(s/'baseline.json').write_text(json.dumps(state,indent=2))
(s/'state.js').write_text((r/'research/giran-camps-v4/state.js').read_text().replace('giran-camps-v4-2026-10-11','giran-orders-v5-2026-10-11'))
(s/'install.ps1').write_text((r/'research/giran-camps-v4/install.ps1').read_text().replace('giran-camps-v4-2026-10-11','giran-orders-v5-2026-10-11'))
