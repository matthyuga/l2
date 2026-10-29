"""Build an isolated native label effect and append one client display record."""
from pathlib import Path
import copy, hashlib, json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
STAGE = Path(__file__).resolve().parent
EDITOR = ROOT / 'research/amber-l2/tools/l2editor/L2Editor'
PACKAGE = 'HellgamesLabelsV1'
CLASSES = EDITOR.parent / PACKAGE / 'Classes'
CLASSES.mkdir(parents=True, exist_ok=True)
CODEC = ROOT / 'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
CLIENT = ROOT.parent / 'l2/system-hud'
sys.path.insert(0, str(ROOT / 'research/amber-l2/scripts'))
from contract_dat import Catalog

def run(cmd, **kwargs):
    r = subprocess.run(list(map(str, cmd)), capture_output=True, timeout=120,
                       creationflags=subprocess.CREATE_NO_WINDOW, **kwargs)
    assert r.returncode == 0, (r.stdout + r.stderr).decode(errors='replace')[-3500:]
    return r

imports = []
def texture(name, image):
    image.save(STAGE / (name + '.png'))
    path = STAGE / (name + '.tga')
    ImageOps.flip(image).save(path)
    imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{path.as_posix()}" MIPS=OFF')

im = Image.new('RGBA', (1024, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((42, 28, 982, 228), radius=16, fill=(10, 18, 28, 224),
                    outline=(233, 191, 121, 245), width=3)
for text, y, size in [('H E L L G A M E S', 66, 28), ('EVENTO', 142, 66)]:
    font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', size)
    d.text((512, y), text, font=font, anchor='mm', fill=(245, 215, 159, 255))
texture('EventLabel', im)
dot = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
for y in range(64):
    for x in range(64):
        a = max(0, 1 - ((x - 31.5)**2 + (y - 31.5)**2)**.5 / 30)**2
        dot.putpixel((x, y), (233, 191, 121, round(220 * a)))
texture('GoldMote', dot)

source = '''class EventGold extends Emitter;
IMPORTS
defaultproperties
{
    Begin Object Class=SpriteEmitter Name=Label
        Texture=Texture'HellgamesLabelsV1.EventLabel'
        DrawStyle=PTDS_AlphaBlend
        CoordinateSystem=PTCS_Relative
        UseDirectionAs=PTDU_None
        UseCollision=False
        UniformSize=False
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=1.0
        MaxParticles=1
        RespawnDeadParticles=True
        SecondsBeforeInactive=0.0
        StartLocationRange=(Z=(Min=90.0,Max=90.0))
        StartSizeRange=(X=(Min=55.0,Max=55.0),Y=(Min=13.75,Max=13.75),Z=(Min=1.0,Max=1.0))
        LifetimeRange=(Min=3600.0,Max=3600.0)
    End Object
    Emitters(0)=SpriteEmitter'Label'
    Begin Object Class=SpriteEmitter Name=Motes
        Texture=Texture'HellgamesLabelsV1.GoldMote'
        DrawStyle=PTDS_AlphaBlend
        CoordinateSystem=PTCS_Relative
        UseDirectionAs=PTDU_None
        UseCollision=False
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=5.0
        MaxParticles=16
        RespawnDeadParticles=True
        SecondsBeforeInactive=0.0
        StartLocationRange=(X=(Min=-20.0,Max=20.0),Y=(Min=-20.0,Max=20.0),Z=(Min=68.0,Max=90.0))
        StartVelocityRange=(X=(Min=-1.0,Max=1.0),Y=(Min=-1.0,Max=1.0),Z=(Min=4.0,Max=7.0))
        StartSizeRange=(X=(Min=0.8,Max=1.8),Y=(Min=0.8,Max=1.8),Z=(Min=0.8,Max=1.8))
        FadeIn=True
        FadeInEndTime=0.4
        FadeOut=True
        FadeOutStartTime=1.8
        LifetimeRange=(Min=2.6,Max=3.2)
    End Object
    Emitters(1)=SpriteEmitter'Motes'
    AutoDestroy=False
    bNoDelete=False
    bHidden=False
    bDirectional=False
    LifeSpan=0.0
}
'''.replace('IMPORTS', '\n'.join(imports))
(CLASSES / 'EventGold.uc').write_text(source, encoding='ascii')
(STAGE / 'EventGold.uc').write_text(source, encoding='ascii')
(EDITOR / (PACKAGE + '.ini')).write_text(
    (EDITOR / 'UT2003.ini').read_text(encoding='latin1') +
    f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={PACKAGE}\n', encoding='latin1')
assert not (EDITOR / (PACKAGE + '.u')).exists(), 'Build output already exists; do not overwrite blindly'
r = run([EDITOR / 'UCC.exe', 'make', '-Silent', '-NoBind', 'ini=' + PACKAGE + '.ini'], cwd=EDITOR)
(STAGE / 'build.log').write_bytes(r.stdout + r.stderr)
(STAGE / (PACKAGE + '.u')).write_bytes((EDITOR / (PACKAGE + '.u')).read_bytes())
run([ROOT / 'tools/jdk-25.0.4.1+1/bin/java.exe', '-cp',
     str(ROOT / 'tools/XDAT_NEW/xdat_editor/dist/*') + ';' + str(ROOT / 'research/amber-l2/scripts'),
     'groovy.ui.GroovyMain', ROOT / 'research/amber-l2/scripts/force_client_particles.groovy',
     STAGE / (PACKAGE + '.u')])

# Decode the current client again: never rebuild from a historical catalog.
run([CODEC, '-o', STAGE / 'npcgrp.before.raw', CLIENT / 'npcgrp.dat'])
cat = Catalog(STAGE / 'npcgrp.before.raw', 'npcgrp.xml', 'Interlude')
assert not any(r['npc_id'] == 59030 for r in cat.rows), 'Client display ID already used'
row = copy.deepcopy(next(r for r in cat.rows if r['npc_id'] == 30004))
row['npc_id'] = 59030
row['deco_effect'] = 1
row['deco_effect_items'] = [{'param_deco_effect': PACKAGE + '.EventGold', 'param_deco_effect_scale': 1.0}]
cat.append([row], STAGE / 'npcgrp.raw')
run([CODEC, '-c', 'encode', '-p', '413', '-o', STAGE / 'npcgrp.dat', STAGE / 'npcgrp.raw'])
run([CODEC, '-o', STAGE / 'npcgrp.roundtrip.raw', STAGE / 'npcgrp.dat'])
assert (STAGE / 'npcgrp.raw').read_bytes() == (STAGE / 'npcgrp.roundtrip.raw').read_bytes()
after = Catalog(STAGE / 'npcgrp.roundtrip.raw', 'npcgrp.xml', 'Interlude')
assert after.count == cat.count + 1
for old, new in zip(cat.rows, after.rows):
    assert cat.data[old['_start']:old['_end']] == after.data[new['_start']:new['_end']]
assert cat.data[cat.end:] == after.data[after.end:]
proof = {'package': PACKAGE, 'client_display_id': 59030, 'server_npc_id': 902530,
         'existing_records_preserved': cat.count, 'dat_roundtrip': True,
         'camera_facing': 'SpriteEmitter PTDU_None; requires ingame confirmation',
         'particles': '1 persistent label + max 16 respawning motes',
         'client_before_sha256': hashlib.sha256((CLIENT / 'npcgrp.dat').read_bytes()).hexdigest()}
(STAGE / 'verification.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
print(json.dumps(proof))
