"""Version-bound, additive PE patches for the native appearance selectors.

Original routines remain the fallback. New section code uses module-relative
addresses and preserves nonvolatile registers. Nothing is installed here.
"""
from pathlib import Path
import json,hashlib,struct,pefile
from keystone import Ks,KS_ARCH_X86,KS_MODE_32
ROOT=Path(__file__).resolve().parent
STAGE=ROOT/'stage';STAGE.mkdir(exist_ok=True)
RACES=['MFighter','FFighter','MDarkElf','FDarkElf','MDwarf','FDwarf','MElf','FElf','MMagic','FMagic','MOrc','FOrc','MShaman','FShaman']
BASE=[5,7,5,7,5,7,5,7,5,7,5,7,5,7]
EXPECTED={'engine.dll':'508974c711f207402719e92737e211a2f029c95c2f68fc0e1c31fcbb9dbb232d','NWindow.dll':'cb85f7a5de375f1e9156ec6559aae2a0a809b3abac4150142aafb14bbf02b47b'}
def sha(b):return hashlib.sha256(b).hexdigest()
def align(v,a):return (v+a-1)//a*a
def asm(s,addr):return bytes(Ks(KS_ARCH_X86,KS_MODE_32).asm(s,addr)[0])
class Patch:
 def __init__(self,name):
  self.name=name;self.original=Path('E:/l2-local/backups/character-appearance-20261024-005140',('0-' if name=='engine.dll' else '1-')+name).read_bytes();assert sha(self.original)==EXPECTED[name],('Unrecognized native build',name)
  self.pe=pefile.PE(data=self.original);self.base=self.pe.OPTIONAL_HEADER.ImageBase;self.data=bytearray(self.original);self.records=[]
  last=self.pe.sections[-1]
  self.raw=align(max(len(self.original),last.PointerToRawData+last.Misc_VirtualSize,last.PointerToRawData+last.SizeOfRawData),self.pe.OPTIONAL_HEADER.SectionAlignment)
  self.rva=last.VirtualAddress+self.raw-last.PointerToRawData
  self.section=bytearray(0x6000)
 def put(self,offset,b):assert offset+len(b)<=len(self.section);self.section[offset:offset+len(b)]=b;return self.base+self.rva+offset
 def patch(self,va,b,expected=None):
  off=self.pe.get_offset_from_rva(va-self.base);old=bytes(self.data[off:off+len(b)])
  if expected is not None:assert old==expected,(hex(va),old.hex(),expected.hex())
  self.data[off:off+len(b)]=b;self.records.append(dict(va=hex(va),offset=off,before=old.hex(),after=b.hex()))
 def hook(self,va,target,length):
  off=self.pe.get_offset_from_rva(va-self.base);old=bytes(self.data[off:off+length]);assert old[:5]==bytes.fromhex('558bec6aff') if self.name=='engine.dll' else old==bytes.fromhex('535556578bf1')
  self.patch(va,asm(f'jmp {target}',va)+b'\x90'*(length-5),old);return old
 def finish(self):
  last=self.pe.sections[-1]
  # Extend the final section without overwriting padding used by the packed image.
  # The original relocation directory range stays exactly the same.
  raw=self.raw;self.data+=bytes(raw-len(self.data))
  self.data+=self.section
  size=len(self.data)-last.PointerToRawData
  struct.pack_into('<I',self.data,last.get_field_absolute_offset('Misc_VirtualSize'),size)
  struct.pack_into('<I',self.data,last.get_field_absolute_offset('SizeOfRawData'),size)
  struct.pack_into('<I',self.data,last.get_field_absolute_offset('Characteristics'),(last.Characteristics|0x20000000)&~0x02000000)
  struct.pack_into('<I',self.data,self.pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(self.rva+len(self.section),self.pe.OPTIONAL_HEADER.SectionAlignment))
  struct.pack_into('<I',self.data,self.pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),0)
  # All pre-existing bytes except explicit hook/header fields remain unchanged.
  path=STAGE/self.name;path.write_bytes(self.data);pe=pefile.PE(str(path));assert pe.get_offset_from_rva(self.rva)==raw
  return dict(name=self.name,original_sha256=sha(self.original),patched_sha256=sha(self.data),base=self.base,section_rva=self.rva,section_raw=raw,section_size=len(self.section),patches=self.records)
