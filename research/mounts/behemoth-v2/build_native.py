"""Compile an isolated NPC mesh/client class and link original native animation in place."""
import pathlib,sys,json,subprocess,struct,hashlib,shutil
from PIL import Image
R=pathlib.Path(__file__).resolve().parent;LAB=R.parents[2];CLIENT=LAB.parent/'l2'
EDITOR=LAB/'research/amber-l2/tools/l2editor/L2Editor'
sys.path.insert(0,str(LAB/'research/dust2-animation-study/native'))
from inspect_package import Package,Reader
from write_l2_animation import ci,chunks
psk=chunks(R/'BehemothTwoRiders.psk')['REFSKELT'];original=chunks(R/'native-source/LineageMonsters3/SkeletalMesh/antaras_ex_a_m00.psk')['REFSKELT']
names=lambda c:[struct.unpack_from('<64s',c[2],i*c[0])[0].rstrip(b'\0') for i in range(c[1])]
assert names(psk)==names(original),'Native animation requires the original ordered skeleton'

# The compiler needs the shipped parent classes; decode copies into its staging directory.
for name in ['LineageWarrior.u','LineageMonster3.u']:
 source=CLIENT/'system-hud'/name;dest=EDITOR/name
 if dest.exists():
  old=Package(dest);new=Package(source)
  assert old.d==new.d,'Compiler dependency already exists with different contents: '+name
 else:dest.write_bytes(Package(source).d)

report=json.loads((R/'animation-build-report.json').read_text())
textures={}
for i,name in enumerate(report['nativeMaterials']):
 texture=R/('Mat'+str(i)+'.tga')
 if i<2:shutil.copy2(R/('native-source/LineageMonstersTex3/Texture/antaras_ex_a_t0'+str(i)+'_sp.tga'),texture)
 elif 'Madera' in name:Image.open(LAB/'research/model-catalog/exports/l2lab-behemoth-two-riders/wood.png').convert('RGB').save(texture)
 elif 'Cuero marron' in name:Image.open(LAB/'research/model-catalog/exports/l2lab-behemoth-two-riders/leather.png').convert('RGB').save(texture)
 else:
  color=(120,82,36) if 'Bronce' in name else (35,40,43) if 'Hierro' in name else (48,23,10) if 'Riendas' in name else (51,11,9)
  Image.new('RGB',(32,32),color).save(texture)
 textures[i]=texture

from pack_native_materials import pack_materials
native_psk,textures=pack_materials(R,chunks)
classes=EDITOR.parent/'BHMTransport/Classes';classes.mkdir(parents=True,exist_ok=True)
uc=(R/'BehemothRide.uc').read_text(encoding='utf8')
directives=[f'#exec MESH MODELIMPORT MESH=BehemothMesh MODELFILE="{native_psk.as_posix()}" LODSTYLE=0 LODSPECIFY=1',
 '#exec MESH LODMODEL MESH=BehemothMesh LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=4 COHERENCE=1',
 '#exec MESHMAP SCALE MESHMAP=BehemothMesh X=1 Y=1 Z=1',
 '#exec MESH ORIGIN MESH=BehemothMesh X=0 Y=0 Z=57 YAW=192']
for i,file in textures.items():
 directives.extend([f'#exec TEXTURE IMPORT NAME=Mat{i} FILE="{file.as_posix()}" MIPS=ON',f'#exec MESHMAP SETTEXTURE MESHMAP=BehemothMesh NUM={i} TEXTURE=Mat{i}'])
uc=uc.replace('var int DriverId','\n'.join(directives)+'\n\nvar int DriverId')
(classes/'BehemothRide.uc').write_text(uc,encoding='ascii')
ini=(EDITOR/'UT2003.ini').read_text(encoding='latin1')+'\n[Core.System]\nPaths='+str(EDITOR/'*.u').replace('\\','/')+'\nPaths='+str(CLIENT/'system-hud/*.u').replace('\\','/')+'\nPaths='+str(CLIENT/'Animations/*.ukx').replace('\\','/')+'\nPaths='+str(CLIENT/'SysTextures/*.utx').replace('\\','/')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=BHMTransport\n'
(EDITOR/'BHMTransport.ini').write_text(ini,encoding='latin1')
compiled=EDITOR/'BHMTransport.u'
if compiled.exists():
 backup=R/'compiler-previous.u';shutil.copy2(compiled,backup);compiled.unlink()
proc=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini=BHMTransport.ini'],cwd=EDITOR,capture_output=True,timeout=120)
(R/'ucc-build.log').write_bytes(proc.stdout+proc.stderr)
print((proc.stdout+proc.stderr).decode('latin1')[-1800:]);assert proc.returncode==0,'UCC compilation failed'
p=Package(compiled);names_table=list(p.names)
def nr(s):
 if s not in names_table:names_table.append(s)
 return names_table.index(s)
