from pathlib import Path
import shutil,json,hashlib,datetime,zipfile
R=Path('E:/l2-local');S=Path(__file__).resolve().parent
if (S/'baseline.json').exists():raise SystemExit('Baseline exists')
backup=R/'backups'/('elven-position-sync-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
rels=['java/org/l2jmobius/gameserver/network/clientpackets/ValidatePosition.java','java/org/l2jmobius/gameserver/network/clientpackets/MoveToLocation.java','java/org/l2jmobius/gameserver/managers/RoomTeleportSync.java']
rows=[]
def remember(p):
    dst=backup/p.relative_to(R)
    if p.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    rows.append({'path':str(p),'existed':p.exists(),'backup':str(dst),'before_sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None})
remember(R/'server/libs/GameServer.jar')
for b in [R/'source/L2J_Mobius_CT_0_Interlude',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude']:
    for rel in rels:remember(b/rel)
for b in [R/'server/game',R/'source/L2J_Mobius_CT_0_Interlude/dist/game',R/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game']:remember(b/'data/scripts/custom/ElvenPvpRoom/PvpRooms.java')
for rel in rels:
    dst=S/'src'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    if rel.endswith('RoomTeleportSync.java'):shutil.copy2(S/'RoomTeleportSync.java',dst);continue
    t=(R/'source/L2J_Mobius_CT_0_Interlude'/rel).read_text()
    if rel.endswith('ValidatePosition.java'):
        marker='\t\tfinal int realX = player.getX();'
        injection='''\t\tif (org.l2jmobius.gameserver.managers.RoomTeleportSync.reject(player, _x, _y, _z))
\t\t{
\t\t\tplayer.sendPacket(new ValidateLocation(player));
\t\t\treturn;
\t\t}
\t\t
'''
    else:
        marker='\t\tif (player.isOverloaded())'
        injection='''\t\tif (org.l2jmobius.gameserver.managers.RoomTeleportSync.reject(player, _originX, _originY, _originZ))
\t\t{
\t\t\tplayer.sendPacket(new org.l2jmobius.gameserver.network.serverpackets.ValidateLocation(player));
\t\t\tplayer.sendPacket(ActionFailed.STATIC_PACKET);
\t\t\treturn;
\t\t}
\t\t
'''
    assert t.count(marker)==1;t=t.replace(marker,injection+marker);dst.write_text(t,encoding='utf-8')
t=(R/'server/game/data/scripts/custom/ElvenPvpRoom/PvpRooms.java').read_text()
marker='''        p.teleToLocation(destination.getX(),destination.getY(),destination.getZ(),destination.getHeading(),instance,false);
        p.onTeleported();'''
assert t.count(marker)==1
t=t.replace(marker,'''        org.l2jmobius.gameserver.managers.RoomTeleportSync.arm(p,instance);
        p.teleToLocation(destination.getX(),destination.getY(),destination.getZ(),destination.getHeading(),instance,false);
        p.setClientX(p.getX()); p.setClientY(p.getY()); p.setClientZ(p.getZ());
        p.setCursorKeyMovement(false);
        p.onTeleported();''')
marker='''        p.setXYZ(destination.getX(),destination.getY(),destination.getZ()); p.setHeading(destination.getHeading());'''
assert t.count(marker)==1;t=t.replace(marker,'''        org.l2jmobius.gameserver.managers.RoomTeleportSync.arm(p,p.getInstanceId());
'''+marker)
(S/'PvpRooms.java').write_text(t,encoding='utf-8')
with zipfile.ZipFile(R/'server/libs/GameServer.jar') as z:
    for name in ['ValidatePosition','MoveToLocation']:(S/(name+'.original.class')).write_bytes(z.read('org/l2jmobius/gameserver/network/clientpackets/'+name+'.class'))
(S/'baseline.json').write_text(json.dumps({'backup':str(backup),'files':rows},indent=2),encoding='utf-8')
print('Prepared with backup',backup)
