from pathlib import Path
import sys,struct,subprocess
root=Path(r'E:\l2-local');s=root/'research/visual-effects/npc-labels/native-v1/compact-v3'
sys.path.insert(0,str(root/'research/gludio-sky'));from package_tools import Edit,change_props,ci
# Always read the installed baseline rather than an earlier staged mutation.
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
subprocess.run([str(codec),'-o',str(s/'HellgamesLabelsV1.u'),r'E:\l2\system-hud\HellgamesLabelsV1.u'],capture_output=True,check=True)
p=Edit(s/'HellgamesLabelsV1.u');ref=p.imp('HGLabelArtV3.EventLabel','Engine.Texture')
def boolprop(name,val):return ci(p.name(name))+bytes([0x83 if val else 0x03])
def rv(x,y,z):
 out=b''
 for axis,v in zip(['X','Y','Z'],[x,y,z]):
  rang=p.float('Min',v)+p.float('Max',v)+p.end()
  out+=p.prop(axis,10,rang,'Range')
 return out+p.end()
for e in p.exports:
 if p.ref(e['cl'])!='Engine.SpriteEmitter':continue
 if e['name']=='Label':changes={'Texture':p.obj('Texture',ref),'StartSizeRange':p.prop('StartSizeRange',10,rv(20,10,1),'RangeVector'),'StartLocationRange':p.prop('StartLocationRange',10,rv(0,0,18),'RangeVector'),'UniformSize':boolprop('UniformSize',False),'UseRegularSizeScale':boolprop('UseRegularSizeScale',False)}
 else:changes={'Disabled':boolprop('Disabled',True)}
 p.replace(e,change_props(p,e,changes))
p.save(s/'HellgamesLabelsV1.compact.raw')
subprocess.run([str(codec),'-c','encode','-p','111','-o',str(s/'HellgamesLabelsV1.u'),str(s/'HellgamesLabelsV1.compact.raw')],capture_output=True,check=True)
subprocess.run([str(codec),'-o',str(s/'label.roundtrip.raw'),str(s/'HellgamesLabelsV1.u')],capture_output=True,check=True)
assert (s/'label.roundtrip.raw').read_bytes()==(s/'HellgamesLabelsV1.compact.raw').read_bytes()
print('PASS compact package mutation and exact encode/decode.')
