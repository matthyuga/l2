"""Recompile donor PSK/TGA resources with the native Interlude-era editor."""
from pathlib import Path
import sys,json,subprocess,struct,hashlib,re
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[3]
EXPORT=PROJECT/'research/character-creation/2026-10-23/downloads/donor-inspection/exports'
EDITOR=PROJECT/'research/amber-l2/tools/l2editor/L2Editor'
PACKAGE='NexusAppearanceV1'
RACES=['MFighter','FFighter','MDarkElf','FDarkElf','MDwarf','FDwarf','MElf','FElf','MMagic','FMagic','MOrc','FOrc','MShaman','FShaman']
BASE=[5,7,5,7,5,7,5,7,5,7,5,5,5,7]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def retarget(psk,race_index):
 def chunks(path):
  b=path.read_bytes();p=0;out=[]
  while p<len(b):
   header=b[p:p+32];name,flags,size,count=struct.unpack('<20siii',header);p+=32
   out.append([name.rstrip(b'\0').decode(),header,size,count,b[p:p+size*count]]);p+=size*count
  return out
 source=chunks(psk);native=chunks(Path(json.loads((ROOT/'native-skeletons.json').read_text())[race_index]['psk']))
 a=next(c for c in source if c[0]=='REFSKELT');n=next(c for c in native if c[0]=='REFSKELT')
 names=lambda c:[c[4][i*c[2]:i*c[2]+64].split(b'\0')[0].decode().lower() for i in range(c[3])]
 old=names(a);new=names(n);head=next(i for i,v in enumerate(new) if v in ('bip01_head','bip01 head'))
 remap={i:(new.index(v) if v in new else head) for i,v in enumerate(old)}
 weights=next(c for c in source if c[0]=='RAWWEIGHTS');merged={}
 for w,point,bone in struct.iter_unpack('<fii',weights[4]):
  key=(point,remap[bone]);merged[key]=merged.get(key,0)+w
 raw=b''.join(struct.pack('<fii',w,p,b) for (p,b),w in sorted(merged.items()))
 result=bytearray()
 for c in source:
  if c[0]=='REFSKELT':result+=n[1]+n[4]
  elif c[0]=='RAWWEIGHTS':result+=struct.pack('<20siii',b'RAWWEIGHTS',struct.unpack_from('<i',c[1],20)[0],12,len(merged))+raw
  else:result+=c[1]+c[4]
 target=ROOT/'retargeted'/psk.name;target.parent.mkdir(exist_ok=True);target.write_bytes(result)
 return target
