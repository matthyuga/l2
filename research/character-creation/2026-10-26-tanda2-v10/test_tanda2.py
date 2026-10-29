from pathlib import Path
import json,struct,pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
D=Path(__file__).resolve().parent;M=json.loads((D/'native-manifest.json').read_text());tests=0
def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def string(u,a):
 out=bytearray()
 while u.mem_read(a,2)!=b'\0\0':out+=u.mem_read(a,2);a+=2
 return out.decode('utf-16le')
regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
for delta in [0,0x02000000]:
 p=pefile.PE(str(D/'stage/engine.dll'));base=p.OPTIONAL_HEADER.ImageBase+delta;img=p.get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(len(img)+4095)//4096*4096);u.mem_write(base,img);u.mem_map(0x40000000,0x100000)
 user=0x40001000;pawn=0x40003000;out=0x40005000;ctor=0x40006000;stop=0x40007000;stack=0x40010000
 put(u,user+0x204,pawn);put(u,base+(0x11d8d988-p.OPTIONAL_HEADER.ImageBase),ctor);state={}
 def hook(u,a,size,unused):
  if a in [M['engine']['mesh_trampoline']+delta,M['engine']['texture_trampoline']+delta]:state['fallback']=True;u.emu_stop()
  elif a==stop:u.emu_stop()
  elif a==ctor:
   s=u.reg_read(UC_X86_REG_ESP);state['name']=string(u,get(u,s+4));put(u,u.reg_read(UC_X86_REG_ECX),1234);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+12)
 u.hook_add(UC_HOOK_CODE,hook)
 for race in range(14):
  for hair in range(-1,12):
   selected=next((x for x in M['tanda2'] if x['race_index']==race and x['index']==hair),None)
   old=M['original_hair_counts'][race]
   if old<=hair<old+2:continue # independently checked by legacy suite
   for kind in ['mesh','texture']:
    for slot in [4,5]:
     for color in range(5):
      for tex in range(4) if kind=='texture' else [0]:
       expected='fallback'
       if selected:
        if slot==4:expected=None
        elif kind=='mesh':expected=selected['mesh']
        elif color>=4 or tex>=len(selected['materials']):expected=None
        else:expected=selected['materials'][tex]
       state.clear();put(u,pawn+0x698,race);put(u,user+0x240,hair);put(u,user+0x244,color);put(u,user+0x248,0);put(u,out,0xdeadbeef);u.mem_write(stack,struct.pack('<4I',stop,out,slot,tex));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,user)
       for i,r in enumerate(regs):u.reg_write(r,0x123000+i)
       u.emu_start(M['engine'][kind+'_hook']+delta,stop+1,count=600)
       assert [u.reg_read(r) for r in regs]==[0x123000+i for i in range(4)]
       if expected=='fallback':assert state.get('fallback') and u.reg_read(UC_X86_REG_ESP)==stack
       else:
        assert state.get('name')==expected and not state.get('fallback'),(race,hair,kind,slot,color,tex,state,expected)
        assert get(u,out)==(1234 if expected else 0);assert u.reg_read(UC_X86_REG_ESP)==stack+(12 if kind=='mesh' else 16)
       tests+=1
 # Per-model UI counts and ABI. Original routine boundary supplies real fields.
 p=pefile.PE(str(D/'stage/NWindow.dll'));base=p.OPTIONAL_HEADER.ImageBase+delta;img=p.get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(len(img)+4095)//4096*4096);u.mem_write(base,img);u.mem_map(0x40000000,0x100000)
 obj=0x40001000;hairctrl=0x40003000;facectrl=0x40005000;stop=0x40007000;stack=0x40010000;put(u,obj+0x1d8,hairctrl);put(u,obj+0x1e0,facectrl);state={}
 def ui_hook(u,a,size,unused):
  s=u.reg_read(UC_X86_REG_ESP)
  if a==stop:u.emu_stop()
  elif a==M['ui']['selector_trampoline']+delta:
   put(u,hairctrl+0x2f4,state['count']);put(u,facectrl+0x2f4,state['faces']);u.reg_write(UC_X86_REG_EAX,987);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+8)
  elif a==M['ui']['add_choice_function']+delta:
   ctrl=u.reg_read(UC_X86_REG_ECX);state['added'].append((ctrl,get(u,s+4)));put(u,ctrl+0x2f4,get(u,ctrl+0x2f4)+1);u.reg_write(UC_X86_REG_EIP,get(u,s));u.reg_write(UC_X86_REG_ESP,s+8)
 u.hook_add(UC_HOOK_CODE,ui_hook)
 for race in range(5):
  for archetype in range(2 if race<4 else 1):
   for female in [0,1]:
    model=([0,8][archetype] if race==0 else 6 if race==1 else 2 if race==2 else 10+archetype*2 if race==3 else 4)+female
    for fresh in [True,False]:
     count=(7 if female else 5) if fresh else M['new_hair_counts'][model]
     state=dict(count=count,faces=3 if fresh else 6,added=[]);put(u,obj+0x1f0,race);put(u,obj+0x1f4,archetype);put(u,obj+0x1f8,female);u.mem_write(stack,struct.pack('<2I',stop,female));u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ECX,obj)
     for i,r in enumerate(regs):u.reg_write(r,0x123000+i)
     u.emu_start(M['ui']['selector_hook']+delta,stop+1,count=1200)
     assert get(u,hairctrl+0x2f4)==M['new_hair_counts'][model],(race,archetype,female,fresh,state)
     expected=[(hairctrl,28000+i) for i in range(M['ui']['extra_counts'][model])]+[(facectrl,182),(facectrl,186),(facectrl,187)] if fresh else []
     assert state['added']==expected;assert get(u,facectrl+0x2f4)==6;assert u.reg_read(UC_X86_REG_EAX)==987;assert u.reg_read(UC_X86_REG_ESP)==stack+8;assert [u.reg_read(r) for r in regs]==[0x123000+i for i in range(4)];tests+=1
 # Actual renderer code, including relocated native FString fallback.
 game=0x40020000;ctor=0x40008000;data=0x40009000;put(u,base+0x22c790,game);put(u,base+0x22c3e4,ctor);u.mem_write(data,'Type A\0'.encode('utf-16le'))
 def labels(u,a,size,unused):
  if a==0x1019751c+delta:u.emu_stop()
  elif a==ctor:
   assert u.reg_read(UC_X86_REG_ECX)==game+179*12+0x6a8dc;s=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,data);u.reg_write(UC_X86_REG_ESP,s+4);u.reg_write(UC_X86_REG_EIP,get(u,s))
 u.hook_add(UC_HOOK_CODE,labels)
 for id,selection,expected in [(179,0,'Type A')]+[(28000+i%4,index,'Type '+chr(65+index)) for i,index in enumerate(range(5,11))]:
  put(u,hairctrl+0x2ec,selection);u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_ESI,hairctrl);u.reg_write(UC_X86_REG_EBP,1234);u.reg_write(UC_X86_REG_EAX,id);u.emu_start(0x10197507+delta,0x1019751c+delta+1,count=300)
  assert string(u,u.reg_read(UC_X86_REG_EAX))==expected;assert u.reg_read(UC_X86_REG_ESP)==stack;assert u.reg_read(UC_X86_REG_EBP)==1234;tests+=1
(D/'tanda2-test-results.json').write_text(json.dumps(dict(passed=tests,relocated_engine_and_ui=True,model_specific_counts=True,all_material_slots=True,abi_preserved=True),indent=2))
print('PASS',tests,'Tanda 2 x86 resource/selector/label/ABI cases')
