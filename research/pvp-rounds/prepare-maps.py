from pathlib import Path
import csv,json,collections
s=Path(__file__).resolve().parent
rows=list(csv.DictReader((s/'terrain.csv').open()))
maps=[dict(id='elven',name='Elven Village',bounds=[42000,49200,46600,54000,-3800,-2000],spawns=[[45150,52100,-2792],[43673,49683,-3048],[47401,51764,-2992],[45443,48357,-3056]])]
for key,name,bounds in [('primeval','Primeval Isle - Playa',[4352,8448,-22064,-17968,-3750,-2700]),('saints','Valley of Saints',[83216,87312,-85952,-81856,-4200,-2200])]:
    x1,x2,y1,y2,z1,z2=bounds
    grid={(int(r['x']),int(r['y'])):r for r in rows if r['map']==key and x1<int(r['x'])<x2 and y1<int(r['y'])<y2 and z1<int(r['z'])<z2}
    center=min(grid,key=lambda p:(p[0]-(x1+x2)/2)**2+(p[1]-(y1+y2)/2)**2)
    seen={center};stack=[center]
    while stack:
        x,y=stack.pop()
        for q,valid in [((x+256,y),grid[(x,y)]['east']=='1'),((x,y+256),grid[(x,y)]['south']=='1'),((x-256,y),grid.get((x-256,y),{}).get('east')=='1'),((x,y-256),grid.get((x,y-256),{}).get('south')=='1')]:
            if valid and q in grid and q not in seen:seen.add(q);stack.append(q)
    spawns=[center]
    for fraction in [(0.2,0.25),(0.8,0.25),(0.5,0.8)]:
        target=(x1+(x2-x1)*fraction[0],y1+(y2-y1)*fraction[1])
        spawns.append(min(seen,key=lambda p:(p[0]-target[0])**2+(p[1]-target[1])**2))
    maps.append(dict(id=key,name=name,bounds=bounds,spawns=[[x,y,int(grid[(x,y)]['z'])] for x,y in spawns],connected_grid_samples=len(seen),interior_grid_samples=len(grid),sample_spacing=256))
(s/'maps.json').write_text(json.dumps(maps,indent=2))
config=['# HELLGAMES PvP rooms. Duration is provisional and configurable.','RoundSeconds=1800','VoteLeadSeconds=300','VoteSeconds=60','FriendlyFire=false','Maps=elven,primeval,saints']
for m in maps:
    config += [f"{m['id']}.Name={m['name']}",f"{m['id']}.Bounds="+','.join(map(str,m['bounds'])),f"{m['id']}.Spawns="+';'.join(','.join(map(str,p)) for p in m['spawns'])]
(s/'PvpRooms.properties').write_text('\n'.join(config)+'\n')
print(json.dumps(maps,indent=2))
