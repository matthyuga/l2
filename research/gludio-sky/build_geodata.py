"""Add mesh-derived high-altitude layers; preserve all old lower-world layers."""
from package_tools import *
import json,collections,hashlib,math
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'))
from geolib.meshes import MeshLibrary,actor_matrix,transform
from geolib.generate import _prep_geometry,_column,_span_layers,_wall_between
D=pathlib.Path(__file__).resolve().parent;audit=json.loads((D/'build-audit.json').read_text())
lib=MeshLibrary(str(D/'stage/StaticMeshes'));triangles=[];bounds=[]
for a in audit['placed']:
    name=a['mesh'].split('.')[-1];mesh=lib.get('HGGludioSky_S',name);assert mesh,(name,lib.failed)
    verts,tris=mesh;world=transform(verts,actor_matrix(a['rotation'],a['scale'],a['scale3d']),a['location'])
    bounds.append(dict(mesh=name,verts=len(verts),triangles=len(tris),bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]))
    triangles.extend(tuple((world[j][0],world[j][1],world[j][2]+43.35) for j in t) for t in tris)
print('Preparing',len(triangles),'collision triangles',flush=True)
west,north=131072,32768
fc,grid,walls,wgrid=_prep_geometry(triangles,west,north)
print('Raycasting',len(grid),'candidate cells',len(walls),'walls',flush=True)
layers={}
for cell,idx in grid.items():
    gy,gx=divmod(cell,2048);fl,ce=_column(west+gx*16+8,north+gy*16+8,idx,fc)
    ls=_span_layers(fl,ce,[])
    if ls:layers[cell]=ls
print('Computing edges for',len(layers),'cells',flush=True)
encoded={}
for cell,ls in layers.items():
    gy,gx=divmod(cell,2048);px,py=west+gx*16+8,north+gy*16+8;out=[]
    for z in ls:
        n=0
        for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
            nc=(gy+dy)*2048+gx+dx
            # Close unsupported edges rather than letting players walk off the island.
            if not any(-96<=nz-z<=24 for nz in layers.get(nc,[])):continue
            wallids=set(wgrid.get(cell,[]))|set(wgrid.get(nc,[]))
            if wallids and _wall_between(px,py,px+dx*16,py+dy*16,z,wallids,walls):continue
            n|=bit
        out.append(((z<<1)&0xfff0)|n)
    encoded[cell]=out

source=ROOT/'server/game/data/geodata/24_19.l2j';b=source.read_bytes();r=Reader(b);result=bytearray();changed=0;oldlayers=0
for bx in range(256):
    for by in range(256):
        start=r.p;ty=r.num('B');cells=[]
        if ty==0:
            z=r.num('h');cells=[[((z<<1)&0xfff0)|15] for _ in range(64)]
        elif ty in (1,2):
            for _ in range(64):
                n=1 if ty==1 else r.num('B');assert 1<=n<=125
                cells.append([r.num('H') for _ in range(n)])
        else:raise AssertionError(ty)
        additions=[encoded.get((by*8+cy)*2048+(bx*8+cx),[]) for cx in range(8) for cy in range(8)]
        if not any(additions):result+=b[start:r.p];continue
        changed+=1;result.append(2)
        for original,new in zip(cells,additions):
            assert all(((v if v<32768 else v-65536)&~15)>>1 < 7000 for v in original),'Unexpected high-altitude baseline layer'
            values=original+new;assert len(values)<=125
            values.sort(key=lambda v:(v if v<32768 else v-65536)&~15,reverse=True)
            result.append(len(values));result+=struct.pack('<'+'H'*len(values),*values);oldlayers+=len(original)
assert b[r.p:] in (b'',b'Kuoja'),('Unrecognized baseline footer',b[r.p:])
result+=b[r.p:]
dest=D/'stage/Geodata/24_19.l2j';dest.parent.mkdir(exist_ok=True);dest.write_bytes(result)

def sample(x,y,z):
    cell=((y-north)//16)*2048+(x-west)//16;vals=encoded.get(cell,[])
    return min([(((v if v<32768 else v-65536)&~15)>>1,v&15) for v in vals],key=lambda q:abs(q[0]-z)) if vals else None
spawn=sample(149000,46700,12000);assert spawn and abs(spawn[0]-12000)<100,spawn
assert spawn[1]!=0,spawn
seed=((46700-north)//16)*2048+(149000-west)//16;seen={(seed,spawn[0])};queue=collections.deque(seen)
while queue:
    cell,z=queue.popleft();gy,gx=divmod(cell,2048)
    val=min(encoded[cell],key=lambda v:abs((((v if v<32768 else v-65536)&~15)>>1)-z));n=val&15
    for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
        if not n&bit:continue
        nc=(gy+dy)*2048+gx+dx
        for v in encoded.get(nc,[]):
            h=((v if v<32768 else v-65536)&~15)>>1
            if -96<=h-z<=24 and (nc,h) not in seen:seen.add((nc,h));queue.append((nc,h))
assert len(seen)>1200,len(seen)
report=dict(triangles=len(triangles),bounds=bounds,new_cells=len(encoded),changed_blocks=changed,preserved_lower_layers_in_changed_blocks=oldlayers,source_sha256=hashlib.sha256(b).hexdigest(),bytes=len(result),spawn=[149000,46700,spawn[0]+24],spawn_floor=spawn[0],spawn_nswe=spawn[1],reachable_layers=len(seen),limits='Mesh-derived prototype. No cloud collision. All original lower layers retained; flat block heights quantized to native 8-unit multilayer precision when promoted.')
(D/'geodata-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='bounds'},indent=2))
