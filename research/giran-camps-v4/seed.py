from pathlib import Path
import hashlib, json
r=Path(__file__).resolve().parents[2]
b=r/'backups/giran-camps-v4-2026-10-11/GiranSiegeLab'
state={'GiranSiegeLab/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.glob('*.java')}
state['GameServer.jar']=hashlib.sha256((r/'server/libs/GameServer.jar').read_bytes()).hexdigest()
(r/'research/giran-camps-v4/baseline.json').write_text(json.dumps(state,indent=2))
text=(r/'research/giran-siege-v3/state.js').read_text().replace('giran-siege-v3-2026-10-11','giran-camps-v4-2026-10-11')
(r/'research/giran-camps-v4/state.js').write_text(text)
