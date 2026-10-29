from pathlib import Path
import pefile,struct,hashlib,json
from keystone import Ks,KS_ARCH_X86,KS_MODE_32
D=Path(__file__).resolve().parent
STAGE=D/'stage';STAGE.mkdir(exist_ok=True)
EXPECTED={'NWindow.dll':'cba1831bb0c6c28b0ab18db47d861a5b87f6f3ac0de85cc55bf8606cac4c2c2d','engine.dll':'b6afd6fa1845c6a966bedf67ef0cee84f32b18f5a385ddfe08492a52ead20863'}
HOOKS={'NWindow.dll':[(0x101977d0,'NexusHairDraw','DRAW'),(0x10021a00,'NexusHairTexture','TEXTURE'),(0x10142000,'NexusHairPacket','PACKET')], 'engine.dll':[(0x104872f0,'NexusHairUser','USER'),(0x10486000,'NexusHairTexName','TEXNAME')]}
ks=Ks(KS_ARCH_X86,KS_MODE_32)
def asm(s,a):return bytes(ks.asm(s,a)[0])
def align(v,a):return (v+a-1)//a*a
manifest={};header=['#pragma once']
for name,hooks in HOOKS.items():
 original=Path('E:/l2/system-hud',name).read_bytes();assert hashlib.sha256(original).hexdigest()==EXPECTED[name]
 p=pefile.PE(data=original);data=bytearray(original);base=p.OPTIONAL_HEADER.ImageBase;last=p.sections[-1]
 raw=align(max(len(data),last.PointerToRawData+last.Misc_VirtualSize,last.PointerToRawData+last.SizeOfRawData),0x1000);rva=last.VirtualAddress+raw-last.PointerToRawData
 section=bytearray(0x4000)
 def put(off,b):section[off:off+len(b)]=b
 imports=b''.join(data[x.struct.get_file_offset():x.struct.get_file_offset()+20] for x in p.DIRECTORY_ENTRY_IMPORT)
 importOff=0x1000;namesOff=0x1800;iltOff=0x1400;iatOff=0x1500;dllOff=0x1700
 put(dllOff,b'NexusHairHslGame.dll\0');desc=struct.pack('<5I',rva+iltOff,0,0,rva+dllOff,rva+iatOff)
 put(importOff,imports+desc+bytes(20));cursor=namesOff;records=[]
 for i,(entry,export,key) in enumerate(hooks):
  put(cursor,b'\0\0'+export.encode()+b'\0');put(iltOff+4*i,struct.pack('<I',rva+cursor));put(iatOff+4*i,struct.pack('<I',rva+cursor));cursor=align(cursor+len(export)+3,2)
  offset=p.get_offset_from_rva(entry-base);old=bytes(data[offset:offset+5]);assert old==bytes.fromhex('558bec6aff') or (key=='TEXNAME' and old[0]==0xe9),(name,hex(entry),old.hex())
  stub=0x100+i*0x40;tramp=0x400+i*0x40
  put(stub,asm(f'call anchor; anchor: pop eax; add eax,{iatOff+4*i-stub-5}; jmp dword ptr [eax]',base+rva+stub))
  if old[0]==0xe9:
   target=entry+5+struct.unpack_from('<i',old,1)[0];put(tramp,asm(f'jmp {target}',base+rva+tramp))
  else:put(tramp,old+asm(f'jmp {entry+5}',base+rva+tramp+5))
  data[offset:offset+5]=asm(f'jmp {base+rva+stub}',entry)
  header.append(f'constexpr unsigned {key}_TRAMP_RVA=0x{rva+tramp:x};')
  records.append(dict(entry=hex(entry),before=old.hex(),after=bytes(data[offset:offset+5]).hex(),trampoline_rva=rva+tramp,export=export))
 data+=bytes(raw-len(data))+section;size=len(data)-last.PointerToRawData
 for field in ['Misc_VirtualSize','SizeOfRawData']:struct.pack_into('<I',data,last.get_field_absolute_offset(field),size)
 struct.pack_into('<I',data,last.get_field_absolute_offset('Characteristics'),(last.Characteristics|0xe0000040)&~0x02000000)
 struct.pack_into('<I',data,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(section),p.OPTIONAL_HEADER.SectionAlignment))
 directory=p.OPTIONAL_HEADER.DATA_DIRECTORY[1];struct.pack_into('<II',data,directory.get_file_offset(),rva+importOff,len(imports)+40)
 struct.pack_into('<I',data,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),0)
 out=STAGE/name;out.write_bytes(data);q=pefile.PE(str(out));assert q.DIRECTORY_ENTRY_IMPORT[-1].dll==b'NexusHairHslGame.dll'
 manifest[name]=dict(before=EXPECTED[name],after=hashlib.sha256(data).hexdigest(),section_rva=rva,hooks=records)
(D/'client_offsets.h').write_text('\n'.join(header)+'\n')
(D/'client-patches.json').write_text(json.dumps(manifest,indent=2))
print('Prepared additive imports and verified trampolines:',{k:len(v['hooks']) for k,v in manifest.items()})
