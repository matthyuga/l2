from pathlib import Path
import pefile,capstone,json,re,struct,hashlib
ROOT=Path(__file__).resolve().parent
P=Path('E:/l2/system-hud/engine.dll');b=P.read_bytes();pe=pefile.PE(data=b);base=pe.OPTIONAL_HEADER.ImageBase
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
def read(va,n):
 off=pe.get_offset_from_rva(va-base);return b[off:off+n]
def resolve(va):
 chain=[]
 for _ in range(6):
  i=next(cs.disasm(read(va,16),va));chain.append(hex(va))
  if i.mnemonic=='jmp' and i.operands[0].type==capstone.x86.X86_OP_IMM:va=i.operands[0].imm
  else:break
 return va,chain
exports={e.name.decode('ascii','replace'):base+e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name and not e.forwarder}
requested=[name for name in exports if re.search(r'GetSunLightDirection|GetSunModifierInfo|GetMoonModifierInfo|GetSunColor@UL2NEnvLight|GetSunScale@UL2NEnvLight|GetSkyBoxColor@UL2NEnvLight|OnRedSky@',name)]
records=[]
for name in requested:
 va,chain=resolve(exports[name]);instructions=[];constants=[]
 for i in cs.disasm(read(va,1800),va):
  instructions.append({'va':hex(i.address),'bytes':i.bytes.hex(),'asm':i.mnemonic+' '+i.op_str})
  for op in i.operands:
   if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index:
    addr=op.mem.disp&0xffffffff
    try:
     raw=read(addr,8);constants.append({'va':hex(addr),'raw':raw.hex(),'float32':struct.unpack('<f',raw[:4])[0],'float64':struct.unpack('<d',raw)[0]})
    except Exception:pass
  if i.mnemonic.startswith('ret') or len(instructions)>=200:break
 records.append({'export':name,'export_va':hex(exports[name]),'jump_chain':chain,'resolved_va':hex(va),'instructions':instructions,'constant_candidates':constants,'coverage':'linear disassembly until first ret or 200 instructions; not full CFG or runtime'})
out={'target':str(P),'sha256':hashlib.sha256(b).hexdigest(),'tool':'Python pefile/capstone (not REA Evidence)','functions':records}
(ROOT/'native-function-views.json').write_text(json.dumps(out,indent=2,allow_nan=True),encoding='utf8')
for f in records:
 print('\n'+f['export']+' => '+f['resolved_va'])
 print('\n'.join(i['va']+' '+i['asm'] for i in f['instructions'][:95]))
