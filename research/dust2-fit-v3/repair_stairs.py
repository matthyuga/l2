"""Allow verified 20..32u Dust2 risers, retaining exact heights and native floors.
Only direction bits change. High platforms and solid walls are excluded by BSP.
"""
from pathlib import Path
import struct,json,sys,hashlib,collections
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import Reader
live=Path(sys.argv[1]) if len(sys.argv)>1 else R/'server/game/data/geodata/24_19.l2j';data=live.read_bytes();r=Reader(data);offsets={};decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:r.read(2);continue
  for cell in range(64):
   n=1 if ty==1 else r.num('B');x,y=bx*8+cell//8,by*8+cell%8
   for _ in range(n):
    off=r.p;v=r.num('H');z=decode(v)
    if 7500<z<8850:offsets[x,y,z]=(off,v)
bsp=(R/'research/dust2/source/de_dust2.bsp').read_bytes();lumps=[struct.unpack_from('<2i',bsp,4+i*8) for i in range(15)]
def lump(i):o,n=lumps[i];return bsp[o:o+n]
planes=list(struct.iter_unpack('<4fi',lump(1)));nodes=list(struct.iter_unpack('<i2h6h2H',lump(5)));leaves=list(struct.iter_unpack('<2i6h2H4B',lump(10)));head=struct.unpack_from('<i',lump(14),36)[0]
def solid(x,y,visual_z):
 p=(x-141000,-(y-57000),visual_z-8000);n=head
 while n>=0:
  nd=nodes[n];q=planes[nd[0]];n=nd[1 if sum(q[i]*p[i] for i in range(3))-q[3]>=0 else 2]
 return leaves[-n-1][0]==-2
rows=json.loads((D/'blocked-step-edges.json').read_text());changed=[];rejected=collections.Counter();out=bytearray(data)
for row in rows:
 x,y,z,tx,ty,tz,vz,tvz=row
 if tz-z>32 or tvz-vz>32 or tvz<=vz:rejected['too_high']+=1;continue
 dx=(tx-x)//16;dy=(ty-y)//16;bit={(1,0):1,(-1,0):2,(0,1):4,(0,-1):8}[dx,dy]
 # A standing body must clear the riser, wall and ceiling along the complete path.
 if any(solid(x+(tx-x)*f+(-dy)*lat,y+(ty-y)*f+dx*lat,tvz+h) for f in (0,.25,.5,.75,1) for lat in (-10.5,0,10.5) for h in (4,24,48,68)):
  rejected['body_obstructed']+=1;continue
 key=((x-131072)//16,(y-32768)//16,z);off,value=offsets[key]
 assert not value&bit;current=struct.unpack_from('<H',out,off)[0];struct.pack_into('<H',out,off,current|bit);changed.append(row)
assert changed,'No safe stair edges found'
assert len(out)==len(data)
for key,(off,_) in offsets.items():
 a,b=struct.unpack_from('<H',data,off)[0],struct.unpack_from('<H',out,off)[0]
 assert a&0xfff0==b&0xfff0,'A floor height changed'
(D/'stairs-repaired.l2j').write_bytes(out);(D/'stairs-repaired-edges.json').write_text(json.dumps(changed))
report=dict(before_sha256=hashlib.sha256(data).hexdigest(),after_sha256=hashlib.sha256(out).hexdigest(),edges_opened=len(changed),rises=dict(collections.Counter(row[5]-row[2] for row in changed)),rejected=dict(rejected),height_values_preserved=True,map_unchanged=True,client_test_pending=True)
(D/'stairs-repair-audit.json').write_text(json.dumps(report,indent=2));print(report)
code='''import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public class StairRepairProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception {
  var g=GeoEngine.getInstance();if(!g.reloadRegion(24,19))throw new IllegalStateException("Geo reload failed");
  int[][] edges=@EDGES@;StringBuilder out=new StringBuilder();int pass=0,fail=0;
  for(int[] e:edges){if(g.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))pass++;else{fail++;out.append("FAIL "+java.util.Arrays.toString(e)+"\\n");}}
  out.append("repaired_stair_edges="+edges.length+" pass="+pass+" fail="+fail+"\\n");Files.writeString(Path.of(dir,"stairs-repair-server.txt"),out);
  if(fail>0)throw new AssertionError("Repaired stairs still blocked: "+fail);
 }
}'''
code=code.replace('@EDGES@','{'+','.join('{'+','.join(map(str,e[:6]))+'}' for e in changed)+'}')
(D/'StairRepairProbe.java').write_text(code)
