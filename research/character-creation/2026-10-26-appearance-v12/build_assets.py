from pathlib import Path
import json,struct,sys,subprocess,re,hashlib,zlib
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');AUD=D.parent/'2026-10-26-rea-appearance-audit';EDITOR=P/'research/amber-l2/tools/l2editor/L2Editor'
sys.path.insert(0,str(P/'research/gludio-sky'));from package_tools import Edit
def chunks(path):
 b=path.read_bytes();p=0;out=[]
 while p<len(b):
  h=b[p:p+32];name,flag,size,count=struct.unpack('<20siii',h);p+=32;out.append((name.split(b'\0')[0].decode(),h,size,count,b[p:p+size*count]));p+=size*count
 return out
def retarget():
 source=AUD/'donor-exports/Orc/SkeletalMesh/MOrc_m001_f.psk';parts=chunks(source);native=json.loads((D.parent/'2026-10-24/hair-alignment-v5/native-skeletons.json').read_text())[10]['psk'];native=next(c for c in chunks(P/native) if c[0]=='REFSKELT');old=next(c for c in parts if c[0]=='REFSKELT')
 names=lambda c:[c[4][i*c[2]:i*c[2]+64].split(b'\0')[0].decode().lower() for i in range(c[3])]
 before,after=names(old),names(native);head=next(i for i,n in enumerate(after) if n in ['bip01 head','bip01_head']);remap={i:(after.index(n) if n in after else head) for i,n in enumerate(before)};merged={}
 for w,point,bone in struct.iter_unpack('<fii',next(c for c in parts if c[0]=='RAWWEIGHTS')[4]):merged[(point,remap[bone])]=merged.get((point,remap[bone]),0)+w
 result=bytearray()
 for name,h,size,count,raw in parts:
  if name=='REFSKELT':result+=native[1]+native[4]
  elif name=='RAWWEIGHTS':result+=struct.pack('<20siii',b'RAWWEIGHTS',struct.unpack_from('<i',h,20)[0],12,len(merged))+b''.join(struct.pack('<fii',w,point,bone) for (point,bone),w in sorted(merged.items()))
  else:result+=h+raw
 target=D/'MOrc_ModernFace.psk';target.write_bytes(result);return target
def main():
 for n in ['stage','raw']:(D/n).mkdir(exist_ok=True)
 package='NexusOrcFaceV12';target=retarget();source=EDITOR.parent/package/'Classes';source.mkdir(parents=True,exist_ok=True)
 t=json.loads((D.parent/'2026-10-24/hair-alignment-v5/native-transforms.json').read_text())[10];o,sc,rot=t['origin'],t['scale'],t['rotation']
 lines=['class Assets extends Actor;',f'#exec MESH MODELIMPORT MESH=MOrc_ModernFace MODELFILE="{target.as_posix()}" LODSTYLE=0',f'#exec MESHMAP SCALE MESHMAP=MOrc_ModernFace X={sc["X"]} Y={sc["Y"]} Z={sc["Z"]}',f'#exec MESH ORIGIN MESH=MOrc_ModernFace X={o["X"]} Y={o["Y"]} Z={o["Z"]} YAW={rot["Yaw"]//256} PITCH={rot["Pitch"]//256} ROLL={rot["Roll"]//256}','defaultproperties','{',' bHidden=True','}'];(source/'Assets.uc').write_text('\n'.join(lines),encoding='ascii')
 ini=re.sub(r'(?im)^EditPackages=.*\n?','',(EDITOR/'UT2003.ini').read_text(encoding='latin1'))+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages='+package+'\n';(EDITOR/(package+'.ini')).write_text(ini,encoding='latin1')
 compiled=EDITOR/(package+'.u');assert not compiled.exists(),'Compilation exists; inspect before reuse'
 with (D/'ucc-build.log').open('w') as log:r=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini='+package+'.ini'],cwd=EDITOR,stdout=log,stderr=subprocess.STDOUT,timeout=180)
 assert r.returncode==0 and compiled.exists();raw_head=D/'raw'/('NexusOrcFaceV12.ukx');raw_head.write_bytes(compiled.read_bytes())
 files=[raw_head];materials=[]
 for package,source_package,template,blend,alpha in [('NexusHairGRepairV12','NexusAppearanceV1','MDarkElf_Hair2_Color{}',2,160),('NexusOrcaJRepairV12','NexusHairT2V11','FOrc_T2_1_Color{}_Tex0',0,128)]:
  e=Edit(D.parent/'2026-10-24/hair-material-v4/empty.u')
  for color in range(4):
   name=('MDarkElf_G_Color' if blend==2 else 'FOrc_J_Color')+str(color);ref=e.imp(source_package+'.'+template.format(color),'Engine.Texture')
   raw=e.obj('Material',ref)+e.prop('FrameBufferBlending',1,bytes([blend]))+e.boolean('AlphaTest',True)+e.boolean('TwoSided',True)+e.boolean('ZWrite',True)+e.boolean('ZTest',True)+e.prop('AlphaRef',1,bytes([alpha]))+e.end();e.add(name,'Engine.FinalBlend',raw,flags=0x000f0004);materials.append(dict(name=package+'.'+name,blend=blend,alpha_ref=alpha,texture=source_package+'.'+template.format(color)))
  path=D/'raw'/(package+'.utx');e.save(path);files.append(path)
 codec=P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';proof=[]
 for source in files:
  out=D/'stage'/source.name;r=subprocess.run([str(codec),'-c','encode','-p','121','-f',source.name,'-o',str(out),str(source)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0
  check=D/'raw'/('roundtrip-'+source.name);r=subprocess.run([str(codec),'-f',source.name,'-o',str(check),str(out)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0 and check.read_bytes()==source.read_bytes();b=out.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20]);proof.append(dict(file=str(out),sha256=hashlib.sha256(b).hexdigest(),protocol=121,crc_and_roundtrip=True))
 (D/'repair-manifest.json').write_text(json.dumps(dict(files=proof,materials=materials,orc_face='NexusOrcFaceV12.MOrc_ModernFace',head_source=str(AUD/'donor-exports/Orc/SkeletalMesh/MOrc_m001_f.psk'),original_faces_preserved=[0,1,2],new_faces=[3,4,5]),indent=2),encoding='utf8');print('BUILT: retargeted Orc face, four donor-matching Dark Elf G materials and four opaque-cutout Orca J materials.')
if __name__=='__main__':main()
