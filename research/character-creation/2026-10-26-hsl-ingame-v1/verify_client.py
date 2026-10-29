from pathlib import Path
import pefile,hashlib,json
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
D=Path(__file__).resolve().parent;manifest=json.loads((D/'client-patches.json').read_text());checks=0
for name,m in manifest.items():
 original=Path('E:/l2/system-hud',name).read_bytes();new=(D/'stage'/name).read_bytes();assert hashlib.sha256(original).hexdigest()==m['before']
 p=pefile.PE(data=original);q=pefile.PE(data=new);base=p.OPTIONAL_HEADER.ImageBase
 # Original import descriptors/IAT, exports and relocation entries stay intact.
 assert [(x.dll,[(y.name,y.ordinal,y.address) for y in x.imports]) for x in p.DIRECTORY_ENTRY_IMPORT]==[(x.dll,[(y.name,y.ordinal,y.address) for y in x.imports]) for x in q.DIRECTORY_ENTRY_IMPORT[:-1]];checks+=1
 assert p.OPTIONAL_HEADER.DATA_DIRECTORY[5].VirtualAddress==q.OPTIONAL_HEADER.DATA_DIRECTORY[5].VirtualAddress;checks+=1
 assert p.OPTIONAL_HEADER.AddressOfEntryPoint==q.OPTIONAL_HEADER.AddressOfEntryPoint;checks+=1
 allowed=set()
 for r in m['hooks']:
  off=p.get_offset_from_rva(int(r['entry'],16)-base);allowed.update(range(off,off+5))
 for field in ['Misc_VirtualSize','SizeOfRawData','Characteristics']:
  off=p.sections[-1].get_field_absolute_offset(field);allowed.update(range(off,off+4))
 for field in ['SizeOfImage','CheckSum']:
  off=p.OPTIONAL_HEADER.get_field_absolute_offset(field);allowed.update(range(off,off+4))
 off=p.OPTIONAL_HEADER.DATA_DIRECTORY[1].get_file_offset();allowed.update(range(off,off+8))
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,new)));checks+=1
 # Execute each shipped entry -> relative stub -> loader IAT. All registers but
 # EAX and the existing thiscall stack/arguments must survive unchanged.
 image=q.get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(len(image)+0xfff)&~0xfff);u.mem_write(base,image)
 u.mem_map(0x30000000,0x10000);u.mem_map(0x31000000,0x1000)
 extra=q.DIRECTORY_ENTRY_IMPORT[-1]
 for i,(hook,imp) in enumerate(zip(m['hooks'],extra.imports)):
  dest=0x31000000+i*16;u.mem_write(imp.address,dest.to_bytes(4,'little'));u.mem_write(dest,b'\x90')
  for reg,v in [(UC_X86_REG_EBX,0x12345678),(UC_X86_REG_ESI,0x34567890),(UC_X86_REG_EDI,0x56789012),(UC_X86_REG_ECX,0x11223344),(UC_X86_REG_EDX,0x55667788),(UC_X86_REG_ESP,0x30008000)]:u.reg_write(reg,v)
  stack=b'\x12\x34\x56\x78'*24;u.mem_write(0x30008000,stack);u.emu_start(int(hook['entry'],16),dest,count=20)
  assert u.reg_read(UC_X86_REG_EIP)==dest and u.reg_read(UC_X86_REG_ESP)==0x30008000;checks+=1
  assert bytes(u.mem_read(0x30008000,len(stack)))==stack;checks+=1
  assert u.reg_read(UC_X86_REG_ECX)==0x11223344 and u.reg_read(UC_X86_REG_EDX)==0x55667788;checks+=1
  assert u.reg_read(UC_X86_REG_EBX)==0x12345678 and u.reg_read(UC_X86_REG_ESI)==0x34567890 and u.reg_read(UC_X86_REG_EDI)==0x56789012;checks+=1
 # New imports resolve to exactly the intended module exports.
 dll=pefile.PE(str(D/'stage/NexusHairHslGame.dll'));exports={x.name.decode() for x in dll.DIRECTORY_ENTRY_EXPORT.symbols if x.name};assert {x.name.decode() for x in extra.imports}<=exports;checks+=1
print('PASS',checks,'PE preservation and shipped hook execution checks')
(D/'client-test-results.json').write_text(json.dumps(dict(passed=checks,original_imports_exports_relocations_preserved=True),indent=2))
