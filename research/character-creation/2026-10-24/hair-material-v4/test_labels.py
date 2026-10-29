from pathlib import Path
import pefile,struct,json
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
D=Path(__file__).resolve().parent
def put(u,a,v):u.mem_write(a,struct.pack('<I',v))
tests=0
for delta in [0,0x02000000]:
 p=pefile.PE(str(D/'stage/NWindow.dll'));u=Uc(UC_ARCH_X86,UC_MODE_32);img=p.get_memory_mapped_image();base=p.OPTIONAL_HEADER.ImageBase+delta;u.mem_map(base,(len(img)+4095)//4096*4096);u.mem_write(base,img)
 u.mem_map(0x40000000,0x100000);ctrl=0x40001000;stack=0x40010000;stop=0x1019751c+delta;ctor=0x40008000;data=0x40009000;game=0x40020000
 put(u,base+0x22c790,game);put(u,base+0x22c3e4,ctor);u.mem_write(data,'Type A\0'.encode('utf-16le'))
 def hook(u,a,size,unused):
  if a==stop:u.emu_stop()
  elif a==ctor:
   assert u.reg_read(UC_X86_REG_ECX)==game+179*12+0x6a8dc
   sp=u.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',u.mem_read(sp,4))[0];u.reg_write(UC_X86_REG_EAX,data);u.reg_write(UC_X86_REG_ESP,sp+4);u.reg_write(UC_X86_REG_EIP,ret)
 u.hook_add(UC_HOOK_CODE,hook)
 for id,selection,label in [(179,0,'Type A'),(28000,5,'Type F'),(28001,6,'Type G'),(28000,7,'Type H'),(28001,8,'Type I')]:
  put(u,ctrl+0x2ec,selection);u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ESI,ctrl);u.reg_write(UC_X86_REG_EBP,1234);u.reg_write(UC_X86_REG_EAX,id)
  u.emu_start(0x10197507+delta,stop+1,count=200)
  ptr=u.reg_read(UC_X86_REG_EAX);raw=bytearray()
  while u.mem_read(ptr,2)!=b'\0\0':raw+=u.mem_read(ptr,2);ptr+=2
  assert raw.decode('utf-16le')==label
  assert u.reg_read(UC_X86_REG_ESP)==stack and u.reg_read(UC_X86_REG_EBP)==1234
  tests+=1
(D/'label-test-results.json').write_text(json.dumps(dict(passed=tests,labels=['Type F','Type G','Type H','Type I'],native_label_fallback=True),indent=2));print('PASS:',tests,'native/custom label scenarios, including rebasing')
