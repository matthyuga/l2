"""Verify the lighting-only revision against the already tested v3 assets."""
import pathlib, json, subprocess, hashlib
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
reader=ROOT/'tools/umodel.exe'
installed=pathlib.Path('E:/l2/animations/L2AmberNPCv4.ukx')

def dump(obj):
    text=subprocess.check_output([str(reader),'-path=E:/l2','-dump',str(installed),obj],text=True,errors='replace')
    (ROOT/('reports/v4-native-'+obj+'.txt')).write_text(text,encoding='utf8')
    return text

for name in ('AmberBody','AmberOutfit'):
    shader=dump(name+'Shader')
    assert "SelfIllumination = Texture'"+name+"'" in shader
    assert 'ZWrite = true' in shader and 'AlphaTest = true' in shader and 'AlphaRef = 128' in shader
    assert 'OutputBlending = OB_Masked' in shader
    original=Image.open(ROOT/('exports/textures/'+name+'.tga')).convert('RGBA')
    exported=Image.open(ROOT/('exports/installed-check/L2AmberNPCv4/Texture/'+name+'.tga')).convert('RGBA')
    assert original.size==exported.size and original.tobytes()==exported.tobytes()
assert 'LodCount = 1' in dump('AmberNPC')
v3=ROOT/'exports/installed-check/L2AmberNPCv3/SkeletalMesh/AmberNPC.psk'
v4=ROOT/'exports/installed-check/L2AmberNPCv4/SkeletalMesh/AmberNPC.psk'
assert v3.read_bytes()==v4.read_bytes(), 'Material revision changed mesh/weights'
motion=pathlib.Path('E:/l2/animations/L2AmberMotionv3.ukx')
assert motion.read_bytes()==(ROOT/'exports/L2AmberMotionv3.ukx').read_bytes(), 'Animation dependency changed'
assert installed.read_bytes()==(ROOT/'exports/L2AmberNPCv4.ukx').read_bytes()
report={'visual_revision':4,'self_illumination':['AmberBody','AmberOutfit'],
        'texture_pixels_roundtrip':True,'geometry_weights_unchanged_from_v3':True,'animation_package_unchanged':True,
        'one_full_detail_lod':True,'depth_write':True,'alpha_test':128,
        'mesh_sha256':hashlib.sha256(v4.read_bytes()).hexdigest(),
        'v3_in_game_screenshot':'2026-10-09: geometry improved; outfit and hair too dark',
        'in_game_validation_v4':False}
(ROOT/'reports/v4-native-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