imports=list(p.imports)
imports.append(dict(cls_pkg=nr('Core'),cls=nr('Package'),outer=0,name=nr('LineageMonsters3')));pkg=-len(imports)
imports.append(dict(cls_pkg=nr('Engine'),cls=nr('MeshAnimation'),outer=pkg,name=nr('antaras_ex_a_anim')));anim=-len(imports)
imports.append(dict(cls_pkg=nr('Core'),cls=nr('Package'),outer=0,name=nr('LineageMonster3')));parentpkg=-len(imports)
imports.append(dict(cls_pkg=nr('Core'),cls=nr('Class'),outer=parentpkg,name=nr('antaras_ex_a')));parentsuper=-len(imports)
e=next(x for x in p.exports if p.names[x['name']]=='BehemothMesh');raw=p.d[e['offset']:e['offset']+e['size']]
native_bones=chunks(native_psk)['REFSKELT']
expected=[x.decode() for x in names(native_bones)];assert expected[:-1]==[x.decode() for x in names(original)] and expected[-1]=='Bone15'
matches=[]
for pos in range(len(raw)-2):
 try:
  r=Reader(raw,pos)
  if r.ci()!=len(expected):continue
  for n in expected:
   if p.names[r.ci()]!=n:raise ValueError()
   r.p+=56
  old=r.ci()
  if old==0:matches.append(r.p-1)
 except (IndexError,ValueError,struct.error):pass
assert len(matches)==1,matches
assert len(ci(anim))==1,'Animation reference must preserve absolute lazy-array offsets'
pos=matches[0];data=bytearray(p.d);data[e['offset']+pos:e['offset']+pos+1]=ci(anim)
# This compiler's Pawn predates the client's animation-name arrays. Add inherited
# property tags at the end of the class defaults without touching mesh payloads.
cls=next(x for x in p.exports if p.names[x['name']]=='BehemothRide')
classraw=p.d[cls['offset']:cls['offset']+cls['size']]
classreader=Reader(classraw);assert classreader.ci()==cls['super']
classraw=ci(parentsuper)+classraw[classreader.p:]
none=ci(nr('None'));assert classraw.endswith(none)
defaults=bytearray(classraw[:-len(none)])
for key,value in {'WaitAnimName':'atkwait','WalkAnimName':'Walk','RunAnimName':'run','DeathAnimName':'death','DeathWaitAnimName':'deathwait'}.items():
 value=ci(nr(value));defaults+=ci(nr(key))+bytes([0x56,len(value)])+value
defaults+=none;classoff=len(data);data+=defaults
P=struct.pack;nameoff=len(data);r=Reader(p.d,struct.unpack_from('<I',p.d,16)[0])
for _ in p.names:r.string();r.u()
start=struct.unpack_from('<I',p.d,16)[0];data+=p.d[start:r.p]
for n in names_table[len(p.names):]:b=n.encode()+b'\0';data+=ci(len(b))+b+P('<I',0x70010)
importoff=len(data)
for i in imports:data+=ci(i['cls_pkg'])+ci(i['cls'])+P('<i',i['outer'])+ci(i['name'])
exportoff=len(data)
for x in p.exports:
 size,offset=(len(defaults),classoff) if x is cls else (x['size'],x['offset'])
 superclass=parentsuper if x is cls else x['super']
 data+=ci(x['cls'])+ci(superclass)+P('<i',x['outer'])+ci(x['name'])+P('<I',x['flags'])+ci(size)+(ci(offset) if size else b'')
struct.pack_into('<6I',data,12,len(names_table),nameoff,len(p.exports),exportoff,len(imports),importoff)
out=R/'BHMTransport.u';out.write_bytes(data);linked=Package(out)
assert linked.obj(anim)=='LineageMonsters3.antaras_ex_a_anim'
assert linked.obj(next(x for x in linked.exports if linked.names[x['name']]=='BehemothRide')['super'])=='LineageMonster3.antaras_ex_a'
for x,y in zip(p.exports,linked.exports):
 if x is not cls:assert x['size']==y['size'] and x['offset']==y['offset']
(R/'native-build-report.json').write_text(json.dumps({'sha256':hashlib.sha256(data).hexdigest(),'bones':len(expected),'nativeAnimation':'LineageMonsters3.antaras_ex_a_anim','parentClass':'LineageMonster3.antaras_ex_a','meshAndTextureOffsetsPreserved':True,'classDefaultsExtended':True,'meshReferencePatchedInPlace':True,'nativeClientVerified':False},indent=2),encoding='utf8')
print('BEHEMOTH_NATIVE_PACKAGE_READY',len(data))