def main():
 stage=ROOT/'stage';stage.mkdir(exist_ok=True);tex=ROOT/'textures';tex.mkdir(exist_ok=True)
 source=EDITOR.parent/PACKAGE/'Classes';source.mkdir(parents=True,exist_ok=True)
 lines=['class Assets extends Actor;'];items=[]
 faces={p.stem.lower():p for p in (EXPORT/'LineageFaceTex/Texture').glob('*.tga')}
 # Four color options for the new styles. The original styles keep their original colors.
 palettes=[None,(0.29,0.16,0.09),(0.78,0.61,0.32),(0.84,0.85,0.87)]
 for race_index,race in enumerate(RACES):
  for variant in range(2):
   mesh_name=f'{race}_Hair{variant+1}';donor_name=f'{race}_h0{variant}_m005'
   psk=EXPORT/'LineagePChair/SkeletalMesh'/(donor_name+'.psk');assert psk.exists(),psk
   image=EXPORT/'LineagePChairTex/Texture'/(donor_name+'_t00_ori.tga');assert image.exists(),image
   native_psk=retarget(psk,race_index)
   lines += [f'#exec MESH MODELIMPORT MESH={mesh_name} MODELFILE="{native_psk.as_posix()}" LODSTYLE=0',f'#exec MESHMAP SCALE MESHMAP={mesh_name} X=1 Y=1 Z=1']
   for color,palette in enumerate(palettes):
    name=f'{race}_Hair{variant+1}_Color{color}'
    im=Image.open(image).convert('RGBA')
    if palette:
     pixels=[]
     for r,g,b,a in im.getdata():
      luminance=(r*.2126+g*.7152+b*.0722)/255
      value=min(1,0.14+luminance*1.08)
      pixels.append(tuple(round(255*min(1,value*c)) for c in palette)+(a,))
     im.putdata(pixels)
    path=tex/(name+'.tga');im.save(path)
    lines.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{path.as_posix()}" MIPS=ON MASKED=1')
   lines.append(f'#exec MESHMAP SETTEXTURE MESHMAP={mesh_name} NUM=0 TEXTURE={race}_Hair{variant+1}_Color0')
   items.append(dict(race_index=race_index,race=race,kind='hair',index=BASE[race_index]+variant,mesh=f'{PACKAGE}.{mesh_name}',materials=[f'{PACKAGE}.{race}_Hair{variant+1}_Color{i}' for i in range(4)],source=str(psk)))
  for variant in range(3):
   # Male Orc uses its own face model m001; the other races use m000.
   candidates=[p for key,p in faces.items() if re.fullmatch(re.escape(race.lower())+r'_m\d{3}_t0'+str(variant+3)+'_f',key)]
   assert len(candidates)==1,(race,variant,candidates)
   image=candidates[0]
   name=f'{race}_Face{variant+3}'
   lines.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{image.as_posix()}" MIPS=ON')
   items.append(dict(race_index=race_index,race=race,kind='face',index=variant+3,material=f'{PACKAGE}.{name}',source=str(image)))
 lines+=['defaultproperties','{','    bHidden=True','}']
 (source/'Assets.uc').write_text('\n'.join(lines),encoding='ascii')
 config=(EDITOR/'UT2003.ini').read_text(encoding='latin1')
 config=re.sub(r'(?im)^EditPackages=.*\n?','',config)
 config+='\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages='+PACKAGE+'\n'
 (EDITOR/(PACKAGE+'.ini')).write_text(config,encoding='latin1')
 compiled=EDITOR/(PACKAGE+'.u')
 # A previous local compilation is never a live installed file.
 if compiled.exists():compiled.rename(ROOT/(PACKAGE+'.previous-'+str(compiled.stat().st_mtime_ns)+'.u'))
 with (ROOT/'ucc-build.log').open('w') as out:
  r=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini='+PACKAGE+'.ini'],cwd=EDITOR,stdout=out,stderr=subprocess.STDOUT,timeout=180)
 assert r.returncode==0,(ROOT/'ucc-build.log').read_text(errors='replace')[-3000:]
 assert compiled.exists()
 sys.path.insert(0,str(PROJECT/'research/airships'));from read_map import Package
 pkg=Package(compiled);assert pkg.version<=123,(pkg.version,pkg.license)
 references={PACKAGE+'.'+pkg.ref(i+1) for i in range(len(pkg.exports))}
 for item in items:
  for key in ['mesh','material']:
   if key in item:assert item[key] in references,item
  for material in item.get('materials',[]):assert material in references,material
 target=stage/(PACKAGE+'.u')
 codec=PROJECT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
 r=subprocess.run([str(codec),'-c','encode','-p','111','-o',str(target),str(compiled)],capture_output=True);assert not r.returncode
 check=stage/'appearance.check.raw';r=subprocess.run([str(codec),'-o',str(check),str(target)],capture_output=True);assert not r.returncode and check.read_bytes()==compiled.read_bytes()
 result=dict(package=PACKAGE,file=str(target),sha256=sha(target),version=pkg.version,license=pkg.license,hair_models=28,hair_materials=112,new_faces=42,items=items,original_options_preserved=True)
 (ROOT/'assets-manifest.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('BUILT',target,'version',pkg.version,'hair',28,'face',42,flush=True)
if __name__=='__main__':main()
