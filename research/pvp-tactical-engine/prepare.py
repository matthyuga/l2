from pathlib import Path
import shutil
r=Path('E:/l2-local');s=Path(__file__).resolve().parent;src=s/'src/custom/ElvenPvpRoom';runtime=r/'server/game/data/scripts/custom/ElvenPvpRoom'
for p in runtime.glob('*.java'):shutil.copy2(p,src/p.name)
shutil.copy2(r/'research/bot-ai-survey/adapter-src/custom/ElvenPvpRoom/RoomTacticalPolicy.java',src/'RoomTacticalPolicy.java')
t=(src/'PvpSiegeBrain.java').read_text();(src/'PvpLegacyBrain.java').write_text(t.replace('PvpSiegeBrain','PvpLegacyBrain'))
t=t.replace('public static void regroup(PvpRoundRooms host,RoundState.Mode mode,Object group){','public static void regroup(PvpRoundRooms host,RoundState.Mode mode,Object group){PvpTacticalEngine.bind(host,mode);')
t=t.replace('public static void forget(Player p){','public static void forget(Player p){PvpTacticalEngine.forget(p);')
t=t.replace(' public static void act(Player p,Player enemy){',' public static void act(Player p,Player enemy){\n  if(PvpTacticalEngine.enabled&&PvpTacticalEngine.act(p,enemy))return;')
(src/'PvpSiegeBrain.java').write_text(t)
t=(src/'PvpRoundRooms.java').read_text().replace(' RoundState botState(Mode mode){',' PvpRoomConfig.ArenaMap tacticalMap(Mode mode){return map(rooms.get(mode));}\n RoundState botState(Mode mode){');(src/'PvpRoundRooms.java').write_text(t)
print('Prepared native tactical engine and preserved legacy baseline.')
