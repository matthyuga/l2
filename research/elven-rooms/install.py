from pathlib import Path
import shutil, datetime, json, hashlib
root=Path('E:/l2-local')
stage=root/'research/elven-rooms'
if (stage/'installation.json').exists():
    raise SystemExit('Installation manifest already exists. Refusing to overwrite the baseline backup; use a reviewed update.')
backup=root/'backups'/('elven-rooms-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
roots=[root/'server/game',root/'source/L2J_Mobius_CT_0_Interlude/dist/game',root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']
records=[]
def put(path,data):
    rel=path.relative_to(root)
    if path.exists():
        old=backup/rel;old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,old)
    records.append({'path':str(path),'existed':path.exists(),'backup':str(backup/rel)})
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data,encoding='utf-8')
    records[-1]['installed_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
source=(roots[0]/'data/scripts/custom/ElvenPvpRoom/ElvenPvpRoom.java').read_text(encoding='utf-8')
start=source.index('\tprivate static void enterRoom(Player player)')
end=source.index('\tprivate static void showStatus(Player player)',start)
source=source[:start]+'''\tprivate static void enterRoom(Player player)
\t{
\t\tfinal IVoicedCommandHandler lobby = VoicedCommandHandler.getInstance().getHandler("salas");
\t\tif (lobby != null) lobby.onCommand("salas", player, "elven");
\t\telse player.sendMessage("El menu de salas PvP aun no esta disponible.");
\t}

\tprivate static void leaveRoom(Player player)
\t{
\t\tfinal IVoicedCommandHandler lobby = VoicedCommandHandler.getInstance().getHandler("salas");
\t\tif (lobby != null) lobby.onCommand("salas", player, "salir");
\t}

'''+source[end:]
source=source.replace('''\t\t\t\t\tprepareArenaPlayer(player);
\t\t\t\t\tplayer.sendMessage("Reapareciste con HP, MP y CP completos; tus buffs fueron conservados.");''','''\t\t\t\t\tplayer.sendMessage("Reapareciste en Elven PvP. La sala no restaura recursos ni efectos.");''')
source=source.replace('''\t * It also detects player revival so every arena respawn starts fully restored
\t * and protected by a fresh Noblesse Blessing.''','''\t * Revival is observed without modifying player resources or effects.''')
source=source.replace('''\t\tplayer.fullRestore();''','''\t\t// Retained for class compatibility with the running controller. Entry/revival never call this.
\t\tif (true) return;
\t\tplayer.fullRestore();''')
# A single targeted custom NPC template; no client assets required.
npc='''<?xml version="1.0" encoding="UTF-8"?>
<list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../../xsd/npcs.xsd">
 <npc id="902600" displayId="30146" level="80" type="Folk" name="Salas PvP" title="HELLGAMES" usingServerSideName="true" usingServerSideTitle="true">
  <race>HUMAN</race><sex>FEMALE</sex>
  <stats str="40" int="21" dex="30" wit="20" con="43" men="20">
   <vitals hp="10000" hpRegen="10" mp="1000" mpRegen="5" />
   <attack physical="100" magical="100" attackSpeed="300" /><defence physical="1000" magical="1000" />
   <speed><walk ground="0" /><run ground="0" /></speed>
  </stats>
  <status talkable="true" attackable="false" undying="true" randomWalk="false" />
  <collision><radius normal="9" /><height normal="23" /></collision>
 </npc>
</list>
'''
for base in roots:
    put(base/'data/scripts/custom/ElvenPvpRoom/ElvenPvpRoom.java',source)
    put(base/'data/scripts/custom/ElvenPvpRoom/PvpRooms.java',(stage/'PvpRooms.java').read_text(encoding='utf-8'))
    put(base/'data/stats/npcs/custom/pvp_rooms.xml',npc)
    path=base/'data/instances/custom/elven_village_pvp.xml'
    data=path.read_text(encoding='utf-8').replace('<exitPoint x="46890" y="51531" z="-2976" />','<exitPoint x="83425" y="148585" z="-3406" />')
    put(path,data)
backup.mkdir(parents=True,exist_ok=True)
(stage/'installation.json').write_text(json.dumps({'backup':str(backup),'files':records},indent=2),encoding='utf-8')
print(str(backup))
