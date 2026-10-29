from pathlib import Path
import zipfile
s=Path(__file__).resolve().parent
p=Path('E:/l2-local/source/L2J_Mobius_CT_0_Interlude/java/org/l2jmobius/gameserver/entity/WorldObject.java')
t=p.read_text();needle='\t\tfinal int oldInstanceId = getInstanceId();'
assert t.count(needle)==1
t=t.replace(needle,needle+'''\n\t\tif ((getObjectId() == 268473899) && (oldInstanceId != instanceId))
\t\t{ new Exception("ELVEN_INSTANCE_TRACE " + oldInstanceId + " -> " + instanceId).printStackTrace(); }''')
needle='\t\t_location.setXYZ(newX, newY, newZ);'
assert t.count(needle)==1
t=t.replace(needle,'''\t\tif ((getObjectId() == 268473899) && (Math.abs((long)newX-getX())+Math.abs((long)newY-getY())>10000))
\t\t{ new Exception("ELVEN_POSITION_TRACE").printStackTrace(); }
'''+needle)
out=s/'instance-trace-src/org/l2jmobius/gameserver/entity/WorldObject.java';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(t)
with zipfile.ZipFile('E:/l2-local/server/libs/GameServer.jar') as z:(s/'WorldObject.original.class').write_bytes(z.read('org/l2jmobius/gameserver/entity/WorldObject.class'))