def engine():
 p=Patch('engine.dll');start=p.base+p.rva
 p.put(0x2000,bytes(BASE))
 def table(offset,names):
  for i,name in enumerate(names):
   b=(name+'\0').encode('utf-16le');assert len(b)<=128;p.put(offset+i*128,b)
 table(0x2100,[f'NexusAppearanceV1.{r}_Hair{v+1}' for r in RACES for v in range(2)])
 table(0x3100,[f'NexusHairMaterialsV2.{r}_Hair{v+1}_Color{c}' for r in RACES for v in range(2) for c in range(4)])
 # 112*128 extends to 0x6900; allocate enough section space before filling tables.
 return p
def build_engine():
 p=Patch('engine.dll');p.section=bytearray(0x9000);start=p.base+p.rva
 p.put(0x2000,bytes(BASE))
 def table(offset,names):
  for i,name in enumerate(names):
   b=(name+'\0').encode('utf-16le');assert len(b)<=128;p.put(offset+i*128,b)
 table(0x2100,[f'NexusAppearanceV1.{r}_Hair{v+1}' for r in RACES for v in range(2)])
 table(0x3100,[f'NexusHairMaterialsV2.{r}_Hair{v+1}_Color{c}' for r in RACES for v in range(2) for c in range(4)])
 table(0x6a00,[f'NexusAppearanceV1.{r}_Face{v+3}' for r in RACES for v in range(3)])
 p.put(0x8100,('NexusDarkFaceV7.MDarkElf_ModernFace'+'\0').encode('utf-16le'))
 mesh_entry=0x10482c90;tex_entry=0x10486000
 for kind,entry,offset,tramp in [('mesh',mesh_entry,0,0x1000),('texture',tex_entry,0x600,0x1100)]:
  va=start+offset
  prologue=f'''push ebx; push esi; push edi; push ebp; mov ebx,ecx;
   call anchor; anchor: pop ebp; sub ebp,{p.rva+offset+10};
   
   mov eax,dword ptr [ebx+0x204]; test eax,eax; je fallback; mov edx,dword ptr [eax+0x718]; test edx,edx; je actual_pawn; mov eax,edx; actual_pawn:
   mov edi,dword ptr [eax+0x698]; cmp edi,14; jae fallback;
   mov eax,dword ptr [esp+24];'''
  if kind=='texture':
   body='''cmp eax,9; je face;'''
  else:body=f"""cmp eax,9; jne mesh_hair; cmp edi,2; jne fallback;
   mov esi,dword ptr [ebx+0x248]; sub esi,3; cmp esi,3; jae fallback;
   lea edx,[ebp+{p.rva+0x8100}]; jmp named; mesh_hair:"""
  body+=f'''cmp eax,4; je hair; cmp eax,5; jne fallback;
   hair: mov esi,dword ptr [ebx+0x240]; movzx edx,byte ptr [ebp+edi+{p.rva+0x2000}];
   sub esi,edx; cmp esi,2; jae fallback;
   cmp eax,4; je empty;
   lea edx,[edi*2]; add edx,esi;'''
  if kind=='texture':
   body+=f'''cmp dword ptr [esp+28],0; jne empty;
    mov eax,dword ptr [ebx+0x244]; cmp eax,4; jae empty;
    shl edx,2; add edx,eax; shl edx,7; lea edx,[ebp+edx+{p.rva+0x3100}]; jmp named;
    face: mov esi,dword ptr [ebx+0x248]; sub esi,3; cmp esi,3; jae fallback;
    cmp dword ptr [esp+28],0; jne empty;
    lea edx,[edi+edi*2]; add edx,esi; shl edx,7; lea edx,[ebp+edx+{p.rva+0x6a00}];'''
  else:body+=f'shl edx,7; lea edx,[ebp+edx+{p.rva+0x2100}];'
  ret=8 if kind=='mesh' else 12
  tail=f'''named: mov edi,dword ptr [esp+20]; push 1; push edx; mov ecx,edi;
   call dword ptr [ebp+{0x11d8d988-p.base}]; mov eax,edi; jmp done;
   empty: mov eax,dword ptr [esp+20]; mov dword ptr [eax],0;
   done: pop ebp; pop edi; pop esi; pop ebx; ret {ret};
   fallback: mov ecx,ebx; pop ebp; pop edi; pop esi; pop ebx; jmp {start+tramp};'''
  code=asm(prologue+body+tail,va);assert len(code)<0x600
  # call anchor pushes the address ten bytes after entry: four pushes, mov, call.
  # Four pushes=4 bytes, mov=2, call=5 => the return address is entry+11.
  code=asm((prologue+body+tail).replace(f'sub ebp,{p.rva+offset+10}',f'sub ebp,{p.rva+offset+11}'),va)
  p.put(offset,code);old=p.hook(entry,va,5)
  p.put(tramp,old+asm(f'jmp {entry+5}',start+tramp+5))
 result=p.finish();result.update(mesh_hook=start,texture_hook=start+0x600,mesh_trampoline=start+0x1000,texture_trampoline=start+0x1100,expected_abi='thiscall; hidden FName return pointer; mesh ret8 / texture ret12')
 return result
