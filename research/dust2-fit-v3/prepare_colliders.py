from pathlib import Path
import json
D=Path(__file__).resolve().parent;V2=D.parent/'dust2-scale-v2';g=json.loads((D/'geodata-audit.json').read_text());count=g['reachable_layers']
for sub in ['native-floor','native-walls']:
 for filename in ['build.py','verify.py']:
  s=(V2/sub/filename).read_text(encoding='utf-8').replace('HGDust2V2','HGDust2V3').replace('11914',str(count))
  s=s.replace('137000<x<144100 and 54500<y<62800','137000<x<145000 and 52500<y<63000')
  s=s.replace('137000<131072+gx*16+8<144100 and 54500<32768+gy*16+8<62800','137000<131072+gx*16+8<145000 and 52500<32768+gy*16+8<63000')
  if sub=='native-floor' and filename=='build.py':
   # Split geodata rectangles when their true rendered heights differ.
   s=s.replace('byz=collections.defaultdict(set)',"exact={(x,y,z):h for x,y,z,h in json.loads((BASE/'visual-floors.json').read_text())}; byz=collections.defaultdict(set)")
   s=s.replace('for x,y,z in seen:byz[z].add((x,y))','for x,y,z in seen:byz[(z,exact[x,y,z])].add((x,y))')
   s=s.replace('for z,plane in sorted(byz.items()):','for (z,visual_z),plane in sorted(byz.items()):')
   s=s.replace('rects.append((x,y,z,w,h))','rects.append((x,y,z,w,h,visual_z))')
   s=s.replace('(gx,gy,z,w,h) in enumerate(rects)','(gx,gy,z,w,h,visual_z) in enumerate(rects)')
   s=s.replace('z-43.35-hi[2]*sz','visual_z-hi[2]*sz')
  elif sub=='native-floor':
   s=s.replace('(gx,gy,z,w,h) in zip(actors,rects)','(gx,gy,z,w,h,visual_z) in zip(actors,rects)').replace('(z-43.35)','visual_z')
  elif sub=='native-walls':
   s=s.replace('for gx,gy,z,w,h in rects','for gx,gy,z,w,h,*rest in rects')
  p=D/sub/filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
print('Prepared exact-height native support builders:',count,'reachable layers')
