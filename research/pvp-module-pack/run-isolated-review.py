from pathlib import Path
import subprocess,json,shutil,hashlib,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'review-tests';OUT.mkdir(exist_ok=True)
SRC=OUT/'java-src';SRC.mkdir(exist_ok=True)
JDK=Path('E:/l2-local/tools/jdk-25.0.4.1+1/bin')
def put(name,text):
    p=SRC/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def copy(src,name):put(name,Path(src).read_text(encoding='utf-8-sig'))

# These are explicit lightweight collaborators, not a replacement server.
put('org/l2jmobius/gameserver/entity/actor/Creature.java','''package org.l2jmobius.gameserver.entity.actor;
public class Creature { public boolean isPlayer(){return this instanceof Player;} public Player asPlayer(){return (Player)this;} }''')
put('org/l2jmobius/gameserver/entity/actor/Player.java','''package org.l2jmobius.gameserver.entity.actor;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
public class Player extends Creature { public int flag; public long until; public void updatePvPFlag(int v){flag=v;} public int getPvpFlag(){return flag;} public void sendMessage(String s){} public void broadcastUserInfo(){} public long getPvpFlagLasts(){return until;} public void stopPvPFlag(){flag=0;PvpFlagTaskManager.getInstance().remove(this);} }''')
put('org/l2jmobius/gameserver/entity/zone/ZoneType.java','''package org.l2jmobius.gameserver.entity.zone;
import org.l2jmobius.gameserver.entity.actor.Creature;
public abstract class ZoneType {public ZoneType(int id){} protected abstract void onEnter(Creature c);protected abstract void onExit(Creature c); public abstract void onDieInside(Creature c);public abstract void onReviveInside(Creature c);}''')
put('org/l2jmobius/commons/threads/ThreadPool.java','''package org.l2jmobius.commons.threads; public class ThreadPool {public static void schedulePriorityTaskAtFixedRate(Runnable r,long a,long b){} }''')
native=Path('E:/l2-local/source/L2J_Mobius_CT_0_Interlude/java')
for rel in ['org/l2jmobius/gameserver/entity/zone/type/FlagPvPZone.java','org/l2jmobius/gameserver/taskmanagers/PvpFlagTaskManager.java']:copy(native/rel,rel)

put('l2jorion/Config.java','''package l2jorion; public class Config {public static int PVP_ZONE_INSTANCE_ID=3051;public static boolean PROHIBIT_HEALER_CLASS=true;}''')
put('l2jorion/game/model/L2Character.java','''package l2jorion.game.model; public class L2Character {}''')
put('l2jorion/game/model/Location.java','''package l2jorion.game.model; public record Location(int x,int y,int z){}''')
put('l2jorion/game/model/base/ClassId.java','''package l2jorion.game.model.base; public enum ClassId {cardinal,evaSaint,shillienSaint,fighter}''')
put('l2jorion/game/model/zone/ZoneId.java','''package l2jorion.game.model.zone; public enum ZoneId {ZONE_RANDOM}''')
put('l2jorion/game/model/zone/L2ZoneType.java','''package l2jorion.game.model.zone; import l2jorion.game.model.L2Character; public abstract class L2ZoneType {public L2ZoneType(int id){} public void setParameter(String n,String v){} public String getName(){return "test";} public abstract int getId();protected abstract void onEnter(L2Character c);protected abstract void onExit(L2Character c);public abstract void onDieInside(L2Character c);public abstract void onReviveInside(L2Character c);}''')
put('l2jorion/game/datatables/csv/MapRegionTable.java','''package l2jorion.game.datatables.csv; public class MapRegionTable {public enum TeleportWhereType{Town}}''')
put('l2jorion/game/network/serverpackets/ExShowScreenMessage.java','''package l2jorion.game.network.serverpackets;public class ExShowScreenMessage {public ExShowScreenMessage(String s,int t,int p,boolean b){}}''')
put('l2jorion/util/random/Rnd.java','''package l2jorion.util.random; public class Rnd {public static int get(int min,int max){if(max<min)throw new IllegalArgumentException("empty range");return min;}}''')
put('l2jorion/game/model/actor/instance/L2PcInstance.java','''package l2jorion.game.model.actor.instance;
import l2jorion.game.model.*;import l2jorion.game.model.base.*;import l2jorion.game.model.zone.*;import l2jorion.game.datatables.csv.MapRegionTable.TeleportWhereType;
public class L2PcInstance extends L2Character {public int instance=3051,flag=0,stops=0,normalTimerStarts=0;public boolean inside=false,ejected=false;public ClassId cls=ClassId.fighter;public int getInstanceId(){return instance;}public void setInstanceId(int v){instance=v;}public void setInsideZone(ZoneId z,boolean b){inside=b;}public boolean isGM(){return false;}public ClassId getClassId(){return cls;}public void sendMessage(String s){}public void sendPacket(Object p){}public void teleToLocation(TeleportWhereType t){ejected=true;}public void stopPvPFlag(){stops++;flag=0;}public void updatePvPFlag(int v){flag=v;}public void updatePvPStatus(){normalTimerStarts++;flag=1;}}''')
orion=ROOT/'external/orion/L2jOrion_SourceCode/src/l2jorion/game/model/zone/type/L2RandomZone.java'
copy(orion,'l2jorion/game/model/zone/type/L2RandomZone.java')

