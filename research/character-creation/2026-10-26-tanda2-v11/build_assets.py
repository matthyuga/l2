from pathlib import Path
import sys,json,struct,subprocess,hashlib,re,zlib
from PIL import Image
from hair_colors import texture_mask,tint
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');AUD=P/'research/character-creation/2026-10-26-mega-audit';OLD=P/'research/character-creation/2026-10-24/hair-alignment-v5'
EDITOR=P/'research/amber-l2/tools/l2editor/L2Editor';PACKAGE='NexusHairT2V11'
sys.path.insert(0,str(P/'research/gludio-sky'));from package_tools import Edit
RACES=['MFighter','FFighter','MDarkElf','FDarkElf','MDwarf','FDwarf','MElf','FElf','MMagic','FMagic','MOrc','FOrc','MShaman','FShaman']
def chunks(path):
 b=path.read_bytes();pos=0;out=[]
 while pos<len(b):
  h=b[pos:pos+32];name,flag,size,count=struct.unpack('<20siii',h);pos+=32;out.append([name.rstrip(b'\0').decode(),h,size,count,b[pos:pos+size*count]]);pos+=size*count
 return out
def pack(name,old,size,count,data):return struct.pack('<20siii',name.encode(),struct.unpack_from('<i',old,20)[0],size,count)+data
def retarget_original(source,model,target):
 c=chunks(source);by={x[0]:x for x in c};faces=by['FACE0000'];mat=by['MATT0000']
 used=sorted({struct.unpack_from('<3HBBI',faces[4],i*faces[2])[3] for i in range(faces[3])});mapping={old:new for new,old in enumerate(used)}
 names=[mat[4][i*mat[2]:i*mat[2]+64].split(b'\0')[0].decode() for i in used];assert 'material_0' not in names,names
 native=chunks(P/Path(json.loads((OLD/'native-skeletons.json').read_text())[RACES.index(model)]['psk']));n=next(x for x in native if x[0]=='REFSKELT');a=by['REFSKELT']
 bone_names=lambda x:[x[4][i*x[2]:i*x[2]+64].split(b'\0')[0].decode().lower() for i in range(x[3])]
 old,new=bone_names(a),bone_names(n);head=next(i for i,v in enumerate(new) if v in ('bip01_head','bip01 head'));remap={i:(new.index(v) if v in new else head) for i,v in enumerate(old)}
 merged={}
 for w,point,bone in struct.iter_unpack('<fii',by['RAWWEIGHTS'][4]):merged[(point,remap[bone])]=merged.get((point,remap[bone]),0)+w
 result=bytearray()
 for name,h,size,count,data in c:
  if name=='REFSKELT':result+=n[1]+n[4]
  elif name=='RAWWEIGHTS':
   raw=b''.join(struct.pack('<fii',w,point,bone) for (point,bone),w in sorted(merged.items()));result+=pack(name,h,12,len(merged),raw)
  elif name=='MATT0000':
   records=[]
   for old_index in used:
    record=bytearray(data[old_index*size:(old_index+1)*size]);struct.pack_into('<i',record,64,mapping[old_index]);records.append(record)
   result+=pack(name,h,size,len(used),b''.join(records))
  elif name=='FACE0000':
   raw=bytearray(data)
   for i in range(count):raw[i*size+6]=mapping[raw[i*size+6]]
   result+=h+raw
  elif name=='VTXW0000':
   raw=bytearray(data)
   for i in range(count):raw[i*size+12]=mapping.get(raw[i*size+12],0)
   result+=h+raw
  else:result+=h+data
 target.write_bytes(result);return names,dict(triangles=faces[3],material_count=len(used),native_bones=n[3],fallback_bones=[old[i] for i,v in remap.items() if old[i] not in new])
