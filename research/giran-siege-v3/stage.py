from pathlib import Path
import hashlib,json,shutil
r=Path(__file__).resolve().parents[2];s=Path(__file__).resolve().parent
for p in (r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'):shutil.copy2(p,s/'GiranSiegeLab'/p.name)
def edit(name,old,new):
 p=s/'GiranSiegeLab'/name;t=p.read_text(encoding='utf-8');assert old in t,(name,old[:70]);p.write_text(t.replace(old,new),encoding='utf-8')
edit('GiranRoster.java','if(castle.getOwnerId()!=0||siege.isInProgress())throw new IllegalStateException("Prueba requiere Giran NPC sin asedio activo.");','if(siege.isInProgress())throw new IllegalStateException("Finaliza el asedio activo primero.");')
edit('GiranRoster.java','if(c==null||c.getLevel()<4||c.getCastleId()!=0)','if(c==null||c.getLevel()<4||c.getCastleId()!=0&&c.getCastleId()!=3)')
edit('GiranRoster.java','if(siege.checkIsDefender(c)||siege.checkIsDefenderWaiting(c))throw new IllegalStateException("Clan registrado de defensor: "+CLANS[t]);','''if(c.getId()==castle.getOwnerId()){if(siege.checkIsAttacker(c))siege.removeSiegeClan(c);continue;}
   if(siege.checkIsDefender(c)||siege.checkIsDefenderWaiting(c))siege.removeSiegeClan(c);''')
edit('GiranSiegeLab.java','if(castle.getOwnerId()!=0||castle.getSiege().isInProgress())throw new IllegalStateException("Prueba NPC requiere Giran sin propietario ni asedio activo.");','if(castle.getSiege().isInProgress())throw new IllegalStateException("Finaliza el asedio activo primero.");')
edit('GiranSiegeLab.java','if(castle.getOwnerId()!=0||castle.getSiege().isInProgress())throw new IllegalStateException("Cambio el estado del castillo.");','if(castle.getSiege().isInProgress())throw new IllegalStateException("Cambio el estado del castillo.");')
edit('GiranSiegeLab.java','move(a.p,camp(s.id,a.slot));','move(a.p,spawnPoint(a.p,s.id,a.slot));')
edit('GiranSiegeLab.java','static void move(Player p,Location to){','''static Location spawnPoint(Player p,int team,int slot){if(p.getClanId()!=GiranRules.castle().getOwnerId())return camp(team,slot);var room=GiranRules.castle().getResidenceZone().getSpawnLoc();return SiegeAgenda.safe(room.getX()+slot*40,room.getY(),room.getZ());}
 static void move(Player p,Location to){''')
old='''   for(int[] data:new int[][]{{903200,114174,145058,-2751},{903201,117700,145150,-2544}}){
    Spawn spawn=new Spawn(data[0]);spawn.setXYZ(data[1],data[2],GeoEngine.getInstance().getHeight(data[1],data[2],data[3]));spawn.setHeading(32768);spawn.setRespawnDelay(0);spawn.stopRespawn();Npc n=spawn.doSpawn(false);bosses.add(spawn);n.setRunning();
   }'''
edit('GiranSiegeLab.java',old,'''   if(castle.getOwnerId()!=0)castle.setFirstMidVictory(true); // Competitive laboratory: attackers also contest each other.
   GiranGuardians.instance.ensure();''')
edit('GiranSiegeLab.java','case "panel","estado" -> {}','case "panel","estado" -> {}\n    case "revivir" -> GiranGuardians.instance.revive(p);')
edit('GiranSiegeLab.java','{1345,4000}','{1345,4000},{2131,1200}')
edit('GiranSiegeLab.java','if(a.p.isDead()){','restoreExperience(a);if(a.p.isDead()){')
edit('GiranSiegeLab.java','Defensa inicial: NPC + Ares/Nyx<br>IA especial de bosses: pendiente','Guardianes Ares/Nyx protegen al propietario actual')
edit('GiranSiegeLab.java','Los pilotos no castean la conquista.','Lideres rivales pueden conquistar: 3 minutos. Se protegen o interrumpen al rival.')
edit('GiranSiegeLab.java','h.append(button("Actualizar","estado"))','if(p.getClanId()==c.getOwnerId())h.append(button("Revivir guardianes caidos","revivir"));\n  h.append(button("Actualizar","estado"))')
edit('GiranSiegeLab.java','int step;boolean seen;','int step;boolean seen,conquest;')
edit('GiranSiegeLab.java','long deadAt,lastMove,pendingSummon,nextThink,lastProgress;','long deadAt,lastMove,pendingSummon,nextThink,lastProgress,nextHeadquarters;boolean headquartersAttempted;')
edit('SiegeSquadBrain.java','if(!c.getSiege().isInProgress()||!c.getSiege().checkIsAttacker(p.getClan()))return false;','''if(!c.getSiege().isInProgress())return false;
  if(target.isPlayable())return GiranRules.hostile(p,target);
  if(!c.getSiege().checkIsAttacker(p.getClan()))return false;''')
edit('SiegeSquadBrain.java','boolean permitted=target instanceof Door?c.getDoors().contains(target):','boolean permitted=target instanceof Door d?GiranRules.doorAllowed(p,d):')
edit('SiegeSquadBrain.java','if(p.isCastingNow())return;','''if(p.isCastingNow())return;
  if(a.squad.conquest&&p.isClanLeader()&&GiranRules.castle().getOwnerId()!=p.getClanId()){
   Creature artifact=GiranRules.castle().getArtefacts().iterator().next();
   if(p.calculateDistance3D(artifact)<=85&&p.getZ()>=artifact.getZ()&&p.getZ()-artifact.getZ()<=45&&cast(a,246,artifact,true))return;
  }
  if(!a.headquartersAttempted&&p.isClanLeader()&&GiranRules.castle().getSiege().checkIsAttacker(p.getClan())&&now>a.nextHeadquarters){
   a.nextHeadquarters=now+15000;if(GiranRules.castle().getSiege().getFlag(p.getClan()).isEmpty()&&p.calculateDistance2D(GiranSiegeLab.camp(a.squad.id,a.slot))<600&&cast(a,247,p,false)){a.headquartersAttempted=true;return;}
  }''')
edit('SiegeSquadBrain.java','if(!repeat&&target.isAffectedBySkill(id))return false;','if(!repeat&&target.isAffectedBySkill(id))return false;')
# Preserve operator-independent shared context and base sources for concurrency-safe installation.
paths=list((r/'server/game/data/scripts/custom/GiranSiegeLab').glob('*.java'))+list((r/'server/game/data/scripts/custom/AmberContract').glob('*.java'))
baseline={str(p.relative_to(r)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
baseline['server/libs/GameServer.jar']=hashlib.sha256((r/'server/libs/GameServer.jar').read_bytes()).hexdigest()
(s/'baseline.json').write_text(json.dumps(baseline,indent=2))
print('V3 staged; runtime unchanged.')
