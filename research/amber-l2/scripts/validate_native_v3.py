import pathlib, struct, json, subprocess
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
reader=ROOT/'tools/umodel.exe'
mesh=pathlib.Path('E:/l2/animations/L2AmberNPCv3.ukx')

def dump(obj):
    text=subprocess.check_output([str(reader),'-path=E:/l2','-dump',str(mesh),obj],text=True,errors='replace')
    (ROOT/('reports/v3-native-'+obj+'.txt')).write_text(text,encoding='utf8')
    return text

body=dump('AmberBodyShader'); outfit=dump('AmberOutfitShader'); mesh_info=dump('AmberNPC')
assert 'LodCount = 1' in mesh_info
assert "SelfIllumination = Texture'AmberBody'" in body
assert 'SelfIllumination = None' in outfit
for shader in (body,outfit):
    assert 'ZWrite = true' in shader and 'AlphaTest = true' in shader and 'AlphaRef = 128' in shader
    assert 'OutputBlending = OB_Masked' in shader
for name in ('AmberBody','AmberOutfit'):
    original=Image.open(ROOT/('exports/textures/'+name+'.tga')).convert('RGBA')
    exported=Image.open(ROOT/('exports/installed-check/L2AmberNPCv3/Texture/'+name+'.tga')).convert('RGBA')
    assert original.size==exported.size and original.tobytes()==exported.tobytes()

psa=ROOT/'exports/installed-check/L2AmberMotionv3/MeshAnimation/FFighter_anim.psa'
sequences=[]
with psa.open('rb') as file:
    while header:=file.read(32):
        name,kind,size,count=struct.unpack('<20siii',header)
        if name.startswith(b'ANIMINFO'):
            for _ in range(count):
                record=file.read(size)
                sequences.append(record[:64].split(b'\0')[0].decode('ascii'))
        else: file.seek(size*count,1)
expected={'Wait_Hand','walk_hand','Run_Hand','AtkWait_Hand','atk01_Hand','Death_Hand','deathwait_Hand'}
assert expected.issubset(set(sequences)),expected-set(sequences)
report={'one_full_detail_lod':True,'texture_pixels_roundtrip':True,'trader_animation_names':sorted(expected),
        'alpha_test':128,'depth_write':True,'outfit_scene_lighting':True,'body_self_illumination':True,
        'in_game_validation_v3':False}
(ROOT/'reports/v3-native-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
