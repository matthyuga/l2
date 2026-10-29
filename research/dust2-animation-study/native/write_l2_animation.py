"""Offline UE2 Lineage2 MeshAnimation writer. Input PSA or local-space JSON.
No game installation is written. Native local transforms use L2/ActorX axes.
"""
import argparse,struct,json,math,uuid,pathlib,hashlib
P=struct.pack

def ci(v):
    sign=128 if v<0 else 0; v=abs(v); b=(v&63)|sign; v>>=6
    out=bytearray([b|(64 if v else 0)])
    while v:
        b=v&127; v>>=7; out.append(b|(128 if v else 0))
    return bytes(out)

def chunks(path):
    d=pathlib.Path(path).read_bytes(); pos=0; out={}
    while pos<len(d):
        name,flags,size,count=struct.unpack_from('<20s3i',d,pos);pos+=32
        out[name.rstrip(b'\0').decode()]=(size,count,d[pos:pos+size*count]);pos+=size*count
    assert pos==len(d)
    return out

def psa(path,sequence=None):
    c=chunks(path); size,count,d=c['BONENAMES']; assert size==120
    bones=[]
    for i in range(count):
        name,flags,children,parent=struct.unpack_from('<64s3i',d,i*size)
        bones.append(dict(name=name.rstrip(b'\0').decode(),parent=parent))
    size,nseq,d=c['ANIMINFO']; assert size==168
    seqs=[]
    for i in range(nseq):
        q=struct.unpack_from('<64s64s4i3f3i',d,i*size)
        seqs.append(dict(name=q[0].rstrip(b'\0').decode(),bones=q[2],fps=q[8],first=q[10],frames=q[11]))
    s=next((s for s in seqs if s['name']==sequence),seqs[0] if sequence is None else None);assert s,'Unknown PSA sequence'
    size,nkeys,k=c['ANIMKEYS'];assert size==32
    frames=[]
    for f in range(s['frames']):
        positions=[];rotations=[]
        for b in range(count):
            q=struct.unpack_from('<8f',k,((s['first']+f)*count+b)*32)
            positions.append(q[:3]);rotations.append(q[3:7])
        frames.append(dict(positions=positions,rotations=rotations))
    return dict(bones=bones,fps=s['fps'],frames=frames,name=s['name'])

def generate(src,out,name):
    bones=src['bones']; frames=src['frames']; fps=src['fps']; assert bones and frames and fps>0
    for f in frames:
        assert len(f['positions'])==len(bones)==len(f['rotations'])
        for p,q in zip(f['positions'],f['rotations']):
            assert len(p)==3 and len(q)==4 and all(math.isfinite(x) for x in (*p,*q))
            assert abs(sum(x*x for x in q)-1)<0.01,'Non-unit quaternion'
    names=list(dict.fromkeys(['None','Core','Package','Class','Engine','MeshAnimation','Dust2Motion',name]+[b['name'] for b in bones]))
    nr=lambda n:ci(names.index(n))
    nametable=b''.join(ci(len(n)+1)+n.encode()+b'\0'+P('<I',0x70010) for n in names)
    # import 1 Engine (Core.Package), import 2 Engine.MeshAnimation (Core.Class)
    imports=nr('Core')+nr('Package')+P('<i',0)+nr('Engine')+nr('Core')+nr('Class')+P('<i',-1)+nr('MeshAnimation')
    refbones=ci(len(bones))+b''.join(nr(b['name'])+P('<Ii',0,b['parent']) for b in bones)
    def arr(values,nfmt):return ci(len(values))+b''.join(P('<'+nfmt,*v) if isinstance(v,(list,tuple)) else P('<'+nfmt,v) for v in values)
    motion=P('<3ffii',0,0,0,len(frames),0,0)+arr(list(range(len(bones))),'i')+ci(len(bones))
    for b in range(len(bones)):
        qs=[list(f['rotations'][b]) for f in frames];ps=[list(f['positions'][b]) for f in frames]
        # UModel ActorX export mirrors Y, conjugates W, for all bones.
        if src.get('from_psa'):
            ps=[[p[0],-p[1],p[2]] for p in ps]
            qs=[[q[0],-q[1],q[2],-q[3]] for q in qs]
        motion+=P('<I',0)+arr(qs,'4f')+arr(ps,'3f')+arr(list(range(len(frames))),'f')
    motion+=P('<I',0)+ci(0)*3 # empty RootTrack
    seq=P('<f',0)+nr(name)+ci(0)+P('<ii',0,len(frames))+ci(0)+P('<f',fps)
    seq+=P('<3i',0,0,0)+ci(0)+P('<2i',0,0) # Lineage sequence extension
    seq+=b'\0'+ci(0)+ci(0)+P('<2i',0,0)+ci(0) # FLineageUnk4
    prefix=nr('None')+P('<i',1)+refbones
    nameoff=64; importoff=nameoff+len(nametable); exportoff=importoff+len(imports)
    # Export table length depends on compact payload offset. Iterate to fixed point.
    dataoff=exportoff+20
    for _ in range(10):
        endmove=dataoff+len(prefix)+4+len(ci(1))+4+len(motion)
        payload=prefix+P('<i',endmove)+ci(1)+P('<i',endmove)+motion+ci(1)+seq
        export=ci(-2)+ci(0)+P('<i',0)+nr('Dust2Motion')+P('<I',0x70004)+ci(len(payload))+ci(dataoff)
        newoff=exportoff+len(export)
        if newoff==dataoff:break
        dataoff=newoff
    else:raise RuntimeError('Offset convergence failed')
    header=P('<IHH7I',0x9e2a83c1,123,30,1,len(names),nameoff,1,exportoff,2,importoff)+uuid.uuid5(uuid.NAMESPACE_OID,hashlib.sha256(nametable+imports+payload).hexdigest()).bytes_le+P('<3I',1,1,len(names))
    assert len(header)==64
    raw=header+nametable+imports+export+payload
    pathlib.Path(out).write_bytes(raw)
    return dict(output=str(out),sha256=hashlib.sha256(raw).hexdigest(),bones=len(bones),frames=len(frames),fps=fps,sequence=name,bytes=len(raw),data_offset=dataoff,lineage_move_end=endmove)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');ap.add_argument('--sequence');ap.add_argument('--skeleton',help='PSK with authoritative parent hierarchy');ap.add_argument('--name',default='Dust2PlantTest');a=ap.parse_args()
    if a.input.lower().endswith('.psa'):
        src=psa(a.input,a.sequence);src['from_psa']=True
    else:src=json.loads(pathlib.Path(a.input).read_text())
    if a.skeleton:
        size,count,d=chunks(a.skeleton)['REFSKELT'];assert size==120 and count==len(src['bones'])
        for i,b in enumerate(src['bones']):
            name,flags,children,parent=struct.unpack_from('<64s3i',d,i*size)
            assert name.rstrip(b'\0').decode()==b['name'],'PSK/animation bone order mismatch'
            b['parent']=parent
    print(json.dumps(generate(src,a.output,a.name),indent=2))
