"""Convert L2 material native blocks from Gracia license 37 to Interlude 28.

Layout: UEViewer UnMaterial2.h SerializeLineage2Material and UnTexture2.cpp.
Preserves tagged artistic properties and mip pixel bytes; discards compiled newer
shader metadata so Interlude can evaluate the retained native material graph.
"""
from package_tools import *

def skip_string(r):
    n=r.compact();r.read(abs(n)*(2 if n<0 else 1))

def convert_materials(pkg):
    assert pkg.version==123 and pkg.license==37
    count=0
    for e in pkg.exports:
        cl=pkg.ref(e['cl'])
        if cl in ['Core.Package','Engine.Palette']:continue
        assert cl.startswith('Engine.'),cl
        pkg.props(e);props_end=pkg.last_props_end;r=Reader(pkg.b,props_end)
        # FLineageShaderProperty (version <129): b1,b2,b3,b4, three ints,
        # eight color bytes, three fade ints, then dynamic stages.
        r.read(36)
        stages=r.compact();assert 0<=stages<1000,(e['name'],stages)
        for _ in range(stages):
            skip_string(r);n=r.compact();assert 0<=n<1000
            for _ in range(n):skip_string(r)
        skip_string(r);r.read(4) # ShaderCode and MaterialCodeVersion.
        native_start=r.p;native=pkg.b[native_start:e['offset']+e['size']]
        ptrs=[]
        if cl in ['Engine.Texture','Engine.Cubemap']:
            rr=Reader(native);n=rr.compact();assert 0<=n<=20,(e['name'],n)
            for _ in range(n):
                loc=rr.p;old=rr.num('i');size=rr.compact();rr.read(size)
                assert old==native_start+rr.p,(e['name'],old,native_start+rr.p)
                ptrs.append(loc);rr.read(10)
            assert rr.p==len(native),(e['name'],rr.p,len(native))
        else:assert not native,(e['name'],cl,len(native))
        props=pkg.b[e['offset']:props_end]
        def converted(new_offset,props=props,native=native,ptrs=ptrs,native_start=native_start):
            raw=bytearray(native);delta=new_offset+len(props)+4-native_start
            for pos in ptrs:struct.pack_into('<i',raw,pos,struct.unpack_from('<i',raw,pos)[0]+delta)
            return props+b'\0'*4+bytes(raw)
        pkg.replace(e,converted);count+=1
    return count

if __name__=='__main__':
    import json,uuid
    from cloud_material import add_cloud_material
    D=pathlib.Path(__file__).resolve().parent;SRC=ROOT/'research/airships/gracia-assets/Textures';report=[]
    names={'glacia_kserth_t','glacia_fieldobj_t','l2_ship_l01_t','bereth_t','spirit_island_v_t','steel_castle_t','steel_castleinside_t','hellbound_01_t','t_hellbound'}
    sources={p.stem.lower():p for p in SRC.glob('*.utx') if p.stem.lower() in names}
    mapping={k:('HGGludioSky_T' if k=='glacia_kserth_t' else 'HGGludio_'+p.stem) for k,p in sources.items()}
    for key,source in sources.items():
        p=Edit(source);p.data[36:52]=uuid.uuid4().bytes
        for imp in p.imports:
            if not imp['outer'] and imp['name'].lower() in mapping:imp['name']=mapping[imp['name'].lower()];p.name(imp['name'])
        count=convert_materials(p)
        if key=='glacia_kserth_t':
            add_cloud_material(p)
        path=p.save(D/'stage/Textures'/(mapping[key]+'.utx'),license=28)
        report.append(dict(package=path.name,converted_materials=count))
    (D/'material-conversion.json').write_text(json.dumps(report,indent=2));print(report)
