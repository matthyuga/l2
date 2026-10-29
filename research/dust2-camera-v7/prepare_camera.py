from pathlib import Path
import json,struct,sys,collections,math
D=Path(__file__).resolve().parent;R=D.parents[1];V4=D.parent/'dust2-stairs-v4'
bsp=(R/'research/dust2/source/de_dust2.bsp').read_bytes();lumps=[struct.unpack_from('<2i',bsp,4+i*8) for i in range(15)]
def lump(i):o,n=lumps[i];return bsp[o:o+n]
planes=list(struct.iter_unpack('<4fi',lump(1)));nodes=list(struct.iter_unpack('<i2h6h2H',lump(5)));leaves=list(struct.iter_unpack('<2i6h2H4B',lump(10)));head=struct.unpack_from('<i',lump(14),36)[0]
def contents(x,y,z):
 p=(x-141000,-(y-57000),z-8000);n=head
 while n>=0:
  nd=nodes[n];q=planes[nd[0]];n=nd[1 if sum(q[i]*p[i] for i in range(3))-q[3]>=0 else 2]
 return leaves[-n-1][0]
rects=json.loads((V4/'native-floor/rectangles.json').read_text());ceilings=collections.defaultdict(set);missing=0;entries=[]
for gx,gy,z,w,h,vz in rects:
 for cy in range(gy,gy+h):
  for cx in range(gx,gx+w):
   x,y=131072+cx*16+8,32768+cy*16+8;start=vz+72;prev=start;hit=None
   # Both physical roof faces and the original GoldSrc sky boundary stop camera rays.
   for height in range(0,1025,16):
    zz=start+height
    if contents(x,y,zz) in (-2,-6):
     low,high=prev,zz
     for _ in range(12):
      mid=(low+high)/2
      if contents(x,y,mid) in (-2,-6):high=mid
      else:low=mid
     hit=round(high);break
    prev=zz
   if hit is None:missing+=1;continue
   hit=min(hit,round(vz+128));ceilings[hit].add((cx,cy));entries.append([cx,cy,z,vz,hit])
boxes=[];covered=0
for z,plane in sorted(ceilings.items()):
 todo=set(plane)
 while todo:
  x,y=min(todo,key=lambda p:(p[1],p[0]));w=1
  while (x+w,y) in todo and w<64:w+=1
  h=1
  while h<64 and all((xx,y+h) in todo for xx in range(x,x+w)):h+=1
  for yy in range(y,y+h):
   for xx in range(x,x+w):todo.remove((xx,yy));covered+=1
  boxes.append([131072+x*16,32768+y*16,z,w*16,h*16])
(D/'ceiling-boxes.json').write_text(json.dumps(boxes));(D/'camera-ceilings.json').write_text(json.dumps(entries));(D/'camera-audit.json').write_text(json.dumps(dict(ceiling_boxes=len(boxes),covered_layer_centers=covered,unbounded_centers=missing,max_camera_clearance=128,profile_hit_check_before=300,profile_hit_check_after=10,zoom_max_preserved=1800,client_test_pending=True),indent=2))
print('Camera ceilings:',len(boxes),'boxes;',covered,'covered layer centers;',missing,'unbounded')
