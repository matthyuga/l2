from pathlib import Path
import hashlib,json,shutil
r=Path(__file__).resolve().parents[1];s=r/'research/giran-guardians-v7';b=r/'backups/giran-guardians-v7-2026-10-11'
assert not s.exists(), 'Stage already exists'
(s/'GiranSiegeLab').mkdir(parents=True);(b/'GiranSiegeLab').mkdir(parents=True)
m={}
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):
    shutil.copy2(p,s/'GiranSiegeLab'/p.name);shutil.copy2(p,b/'GiranSiegeLab'/p.name);m['GiranSiegeLab/'+p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
for k,p in {'GameServer.jar':r/'server/libs/GameServer.jar','geodata/23_22.l2j':r/'server/game/data/geodata/23_22.l2j','npcs/giran_lab_guardians.xml':r/'server/game/data/stats/npcs/custom/giran_lab_guardians.xml'}.items():m[k]=hashlib.sha256(p.read_bytes()).hexdigest()
(s/'baseline.json').write_text(json.dumps(m,indent=2))
t=(r/'research/giran-assault-v6/install.ps1').read_text(encoding='utf-8-sig').replace('giran-assault-v6-2026-10-11','giran-guardians-v7-2026-10-11')
t=t.replace("elseif($entry.Name.StartsWith('geodata/'))", "elseif($entry.Name.StartsWith('npcs/')){'server/game/data/stats/npcs/custom/'+$entry.Name.Substring(5)}elseif($entry.Name.StartsWith('geodata/'))")
t=t.replace(";Copy-Item (Join-Path $PSScriptRoot 'repaired-geodata/23_22.l2j') $geo", "")
t=t.replace("$state['GameServer.jar']=", "$state['npcs/giran_lab_guardians.xml']=(Get-FileHash (Join-Path $root 'server/game/data/stats/npcs/custom/giran_lab_guardians.xml')).Hash\n$state['GameServer.jar']=")
(s/'install.ps1').write_text(t,encoding='utf-8')
(s/'state.js').write_text((r/'research/giran-assault-v6/state.js').read_text().replace('giran-assault-v6-2026-10-11','giran-guardians-v7-2026-10-11'))
t=(s/'GiranSiegeLab/GiranDefenseVerification.java').read_text().replace('GIRAN_V6_VERIFY','GIRAN_V7_VERIFY')
t=t.replace('c.setFirstMidVictory(true);','c.setFirstMidVictory(true);GiranGuardians.instance.verificationPaused=true;')
t=t.replace('// Real native bow damage, autonomous selection, owner target unset.','GiranGuardianVerification.run(squads, this::check, (condition,why,timeout)->waitFor(condition,why,timeout));\n  // Real native bow damage, autonomous selection, owner target unset.')
t=t.replace('if(started)c.getSiege().endSiege();','if(started)c.getSiege().endSiege();GiranGuardians.instance.verificationPaused=false;for(var g:GiranGuardians.instance.actors){GiranGuardianBrain.clear(g);g.returning=true;}')
(s/'GiranSiegeLab/GiranDefenseVerification.java').write_text(t,encoding='utf-8')
(s/'classes').mkdir()
print('V7 isolated stage; runtime unchanged.')
