"""Read GoldSrc IDST v10 using Valve's engine/studio.h layout; never executes models.
Exports all bodypart/submodel geometry in the bone default pose and skin family 0.
Units and right-handed Z-up coordinates are preserved. OBJ V reverses texture T.
"""
from pathlib import Path
import struct, json, hashlib, math, shutil
import numpy as np
from PIL import Image

SOURCE = Path(r'D:\juegos\cs1.6\cstrike\models')
ROOT = Path(__file__).resolve().parent

def export(name):
    src = SOURCE / (name + '.mdl')
    d = src.read_bytes()
    out = ROOT / name
    out.mkdir(exist_ok=True)
    shutil.copy2(src, out / src.name)
    def unpack(fmt, off):
        assert 0 <= off and off + struct.calcsize(fmt) <= len(d), (fmt, off)
        return struct.unpack_from(fmt, d, off)
    def integer(off): return unpack('<i', off)[0]
    def text(raw): return raw.split(b'\0')[0].decode('latin1')
    assert d[:4] == b'IDST' and integer(4) == 10 and integer(72) == len(d)
    nb, bi = unpack('<2i', 140)
    bones, globals_ = [], []
    for i in range(nb):
        off = bi + i * 112
        bn, parent = unpack('<32si', off)
        vals = unpack('<6f', off + 64)
        x,y,z,rx,ry,rz = vals
        sx,cx,sy,cy,sz,cz = math.sin(rx),math.cos(rx),math.sin(ry),math.cos(ry),math.sin(rz),math.cos(rz)
        # Valve AngleQuaternion/QuaternionMatrix equivalence: Rz * Ry * Rx.
        rot = np.array([[cy*cz,sx*sy*cz-cx*sz,cx*sy*cz+sx*sz],
                        [cy*sz,sx*sy*sz+cx*cz,cx*sy*sz-sx*cz],
                        [-sy,sx*cy,cx*cy]])
        local = np.eye(4); local[:3,:3] = rot; local[:3,3] = [x,y,z]
        assert parent < i
        glob = globals_[parent] @ local if parent >= 0 else local
        assert np.allclose(glob[:3,:3].T @ glob[:3,:3], np.eye(3))
        globals_.append(glob)
        bones.append(dict(name=text(bn), parent=parent, values=vals, global_matrix=glob.tolist()))
    nt, ti = unpack('<2i', 180)
    textures = []
    mtl = []
    for i in range(nt):
        tn, flags,w,h,pixels = unpack('<64s4i', ti + 80*i)
        assert 0 < w <= 4096 and 0 < h <= 4096
        palette_off = pixels+w*h
        assert palette_off+768 <= len(d)
        im = Image.frombytes('P',(w,h),d[pixels:palette_off])
        im.putpalette(d[palette_off:palette_off+768])
        filename = f'texture_{i}_{Path(text(tn)).stem}.png'
        im.convert('RGB').save(out / filename)
        textures.append(dict(name=text(tn),flags=flags,width=w,height=h,pixel_offset=pixels,file=filename))
        mtl.extend([f'newmtl tex_{i}', 'Kd 1 1 1', 'Ka 0.2 0.2 0.2', 'Ks 0 0 0', 'd 1', f'map_Kd {filename}', ''])
    (out / (name+'.mtl')).write_text('\n'.join(mtl))
    nsref, nsfamily, skinidx = unpack('<3i', 192)
    skins = [unpack('<'+str(nsref)+'h', skinidx+f*nsref*2) for f in range(nsfamily)]
    nbody, bodyidx = unpack('<2i',204)
    obj = [f'# GoldSrc {src.name}; default bone pose; native Z-up units',f'mtllib {name}.mtl']
    models=[]; allverts=[]; vcount=0; uvcount=0; ncount=0
    for b in range(nbody):
        bodyname, nmodels, base, modelidx = unpack('<64s3i', bodyidx+b*76)
        for m in range(nmodels):
            mn, typ, radius, nm, meshidx, nv, vbi, vi, nn, nbi, ni, ng, gi = unpack('<64sif10i',modelidx+m*112)
            verts=[]; normals=[]
            for k in range(nv):
                bone=d[vbi+k]; assert bone < nb
                v=globals_[bone] @ np.array([*unpack('<3f', vi+k*12),1.])
                verts.append(v[:3]); allverts.append(v[:3])
                obj.append('v '+' '.join(f'{a:.9g}' for a in v[:3]))
            for k in range(nn):
                bone=d[nbi+k]; assert bone < nb
                n=globals_[bone][:3,:3] @ np.array(unpack('<3f',ni+k*12))
                n=n/np.linalg.norm(n)
                normals.append(n)
                obj.append('vn '+' '.join(f'{a:.9g}' for a in n))
            modelstats=dict(name=text(mn),bodypart=text(bodyname),vertices=nv,normals=nn,meshes=[])
            for mesh in range(nm):
                expected, cmd, skinref, numnorms, normidx = unpack('<5i',meshidx+mesh*20)
                tex=skins[0][skinref]; tw=textures[tex]['width']; th=textures[tex]['height']
                obj.extend([f'g body_{b}_model_{m}_mesh_{mesh}',f'usemtl tex_{tex}'])
                triangles=0; facing=[]; streams=[]
                while True:
                    count=unpack('<h',cmd)[0]; cmd+=2
                    if count == 0: break
                    corners=[]
                    for k in range(abs(count)):
                        vp,np_,s,t = unpack('<4h',cmd);cmd+=8
                        assert 0 <= vp < nv and 0 <= np_ < nn
                        obj.append(f'vt {s/tw:.9g} {1-t/th:.9g}')
                        uvcount+=1
                        corners.append((vp+1+vcount,uvcount,np_+1+ncount,vp,np_))
                    streams.append(dict(mode='strip' if count>0 else 'fan',corners=abs(count)))
                    for k in range(2,abs(count)):
                        inds=(k-2,k-1,k) if count>0 and k%2==0 else ((k-1,k-2,k) if count>0 else (0,k-1,k))
                        # GoldSrc studio renderer uses clockwise front faces.
                        # OBJ uses counterclockwise, so reverse triangle winding.
                        cs=[corners[a] for a in reversed(inds)]
                        obj.append('f '+' '.join(f'{c[0]}/{c[1]}/{c[2]}' for c in cs))
                        a,bv,c=[verts[c[3]] for c in cs]
                        cross=np.cross(bv-a,c-a)
                        if np.linalg.norm(cross)>1e-9:
                            facing.append(float(np.dot(cross/np.linalg.norm(cross), np.mean([normals[c[4]] for c in cs],axis=0))))
                        triangles+=1
                assert triangles==expected,(triangles,expected)
                modelstats['meshes'].append(dict(texture=tex,triangles=triangles,commands=streams,min_face_normal_dot=min(facing,default=0),positive_face_normals=sum(x>0 for x in facing),nondegenerate_faces=len(facing)))
            vcount+=nv;ncount+=nn;models.append(modelstats)
    (out / (name+'.obj')).write_text('\n'.join(obj)+'\n')
    seqs=[]
    for q in range(integer(164)):
        off=integer(168)+q*176
        seqs.append(dict(name=text(unpack('<32s',off)[0]),frames=integer(off+56),group=integer(off+156)))
    arr=np.array(allverts)
    manifest=dict(source=str(src),sha256=hashlib.sha256(d).hexdigest(),bytes=len(d),magic='IDST',version=10,coordinates='Right-handed GoldSrc X/Y/Z, Z-up; native units, no recentering',pose='Default bone values, not decoded sequence deltas',bones=bones,textures=textures,skin_families=skins,models=models,sequences=seqs,bounds_min=arr.min(axis=0).tolist(),bounds_max=arr.max(axis=0).tolist(),dimensions=np.ptp(arr,axis=0).tolist(),format_source='https://github.com/ValveSoftware/halflife/blob/master/engine/studio.h',validation='All offsets bounds checked; bone parents and vertex/normal indices checked; transforms orthonormal; triangle counts equal each declared mesh count; source length equal header length')
    (out / 'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(name, 'vertices',vcount,'triangles',sum(x['triangles'] for m in models for x in m['meshes']),'dimensions',manifest['dimensions'])
    return manifest

if __name__ == '__main__':
    for name in ['w_c4','p_c4']:
        export(name)