def retarget(source,model,target):
 names,proof=retarget_original(source,model,target)
 if len(names)==1:
  proof['atlas_regions']=[];return names,proof
 # Preserve source pixels, pad each region and map all active faces to one skin.
 images=[Image.open(next((AUD/'gallery-assets').rglob(name+'.png'))).convert('RGBA') for name in names]
 pad=4;power=lambda x:1<<(x-1).bit_length();width=power(sum(im.width+pad*2 for im in images));height=power(max(im.height+pad*2 for im in images));atlas=Image.new('RGBA',(width,height));regions=[];x=0
 for im in images:
  box=(x+pad,pad,im.width,im.height);regions.append(dict(x=box[0],y=box[1],width=im.width,height=im.height,atlas_width=width,atlas_height=height))
  atlas.paste(im,(box[0],box[1]));atlas.paste(im.crop((0,0,1,im.height)).resize((pad,im.height)),(x,pad));atlas.paste(im.crop((im.width-1,0,im.width,im.height)).resize((pad,im.height)),(box[0]+im.width,pad))
  atlas.paste(im.crop((0,0,im.width,1)).resize((im.width,pad)),(box[0],0));atlas.paste(im.crop((0,im.height-1,im.width,im.height)).resize((im.width,pad)),(box[0],pad+im.height));x+=im.width+pad*2
 c=chunks(target);by={v[0]:v for v in c};ws,wcount,wb=by['VTXW0000'][2:];fs,fcount,fb=by['FACE0000'][2:];new_wedges=[];lookup={};faces=bytearray(fb)
 for i in range(fcount):
  a,b,cidx,mat,aux,flags=struct.unpack_from('<3HBBI',fb,i*fs);region=regions[mat];indices=[]
  for old_wedge in [a,b,cidx]:
   key=(old_wedge,mat)
   if key not in lookup:
    rec=bytearray(wb[old_wedge*ws:(old_wedge+1)*ws]);u,v=struct.unpack_from('<ff',rec,4);assert 0<=u<=1 and 0<=v<=1
    struct.pack_into('<ff',rec,4,(region['x']+u*region['width'])/width,(region['y']+v*region['height'])/height);rec[12]=0;lookup[key]=len(new_wedges);new_wedges.append(bytes(rec))
   indices.append(lookup[key])
  struct.pack_into('<3HBBI',faces,i*fs,*indices,0,0,flags)
 result=bytearray()
 for name,h,size,count,data in by.values():
  if name=='VTXW0000':result+=pack(name,h,size,len(new_wedges),b''.join(new_wedges))
  elif name=='FACE0000':result+=h+faces
  elif name=='MATT0000':
   material=bytearray(data[:size]);struct.pack_into('<i',material,64,0);result+=pack(name,h,size,1,material)
  else:result+=h+data
 target.write_bytes(result);texture_name=target.stem+'_Atlas';atlas.save(D/'textures'/(texture_name+'.png'))
 proof.update(material_count=1,atlas_regions=regions,atlas_source_textures=names)
 return [texture_name],proof

