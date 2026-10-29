from pathlib import Path
s=Path(__file__).resolve().parent
t=(s/'VerifyRoundRoomsV3.java').read_text().replace('VerifyRoundRoomsV3','VerifyRoundRoomsV4').replace('server-verification-v3.txt','server-verification-v4.txt')
t=t.replace('free.setOnlineStatus(false,false);controller.tick();', '''
   var party=new org.l2jmobius.gameserver.entity.groups.Party(free,org.l2jmobius.gameserver.entity.groups.PartyDistributionType.FINDERS_KEEPERS);
   free.setParty(party);free2.joinParty(party);
   check(free2.isAutoAttackable(free)&&free.checkPvpSkill(free2,debuff),"FFA party restriction remained");
   free2.setXYZ(free.getX()+32,free.getY(),free.getZ());
   check(org.l2jmobius.gameserver.mechanics.skill.Skill.checkForAreaOffensiveSkills(free,free2,debuff,true),"FFA party AoE restriction remained");
   free2.leaveParty();free.leaveParty();
   Player green=player("RoundProbeGreen"),red=player("RoundProbeRed"),blue=player("RoundProbeBlue");probes.add(green);probes.add(red);probes.add(blue);
   controller.onCommand("salas",red,"tres");controller.onCommand("salas",blue,"tres");controller.onCommand("salas",green,"tres");
   check(RoomCombatRules.decision(red,green)==1&&green.getAppearance().getVisibleTitle().equals("VERDES"),"Three-team identity/relation");
   Player arena=player("RoundProbeArena");probes.add(arena);controller.onCommand("salas",arena,"arena");
   check(arena.getInstanceId()!=green.getInstanceId()&&arena.getInstanceId()!=free.getInstanceId(),"Arena not isolated");
   // A dead player survives round changes as dead, then travels after a normal revive.
   green.setDead(true);Object triple=rooms.get(Mode.THREE_TEAMS);RoundState ts=(RoundState)field(triple,"state");
   clock.set(start+config.roundNanos*3-config.voteLeadNanos);controller.tick();controller.onCommand("salas",red,"votar "+ts.generation()+" primeval");
   clock.set(start+config.roundNanos*3);controller.tick();check(green.isDead(),"Map switch revived player");
   green.setDead(false);controller.tick();check(config.maps.get("primeval").inside(new Location(green)),"Revived player not relocated to new map");
   out.append("PASS party and area attacks in FFA, three-team green identity, isolated Arena, dead-player map transition without resurrection.\\n");
   free.setOnlineStatus(false,false);controller.tick();''')
(s/'VerifyRoundRoomsV4.java').write_text(t)
(s/'verify-v4.mf').write_text('Manifest-Version: 1.0\nAgent-Class: VerifyRoundRoomsV4\n\n')
