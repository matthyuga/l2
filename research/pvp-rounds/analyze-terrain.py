from pathlib import Path
import csv,json,collections
s=Path(__file__).resolve().parent
rows=list(csv.DictReader((s/'terrain.csv').open()))
for name,minz,maxz in [('primeval',-3700,-2700),('saints',-4200,-2200)]:
    nodes={(int(r['x']),int(r['y'])):r for r in rows if r['map']==name and minz<int(r['z'])<maxz}
    seen=set();components=[]
    for point in nodes:
        if point in seen:continue
        stack=[point];seen.add(point);comp=[]
        while stack:
            x,y=stack.pop();comp.append((x,y))
            for q,valid in [((x+256,y),nodes[(x,y)]['east']=='1'),((x,y+256),nodes[(x,y)]['south']=='1'),((x-256,y),nodes.get((x-256,y),{}).get('east')=='1'),((x,y-256),nodes.get((x,y-256),{}).get('south')=='1')]:
                if valid and q in nodes and q not in seen:seen.add(q);stack.append(q)
        components.append(comp)
    components.sort(key=len,reverse=True)
    for comp in components[:2]:
        xs=[p[0] for p in comp];ys=[p[1] for p in comp]
        print(name,'component',len(comp),'bounds',min(xs),max(xs),min(ys),max(ys))
    # Rank 4096 x 4096 candidate areas by connected, traversable coverage.
    comp=set(components[0]);candidates=[]
    for x,y in comp:
        square={(xx,yy) for xx in range(x,x+4097,256) for yy in range(y,y+4097,256)}
        valid=square&comp
        candidates.append((len(valid),x,y))
    for count,x,y in sorted(candidates,reverse=True)[:6]:
        center=min(comp,key=lambda p:(p[0]-x-2048)**2+(p[1]-y-2048)**2)
        print('candidate',count,'of 289',x,x+4096,y,y+4096,'spawn',center,int(nodes[center]['z']))
