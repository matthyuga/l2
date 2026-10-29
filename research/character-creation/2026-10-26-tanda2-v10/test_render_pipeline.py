from pathlib import Path
import json,struct,pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
D=Path(__file__).resolve().parent;M=json.loads((D/'native-manifest.json').read_text());tests=0;replays=0
def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def readstr(u,a):
 b=bytearray()
 while u.mem_read(a,2)!=b'\0\0':b+=u.mem_read(a,2);a+=2
 return b.decode('utf-16le')
for delta in [0,0x02000000]:
 p=pefile.PE(str(D/'stage/engine.dll'));base=p.OPTIONAL_HEADER.ImageBase+delta;b=p.get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(len(b)+4095)//4096*4096);u.mem_write(base,b);u.mem_map(0x40000000,0x100000)
 user=0x40001000;pawn=0x40003000;stack=0x40010000;stop=0x40007000;ctor=0x40006000;actor=0x40030000;vtable=0x40031000;setskin=0x40008000;frame=0x40018000
 put(u,user+0x204,pawn);put(u,base+(0x11d8d988-p.OPTIONAL_HEADER.ImageBase),ctor);put(u,actor,vtable);put(u,vtable+0xd4,setskin);state={};regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
 def hook(u,a,size,unused):
  s=u.reg_read(UC_X86_REG_ESP)
  if a in [stop,0x10487aa9+delta]:u.emu_stop()
  elif a==M['engine']['count_trampoline']+delta:state['fallback']=True;u.emu_stop()
  elif a==ctor:
   name=readstr(u,get(u,s+4));n=len(state['names'])+1;state['names'][n]=name;put(u,u.reg_read(UC_X86_REG_ECX),n);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+12)
  elif a==setskin:
   assert u.reg_read(UC_X86_REG_ECX)==actor;part,name,index=[get(u,s+4+i*4) for i in range(3)];state['skins'].append((part,index,state['names'].get(name)));u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+16)
 u.hook_add(UC_HOOK_CODE,hook)
 for race in range(14):
  for hair in range(-1,12):
   item=next((x for x in M['tanda2'] if x['race_index']==race and x['index']==hair),None)
   for part in range(16):
    state.clear();put(u,pawn+0x698,race);put(u,user+0x240,hair);u.mem_write(stack,struct.pack('<2I',stop,part));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,user)
    for i,r in enumerate(regs):u.reg_write(r,0x123000+i)
    u.emu_start(M['engine']['count_hook']+delta,stop+1,count=500)
    expected=None if not item or part not in [4,5] else (len(item['materials']) if part==5 else 0)
    if expected is None:assert state.get('fallback') and u.reg_read(UC_X86_REG_ESP)==stack
    else:assert not state.get('fallback') and u.reg_read(UC_X86_REG_EAX)==expected;assert u.reg_read(UC_X86_REG_ESP)==stack+8
    assert [u.reg_read(r) for r in regs]==[0x123000+i for i in range(4)];tests+=1
 # Replay the shipped native material loop at 10487a65, not a simulated loop.
 for item in M['tanda2']:
  for part in [4,5]:
   for color in range(4):
    state.clear();state.update(names={},skins=[]);put(u,pawn+0x698,item['race_index']);put(u,user+0x240,item['index']);put(u,user+0x244,color);put(u,user+0x248,0);put(u,frame-0x14,user)
    u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EBP,frame);u.reg_write(UC_X86_REG_ESI,actor);u.reg_write(UC_X86_REG_EDI,part);u.reg_write(UC_X86_REG_EBX,user)
    u.emu_start(0x10487a65+delta,0x10487aa9+delta+1,count=5000)
    expected=[(5,i,name) for i,name in enumerate(item['materials'])] if part==5 else []
    assert not state.get('fallback') and state['skins']==expected,(item['model'],item['letter'],part,state,expected)
    assert u.reg_read(UC_X86_REG_ESP)==stack;assert u.reg_read(UC_X86_REG_EBP)==frame;replays+=1
(D/'render-pipeline-test-results.json').write_text(json.dumps(dict(count_cases=tests,shipped_native_loop_replays=replays,all_materials_bound=True,relocation_and_abi=True,original_and_tanda1_count_fallback=True),indent=2),encoding='utf8')
print('PASS',tests,'count/ABI cases and',replays,'actual native material-loop replays; all active skins receive their own FinalBlend.')
