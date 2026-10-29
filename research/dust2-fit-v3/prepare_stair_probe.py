import pathlib,sys,json,collections,random
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Reader
r=Reader((D/'stage/Geodata/24_19.l2j').read_bytes());cells={};decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:
   z=r.num('h');vals=[[((z<<1)&0xfff0)|15]]*64
  else:
   vals=[]
   for _ in range(64):
    n=1 if ty==1 else r.num('B');vals.append([r.num('H') for _ in range(n)])
  for i,vs in enumerate(vals):
   cx,cy=divmod(i,8);x,y=bx*8+cx,by*8+cy
   if not(137000<131072+x*16+8<145000 and 52500<32768+y*16+8<63000):continue
   out=[(decode(v),v&15) for v in vs if 7500<decode(v)<8850]
   if out:cells[x,y]=out
rects=json.loads((D/'native-floor/rectangles.json').read_text());seen={(x,y,z) for gx,gy,z,w,h,*rest in rects for y in range(gy,gy+h) for x in range(gx,gx+w)};pairs=[]
for x,y,z in sorted(seen):
 n=next(n for h,n in cells[x,y] if h==z)
 for dx,dy,bit in [(1,0,1),(-1,0,2),(0,1,4),(0,-1,8)]:
  if not n&bit:continue
  for nz,_ in cells.get((x+dx,y+dy),[]):
   if 0<nz-z<=16 and (x+dx,y+dy,nz) in seen:pairs.append([131072+x*16+8,32768+y*16+8,z,131072+(x+dx)*16+8,32768+(y+dy)*16+8,nz])
assert len(pairs)>100;random.seed(190);sample=random.sample(pairs,min(192,len(pairs)))
text=(D/'Dust2Smoke.java').read_text();needle='out.append("open_edges_verified="';pos=text.index(needle)
code='int[][] stairs={'+','.join('{'+','.join(map(str,p))+'}' for p in sample)+'};\nfor(int[] e:stairs)if(!geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Ascending stair blocked "+java.util.Arrays.toString(e));\nout.append("ascending_stair_samples="+stairs.length+"\\n");\n'
text=text[:pos]+code+text[pos:];(D/'Dust2Smoke.java').write_text(text)
(D/'stair-audit.json').write_text(json.dumps(dict(ascending_connections=len(pairs),sampled=len(sample),rises=sorted(set(p[5]-p[2] for p in pairs)),previous_goldsrc_scale=1.5,new_goldsrc_scale=.625,reference_goldsrc_hull_height=72,scaled_hull_height=45,source='https://github.com/ValveSoftware/halflife/blob/master/dlls/util.h'),indent=2));print('Prepared',len(sample),'server ascent samples from',len(pairs),'ascending connections')
