"""Execute the exact staged x86 hooks, checking resource names and ABI."""
from pathlib import Path
import json,struct,pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
D=Path(__file__).resolve().parent
M=json.loads((D/'native-manifest.json').read_text())
def put(u,a,v):u.mem_write(a,struct.pack('<I',v))
def get(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
R=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
tests=0
for delta in [0,0x02000000]:
 p=pefile.PE(str(D/'stage/engine.dll'));base=p.OPTIONAL_HEADER.ImageBase+delta
 u=Uc(UC_ARCH_X86,UC_MODE_32);img=p.get_memory_mapped_image();u.mem_map(base,(len(img)+4095)//4096*4096);u.mem_write(base,img)
 u.mem_map(0x40000000,0x100000);user=0x40001000;pawn=0x40003000;stack=0x40010000;out=0x40005000;ctor=0x40006000;stop=0x40007000
 put(u,user+0x204,pawn);put(u,base+(0x11d8d988-p.OPTIONAL_HEADER.ImageBase),ctor)
 state={}
 def hook(u,a,size,data):
  if a in [M['engine']['mesh_trampoline']+delta,M['engine']['texture_trampoline']+delta]:state['fallback']=True;u.emu_stop()
  elif a==stop:u.emu_stop()
  elif a==ctor:
   s=u.reg_read(UC_X86_REG_ESP);ptr=get(u,s+4);raw=bytearray()
   while u.mem_read(ptr,2)!=b'\0\0':raw+=u.mem_read(ptr,2);ptr+=2
   state['name']=raw.decode('utf-16le');put(u,u.reg_read(UC_X86_REG_ECX),1234);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+12)
 u.hook_add(UC_HOOK_CODE,hook)
 def run(kind,race,hair,face,color,slot,expected,tex=0,npc=0):
  global tests
  state.clear();put(u,user+8,npc);put(u,pawn+0x698,race);put(u,user+0x240,hair);put(u,user+0x244,color);put(u,user+0x248,face);put(u,out,0xdeadbeef)
  u.mem_write(stack,struct.pack('<4I',stop,out,slot,tex));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,user)
  for i,r in enumerate(R):u.reg_write(r,0x123000+i)
  u.emu_start(M['engine'][kind+'_hook']+delta,stop+1,count=500)
  assert [u.reg_read(r) for r in R]==[0x123000+i for i in range(4)],state
  if expected=='fallback':assert state.get('fallback') and u.reg_read(UC_X86_REG_ESP)==stack and u.reg_read(UC_X86_REG_ECX)==user,state
  else:
   assert not state.get('fallback'),state
   assert state.get('name')==expected,(kind,race,hair,face,color,slot,state,expected)
   assert get(u,out)==(1234 if expected else 0)
   assert u.reg_read(UC_X86_REG_ESP)==stack+(12 if kind=='mesh' else 16)
   assert u.reg_read(UC_X86_REG_EAX)==out
  tests+=1
 for race,name in enumerate(M['race_names']):
  old=M['original_hair_counts'][race]
  for hair in range(old):
   for slot in [4,5,9,0,7]:
    for kind in ['mesh','texture']:run(kind,race,hair,0,0,slot,'fallback')
  for h in range(2):
   run('mesh',race,old+h,0,0,5,f'NexusAppearanceV1.{name}_Hair{h+1}')
   run('mesh',race,old+h,0,0,4,None)
   for c in range(4):run('texture',race,old+h,0,c,5,f'NexusHairGRepairV12.MDarkElf_G_Color{c}' if race==2 and h==1 else f'NexusHairMaterialsV2.{name}_Hair{h+1}_Color{c}')
   run('texture',race,old+h,0,0,5,None,tex=1)
   run('texture',race,old+h,0,4,5,None)
  for face in range(3,6):
   run('texture',race,0,face,0,9,'MOrc.MOrc_m000_t00_f' if race==10 else f'NexusAppearanceV1.{name}_Face{face}')
   run('mesh',race,0,face,0,9,'NexusDarkFaceV7.MDarkElf_ModernFace' if race==2 else 'Orc.MOrc_m000_f' if race==10 else 'fallback')
 run('mesh',14,5,0,0,5,'fallback');run('mesh',0,5,0,0,5,'NexusAppearanceV1.MFighter_Hair1',npc=1)

# Simulate the unchanged original UI routine and actual append function boundary.
p=pefile.PE(str(D/'stage/NWindow.dll'));base=p.OPTIONAL_HEADER.ImageBase;u=Uc(UC_ARCH_X86,UC_MODE_32);img=p.get_memory_mapped_image();u.mem_map(base,(len(img)+4095)//4096*4096);u.mem_write(base,img)
u.mem_map(0x40000000,0x100000);obj=0x40001000;hair=0x40003000;face=0x40005000;stack=0x40010000;stop=0x40007000
put(u,obj+0x1d8,hair);put(u,obj+0x1e0,face);state={}
def ui_hook(u,a,size,data):
 s=u.reg_read(UC_X86_REG_ESP)
 if a==stop:u.emu_stop()
 elif a==M['ui']['selector_trampoline']:
  put(u,hair+0x2f4,state['count']);put(u,face+0x2f4,state['faces']);u.reg_write(UC_X86_REG_EAX,987);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+8)
 elif a==M['ui']['add_choice_function']:
  ctrl=u.reg_read(UC_X86_REG_ECX);state['added'].append((ctrl,get(u,s+4)));put(u,ctrl+0x2f4,get(u,ctrl+0x2f4)+1);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+8)
u.hook_add(UC_HOOK_CODE,ui_hook)
for count,faces in [(5,3),(7,3),(9,6)]:
 put(u,obj+0x1f8,1 if count==7 else 0)
 state=dict(count=count,faces=faces,added=[]);u.mem_write(stack,struct.pack('<2I',stop,1));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,obj);u.reg_write(UC_X86_REG_EBX,123)
 u.emu_start(M['ui']['selector_hook'],stop+1,count=500)
 assert get(u,hair+0x2f4)==(count+2 if count in [5,7] else count)
 assert get(u,face+0x2f4)==6
 assert u.reg_read(UC_X86_REG_EAX)==987 and u.reg_read(UC_X86_REG_EBX)==123 and u.reg_read(UC_X86_REG_ESP)==stack+8
 assert state['added']==([(hair,28000),(hair,28001),(face,182),(face,186),(face,187)] if faces==3 else [])
 tests+=1
(D/'native-test-results.json').write_text(json.dumps(dict(passed=tests,original_fallback=True,relocated_engine=True,abi_preserved=True,selector_counts=True),indent=2))
print('PASS',tests,'x86 resource/selector/ABI scenarios, including relocated engine')
