from pathlib import Path
import json,hashlib,shutil
D=Path(__file__).resolve().parent;R=D.parents[1];rel='data/scripts/custom/Dust2Arena/Dust2Arena.java';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=(R/'server/game'/rel).read_text(encoding='utf-8');assert 'escalera2' not in s
s=s.replace('a.equals("escalera")||','a.equals("escalera2")||a.equals("escalera")||').replace('int[] s=a.equals("escalera")?','int[] s=a.equals("escalera2")?new int[]{141320,55440,8064}:a.equals("escalera")?').replace('a.equals("escalera")?49152:0','(a.equals("escalera")||a.equals("escalera2"))?49152:0')
p=D/'stage/server'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
m=json.loads((D/'installation.json').read_text());assert len(m['files'])==2
for base in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:
 target=base/rel;backup=Path(m['backup'])/'project'/target.relative_to(R);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
 m['files'].append(dict(target=str(target),backup=str(backup),before_sha256=sha(target),after_sha256=sha(p)));shutil.copy2(p,target)
for dest in [D/'installation.json',Path(m['backup'])/'manifest.json']:dest.write_text(json.dumps(m,indent=2))
for name in ['dust2-integration','dust2-scale-v2','dust2-fit-v3','dust2-stairs-v4','dust2-ramp-v5','dust2-ramps-v6']:
 path=D.parent/name/'installation.json';parent=json.loads(path.read_text(encoding='utf-8'))
 for row in parent['files']:
  for new in m['files']:
   if Path(row['target'])==Path(new['target']):row['after_sha256']=new['after_sha256']
 parent['camera_v7']=m
 for dest in [path,Path(parent['backup'])/'manifest.json']:dest.write_text(json.dumps(parent,ensure_ascii=False,indent=2),encoding='utf-8')
probe=(D.parent/'dust2-ramp-v5/RampProbe.java').read_text().replace('class RampProbe','class CameraStairCommandProbe').replace('command.onCommand("dust2",p,"escalera")','command.onCommand("dust2",p,"escalera2")').replace('p.getX()!=139336 || p.getY()!=56560','p.getX()!=141320 || p.getY()!=55440').replace('dust2_escalera=','dust2_escalera2=')
(D/'CameraStairCommandProbe.java').write_text(probe)
print('Added .dust2 escalera2 for the long6-tread staircase; sources and manifests synchronized')
