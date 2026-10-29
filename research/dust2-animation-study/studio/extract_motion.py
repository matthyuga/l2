"""Read-only Unity source extraction, transforms sampled at original frame times."""
import UnityPy, json, math, struct, bisect, hashlib, argparse, copy, zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=Path(r'K:\JUEGOS\KOIKATSU 22\abdata\studio\anime\00.unity3d')
RIG=Path(r'K:\JUEGOS\KOIKATSU 22\abdata\chara\oo_base.unity3d')

def vec(v,keys): return [v[k] for k in keys]
def extract_rig():
    env=UnityPy.load(str(RIG)); objects={o.path_id:o for o in env.objects}
    root=objects[8737511382815108191].read_typetree()
    avatar=objects[8543214252501933291].read_typetree()
    tos=dict(avatar['m_TOS']); hashes={v:k for k,v in tos.items()}
    bones=[]
    def visit(t,path,parent):
        go=objects[t['m_GameObject']['m_PathID']].read_typetree()
        idx=len(bones)
        hashvalue=zlib.crc32(path.encode('utf-8'))
        if path in hashes: assert hashvalue==hashes[path]
        bones.append(dict(name=go['m_Name'],path=path,parent=parent,hash=hashvalue,rest=dict(position=vec(t['m_LocalPosition'],'xyz'),rotation=vec(t['m_LocalRotation'],'xyzw'),scale=vec(t['m_LocalScale'],'xyz'))))
        for pp in t['m_Children']:
            child=objects[pp['m_PathID']].read_typetree();name=objects[child['m_GameObject']['m_PathID']].read().m_Name
            visit(child,('/' if path else '').join([path,name]) if path else name,idx)
    visit(root,'',-1)
    tos.update({b['hash']:b['path'] for b in bones})
    return bones,tos

def parse_stream(stream):
    raw=struct.pack('<%dI'%len(stream['data']),*stream['data']); offset=0
    curves=[[] for _ in range(stream['curveCount'])];frame_times=[]
    while offset<len(raw):
        time,n=struct.unpack_from('<fI',raw,offset);offset+=8;frame_times.append(time)
        for _ in range(n):
            index,*coeff=struct.unpack_from('<I4f',raw,offset);offset+=20
            curves[index].append((time,coeff))
    assert offset==len(raw)
    return curves,frame_times

def decode_clip(obj,bones,tos):
    d=obj.read_typetree(); c=d['m_MuscleClip']['m_Clip']['data']; muscle=d['m_MuscleClip']
    streamed,streamtimes=parse_stream(c['m_StreamedClip']);dense=c['m_DenseClip'];const=c['m_ConstantClip']['data']
    ns=len(streamed); nd=dense['m_CurveCount']; total=ns+nd+len(const)
    assert all(b['typeID']==4 and b['attribute'] in [1,2,3] for b in d['m_ClipBindingConstant']['genericBindings'])
    bonehash={b['hash']:i for i,b in enumerate(bones) if b['hash'] is not None}
    bindings=[];index=0;unmatched=[]
    for b in d['m_ClipBindingConstant']['genericBindings']:
        attr=b['attribute'];width=4 if attr==2 else 3
        target=bonehash.get(b['path']); bindings.append((target,attr,index,width))
        if target is None:unmatched.append(dict(hash=b['path'],path=tos.get(b['path']),attribute=attr))
        index+=width
    assert index==total,(index,total)
    times_by_curve=[[k[0] for k in keys] for keys in streamed]
    def values_at(t):
        vals=[]
        for keys,times in zip(streamed,times_by_curve):
            j=bisect.bisect_right(times,t)-1
            assert j>=0
            kt,co=keys[j];dt=t-kt
            # Each Unity streamed key stores a cubic polynomial in dt.
            value=((co[0]*dt+co[1])*dt+co[2])*dt+co[3] if math.isfinite(kt) else co[3]
            vals.append(value)
        fi=(t-dense['m_BeginTime'])*dense['m_SampleRate'];lo=max(0,min(dense['m_FrameCount']-1,int(math.floor(fi+1e-6))));hi=min(lo+1,dense['m_FrameCount']-1);alpha=max(0,min(1,fi-lo))
        vals.extend(dense['m_SampleArray'][lo*nd+k]*(1-alpha)+dense['m_SampleArray'][hi*nd+k]*alpha for k in range(nd))
        vals.extend(const)
        return vals
    fps=d['m_SampleRate']; duration=muscle['m_StopTime']-muscle['m_StartTime']; frames=[];normerrors=[]
    for f in range(round(duration*fps)+1):
        t=min(duration,f/fps); vals=values_at(muscle['m_StartTime']+t);transforms=[copy.deepcopy(b['rest']) for b in bones]
        for target,attr,index,width in bindings:
            if target is None:continue
            key={1:'position',2:'rotation',3:'scale'}[attr];v=vals[index:index+width]
            assert all(math.isfinite(x) for x in v)
            if attr==2:
                n=math.sqrt(sum(x*x for x in v));normerrors.append(abs(n-1))
                assert n>0.5 and n<1.5,(d['m_Name'],target,n)
                v=[x/n for x in v]
            transforms[target][key]=v
        frames.append(dict(time=t,transforms=transforms))
    return dict(fps=fps,duration_seconds=duration,coordinate_system='Unity left-handed X right Y up Z forward, metres; quaternion xyzw',bones=bones,frames=frames,source=dict(clip_name=d['m_Name'],clip_path_id=obj.path_id,bundle=str(SOURCE),bundle_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),rig_bundle=str(RIG),rig_root='p_cf_body_bone',rig_avatar='cf_body_00Avatar',rig_sha256=hashlib.sha256(RIG.read_bytes()).hexdigest()),validation=dict(bindings=len(bindings),matched_bindings=len(bindings)-len(unmatched),unmatched_bindings=unmatched,streamed_curves=ns,dense_curves=nd,constant_scalars=len(const),curve_scalar_total=total,max_quaternion_norm_error=max(normerrors),stream_frames=len(streamtimes),sample_count=len(frames),limitations=['No runtime CharaStudio IK, constraints or look-at evaluated.','Source movements require artistic adaptation for bomb-manipulation choreography.']))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--clip',default='mc_m_squat_00_00_01');args=ap.parse_args()
    bones,tos=extract_rig();e=UnityPy.load(str(SOURCE));obj=next(o for o in e.objects if o.type.name=='AnimationClip' and o.read().m_Name==args.clip)
    result=decode_clip(obj,bones,tos);out=HERE/(args.clip+'.motion.json');out.write_text(json.dumps(result,separators=(',',':')),encoding='utf-8');print(out);print(json.dumps({k:v for k,v in result['validation'].items() if k!='unmatched_bindings'},indent=2))