def main():
 for n in ['stage','retargeted','textures','raw']:(D/n).mkdir(exist_ok=True)
 source_dir=EDITOR.parent/PACKAGE/'Classes';source_dir.mkdir(parents=True,exist_ok=True)
 selection=json.loads((D/'selection.json').read_text());transforms=json.loads((OLD/'native-transforms.json').read_text());lines=['class Assets extends Actor;'];items=[];counts={}
 for selected in selection:
  model=selected['model'];counts[model]=counts.get(model,0)+1;mesh=model+'_T2_'+str(counts[model]);source=AUD/'gallery-assets'/selected['group']/'SkeletalMesh'/selected['meshes'][0];assert len(selected['meshes'])==1
  names,proof=retarget(source,model,D/'retargeted'/(mesh+'.psk'))
  t=transforms[RACES.index(model)];o,sc,rot=t['origin'],t['scale'],t['rotation']
  lines += [f'#exec MESH MODELIMPORT MESH={mesh} MODELFILE="{(D/"retargeted"/(mesh+".psk")).as_posix()}" LODSTYLE=0',f'#exec MESHMAP SCALE MESHMAP={mesh} X={sc["X"]} Y={sc["Y"]} Z={sc["Z"]}',f'#exec MESH ORIGIN MESH={mesh} X={o["X"]} Y={o["Y"]} Z={o["Z"]} YAW={rot["Yaw"]//256} PITCH={rot["Pitch"]//256} ROLL={rot["Roll"]//256}']
  colors_materials=[];colors_textures=[]
  for color in range(4):
   mats=[];texnames=[]
   for i,name in enumerate(names):
    texture=(D/'textures'/(name+'.png')) if (D/'textures'/(name+'.png')).exists() else next((AUD/'gallery-assets').rglob(name+'.png'));base=Image.open(texture).convert('RGBA');mask=texture_mask(model,counts[model],base,proof,AUD/'gallery-assets');mask.save(D/'textures'/(mesh+'_TintMask.png'));im=tint(base,mask,color)
    texname=mesh+'_Color'+str(color)+'_Tex'+str(i);path=D/'textures'/(texname+'.tga');im.save(path)
    lines.append(f'#exec TEXTURE IMPORT NAME={texname} FILE="{path.as_posix()}" MIPS=ON MASKED=1')
    if color==0:lines.append(f'#exec MESHMAP SETTEXTURE MESHMAP={mesh} NUM={i} TEXTURE={texname}')
    texnames.append(texname);mats.append('NexusHairT2M11.'+mesh+'_Color'+str(color)+'_Mat'+str(i))
   colors_materials.append(mats);colors_textures.append(texnames)
  items.append(dict(model=model,race_index=RACES.index(model),index=selected['index'],letter=selected['new_style'],source_style=selected['source_style'],mesh=PACKAGE+'.'+mesh,materials=colors_materials[0],textures=colors_textures[0],color_materials=colors_materials,color_textures=colors_textures,source=str(source),**proof))
 lines+=['defaultproperties','{',' bHidden=True','}'];(source_dir/'Assets.uc').write_text('\n'.join(lines),encoding='ascii')
 config=(EDITOR/'UT2003.ini').read_text(encoding='latin1');config=re.sub(r'(?im)^EditPackages=.*\n?','',config);config+='\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages='+PACKAGE+'\n';(EDITOR/(PACKAGE+'.ini')).write_text(config,encoding='latin1')
 compiled=EDITOR/(PACKAGE+'.u')
 if compiled.exists():assert '--reuse-compiled' in sys.argv,'Unique compilation already exists; inspect before rebuilding'
 else:
  with (D/'ucc-build.log').open('w') as log:r=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini='+PACKAGE+'.ini'],cwd=EDITOR,stdout=log,stderr=subprocess.STDOUT,timeout=180)
  assert r.returncode==0 and compiled.exists(),(D/'ucc-build.log').read_text(errors='replace')[-3000:]
 # Keep native compiler mesh/class payloads byte-for-byte. Materials live in a
 # separate minimal texture package, as in the working Tanda 1 integration.
 e=Edit(P/'research/character-creation/2026-10-24/hair-material-v4/empty.u')
 for item in items:
  for mats,textures in zip(item['color_materials'],item['color_textures']):
   for name,tex in zip(mats,textures):
    ref=e.imp(PACKAGE+'.'+tex,'Engine.Texture')
    raw=e.prop('FrameBufferBlending',1,bytes([2]))+e.boolean('ZWrite',True)+e.boolean('ZTest',True)+e.boolean('AlphaTest',True)+e.boolean('TwoSided',True)+e.prop('AlphaRef',1,bytes([5]))+e.obj('Material',ref)+e.end()
    e.add(name.split('.')[-1],'Engine.FinalBlend',raw,flags=0x000f0004)
 raw=D/'raw'/(PACKAGE+'.u');raw.write_bytes(compiled.read_bytes());materials=D/'raw/NexusHairT2M11.utx';e.save(materials)
 codec=P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';files=[]
 for original in [raw,materials]:
  target=D/'stage'/original.name
  r=subprocess.run([str(codec),'-c','encode','-p','121','-f',original.name,'-o',str(target),str(original)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0,r.stderr
  check=D/'raw'/('roundtrip-'+original.name);r=subprocess.run([str(codec),'-f',original.name,'-o',str(check),str(target)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0 and check.read_bytes()==original.read_bytes(),r.stdout+r.stderr
  b=target.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20]);assert b[:28].decode('utf-16le')=='Lineage2Ver121'
  files.append(dict(file=str(target),sha256=hashlib.sha256(b).hexdigest()))
 (D/'assets-manifest.json').write_text(json.dumps(dict(package=PACKAGE,files=files,items=items,color_names=["Original","Casta?o","Rubio","Plateado"],alpha_preserved=True,protocol=121,crc_verified=True),indent=2),encoding='utf8')
 print('BUILT',len(items),'meshes and',sum(sum(len(v) for v in x['color_materials']) for x in items),'FinalBlend materials; native 121 verified.',flush=True)
if __name__=='__main__':main()