def build_ui():
 p=Patch('NWindow.dll');start=p.base+p.rva
 entry=0x10199630;tramp=start+0x800;append=0x10198e40
 code=asm(f'''push ebx; mov ebx,ecx; push dword ptr [esp+8]; call {tramp}; push eax;
  mov ecx,dword ptr [ebx+0x1d8]; cmp dword ptr [ecx+0x2f4],5; je hair;
  cmp dword ptr [ecx+0x2f4],7; jne faces;
  hair: push 28000; call {append}; mov ecx,dword ptr [ebx+0x1d8]; push 28001; call {append};
  faces: mov ecx,dword ptr [ebx+0x1e0]; cmp dword ptr [ecx+0x2f4],3; jne done;
  push 0xb6; call {append}; mov ecx,dword ptr [ebx+0x1e0]; push 0xba; call {append};
  mov ecx,dword ptr [ebx+0x1e0]; push 0xbb; call {append};
  done: pop eax; pop ebx; ret 4;''',start)
 p.put(0,code);old=p.hook(entry,start,6);p.put(0x800,old+asm(f'jmp {entry+6}',tramp+6))
 # The native selector indexes a fixed FString array; custom labels bypass it.
 labels=start+0x1400
 for i,letter in enumerate('FGHI'):p.put(0x1400+i*32,('Type '+letter+'\0').encode('utf-16le'))
 draw=0x10197507;resume=0x1019751c;helper=start+0x1000
 code=asm(f"""call origin; origin: pop ecx; sub ecx,{p.rva+0x1000+5};
 cmp eax,28000; jb native_label; cmp eax,28001; ja native_label;
 mov eax,dword ptr [esi+0x2ec]; sub eax,5; cmp eax,3; ja empty_label; shl eax,5; lea eax,[ecx+eax+{p.rva+0x1400}]; jmp {resume};
 empty_label: lea eax,[ecx+{p.rva+0x1500}]; jmp {resume};
 native_label: push ebp; mov ebp,ecx; lea edx,[eax+eax*2]; mov eax,dword ptr [ebp+0x22c790]; lea ecx,[eax+edx*4+0x6a8dc]; call dword ptr [ebp+0x22c3e4]; pop ebp; jmp {resume};""",helper)
 p.put(0x1000,code);p.patch(draw,asm(f'jmp {helper}',draw)+b'\x90'*16,bytes.fromhex('8d1440a190c722108d8c90dca80600ff15e4c32210'))
 result=p.finish();result.update(selector_hook=start,selector_trampoline=tramp,add_choice_function=append,new_hair_label_ids=[28000,28001]);return result
def main():
 data=dict(engine=build_engine(),ui=build_ui(),race_names=RACES,original_hair_counts=BASE,new_hair_counts=[x+2 for x in BASE],original_face_count=3,new_face_count=6)
 (ROOT/'native-manifest.json').write_text(json.dumps(data,indent=2),encoding='utf8');print('BUILT native engine and creator selector patches')
if __name__=='__main__':main()