put('ReviewHarness.java','''import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.zone.type.FlagPvPZone;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import l2jorion.game.model.zone.type.L2RandomZone;
import l2jorion.game.model.actor.instance.L2PcInstance;
import l2jorion.game.model.base.ClassId;
public class ReviewHarness {
 static class N extends FlagPvPZone{N(int id){super(id);}void enter(Creature c){onEnter(c);}void exit(Creature c){onExit(c);}}
 static class O extends L2RandomZone{O(){super(1);}void enter(l2jorion.game.model.L2Character c){onEnter(c);}void exit(l2jorion.game.model.L2Character c){onExit(c);}}
 static int checks=0;static void check(boolean b,String s){if(!b)throw new AssertionError(s);checks++;System.out.println("PASS "+s);}
 public static void main(String[] args){
  N n=new N(1);Player p=new Player();n.enter(p);check(p.flag==1,"Mobius entering sets flag");
  n.exit(p);check(p.flag==0,"Mobius leaving clears flag immediately");
  p.flag=1;n.onDieInside(p);check(p.flag==0,"Mobius death clears flag via exit");
  n.onReviveInside(p);check(p.flag==1,"Mobius revive sets flag");
  N second=new N(2);second.enter(p);n.exit(p);check(p.flag==0,"Mobius overlapping-zone exit has no ownership guard");
  n.enter(p);p.until=1;PvpFlagTaskManager.getInstance().add(p);PvpFlagTaskManager.getInstance().run();check(p.flag==0,"Mobius existing expired combat timer can clear flag while inside");
  O o=new O();o.setParameter("autoPvpFlag","true");L2PcInstance q=new L2PcInstance();
  o.enter(q);check(!q.inside && q.flag==0,"Orion inactive zone ignores entry");
  o.setActiveZone(true);q.instance=0;o.enter(q);check(!q.inside && q.flag==0,"Orion entry requires configured instance already assigned");
  q.instance=3051;o.enter(q);check(q.inside && q.flag==1 && q.stops==1,"Orion entry stops old flag task and sets forced flag");
  o.exit(q);check(q.instance==0 && !q.inside && q.normalTimerStarts==1,"Orion geometric exit immediately resets instance and requests normal flag timer");
  L2PcInstance healer=new L2PcInstance();healer.cls=ClassId.cardinal;o.enter(healer);check(healer.ejected,"Orion healer restriction ejects cardinal when enabled");
  o.onDieInside(q);o.onReviveInside(q);check(q.instance==0 && q.normalTimerStarts==1,"Orion death/revive callbacks perform no action");
  O empty=new O();boolean rejected=false;try{empty.getLoc();}catch(RuntimeException e){rejected=true;}check(rejected,"Orion empty spawn list fails at selection");
  o.setParameter("locs","10,20,30;40,50,60;");check(o.getLoc().x()==10,"Orion configured spawn list parses trailing separator");
  boolean centerMissing=false;try{o.getCenterLoc();}catch(IndexOutOfBoundsException e){centerMissing=true;}check(centerMissing,"Orion fence center missing fails at access");
  System.out.println("TOTAL "+checks);
 }
}''')
java_files=list(SRC.rglob('*.java'))
classes=OUT/'classes';classes.mkdir(exist_ok=True)
r=subprocess.run([str(JDK/'javac.exe'),'-encoding','UTF-8','-d',str(classes),*[str(p) for p in java_files]],capture_output=True,text=True)
(OUT/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8')
if r.returncode:raise RuntimeError('Harness compile failed; see compile.log')
r=subprocess.run([str(JDK/'java.exe'),'-cp',str(classes),'ReviewHarness'],capture_output=True,text=True)
(OUT/'behavior-results.txt').write_text(r.stdout+r.stderr,encoding='utf-8');print(r.stdout)
if r.returncode:raise RuntimeError('Behavior check failed')

# Compile the original Lisvus class against a minimal declared API, preserving the published spelling.
lis=OUT/'lisvus-src';lis.mkdir(exist_ok=True)
patch=next(OUT.glob('lisvus-*.patch')).read_text()
original='\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
files={
'net/sf/l2j/gameserver/model/zone/type/L2FlagZone.java':original,
'net/sf/l2j/gameserver/model/L2Character.java':'package net.sf.l2j.gameserver.model;public class L2Character {}',
'net/sf/l2j/gameserver/model/actor/instance/L2PcInstance.java':'package net.sf.l2j.gameserver.model.actor.instance;public class L2PcInstance extends net.sf.l2j.gameserver.model.L2Character {public void updatePvPFlag(int x){}public void sendMessage(String x){}public void broadcastUserInfo(){}}',
'net/sf/l2j/gameserver/model/zone/L2ZoneSpawn.java':'package net.sf.l2j.gameserver.model.zone;import net.sf.l2j.gameserver.model.L2Character;public abstract class L2ZoneSpawn {public L2ZoneSpawn(int x){}protected abstract void onEnter(L2Character c);protected abstract void onExit(L2Character c);}'
}
for rel,text in files.items():p=lis/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
lisclasses=OUT/'lisvus-classes';lisclasses.mkdir(exist_ok=True)
r=subprocess.run([str(JDK/'javac.exe'),'-encoding','UTF-8','-d',str(lisclasses),*[str(p) for p in lis.rglob('*.java')]],capture_output=True,text=True)
(OUT/'lisvus-compile.log').write_text(r.stdout+r.stderr,encoding='utf-8')
typo_observed=r.returncode!=0 and 'updatetPvPFlag' in r.stderr
assert typo_observed,'Expected published typo not reproduced'
print('Confirmed Lisvus compile failure at updatetPvPFlag with declared updatePvPFlag API')

# Check source configurations: geometry only, no geodata or render claims.
xml=ROOT/'external/orion/L2jOrion_Datapack/game/data/xml/zones/RandomZone.xml'
def inside(x,y,poly):
    hit=False;j=len(poly)-1
    for i in range(len(poly)):
        a,b=poly[i],poly[j]
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
        j=i
    return hit
zones=[]
for z in ET.parse(xml).getroot().findall('zone'):
    s={v.attrib['name']:v.attrib['val'] for v in z.findall('stat')};poly=[(int(n.attrib['X']),int(n.attrib['Y'])) for n in z.findall('node')]
    locs=[tuple(map(int,p.split(','))) for p in s['locs'].split(';') if p]
    invalid=[p for p in locs if not inside(p[0],p[1],poly) or not int(z.attrib['minZ'])<=p[2]<=int(z.attrib['maxZ'])]
    zones.append({'name':z.attrib['name'],'id':int(s['id']),'seconds':int(s['time']),'spawn_count':len(locs),'outside_polygon_or_z':invalid})
ids=[z['id'] for z in zones]
results={'scope':'Real original zone classes and Mobius flag task, with test doubles for engine/player APIs. No live server, no real client or geodata tests. Orion normal timer is a recorded stub call, not the real Orion Player implementation. Lisvus compile failure uses declared minimal updatePvPFlag API, not a full Lisvus build.','behavior_checks':15,'lisvus_typo_compile_failure_reproduced':typo_observed,'zones':zones,'orion_ids_contiguous_1_to_count':sorted(ids)==list(range(1,len(ids)+1)),'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [orion,native/'org/l2jmobius/gameserver/entity/zone/type/FlagPvPZone.java',native/'org/l2jmobius/gameserver/taskmanagers/PvpFlagTaskManager.java',xml]]}
(OUT/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps({'zones':zones,'ids_contiguous':results['orion_ids_contiguous_1_to_count']},indent=2))
