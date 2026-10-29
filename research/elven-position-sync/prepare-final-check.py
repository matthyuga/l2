from pathlib import Path
s=Path(__file__).resolve().parent
text=(s/'CheckClientRoomSync.java').read_text()
text=text.replace('CheckClientRoomSync','CheckClientRoomSyncV2')
text=text.replace('int oldX=p.getX(),oldY=p.getY(),oldZ=p.getZ();','int oldX=83425,oldY=148585,oldZ=-3406; // known pre-entry Giran coordinates')
text=text.replace('int x=p.getX(),y=p.getY(),z=p.getZ();','int x=p.getX(),y=p.getY(),z=p.getZ();\n   org.l2jmobius.gameserver.managers.RoomTeleportSync.arm(p,room);\n   require(Math.hypot(oldX-x,oldY-y)>600,"Fixture must be outside synchronization tolerance");')
text=text.replace('client-verification.txt','client-verification-v2.txt')
(s/'CheckClientRoomSyncV2.java').write_text(text)
(s/'client-check-v2.mf').write_text('Manifest-Version: 1.0\nAgent-Class: CheckClientRoomSyncV2\n\n')
