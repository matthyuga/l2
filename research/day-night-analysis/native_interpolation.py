from native_functions import P,b,pe,base,cs,read,resolve,exports,ROOT
import json,capstone,struct
reverse={v:k for k,v in exports.items()}
imports={i.address:(d.dll.decode()+':'+(i.name.decode() if i.name else '#'+str(i.ordinal))) for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports}
def cfg(start,budget=450,span=8192):
 pending=[start];seen={};unknown=[]
 while pending and len(seen)<budget:
  va=pending.pop()
  while va not in seen and len(seen)<budget:
   if va<start or va>=start+span:unknown.append(hex(va));break
   ins=next(cs.disasm(read(va,16),va),None)
   if not ins:unknown.append(hex(va));break
   row={'va':hex(ins.address),'asm':ins.mnemonic+' '+ins.op_str,'bytes':ins.bytes.hex()}
   for op in ins.operands:
    if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index:
     addr=op.mem.disp&0xffffffff
     if addr in imports:row['import']=imports[addr]
     elif ins.mnemonic.startswith(('fld','fmul','fdiv','fsub','fcom')):
      try:
       raw=read(addr,op.size);row.setdefault('constants',[]).append({'va':hex(addr),'bytes':op.size,'value':struct.unpack('<d' if op.size==8 else '<f',raw)[0]})
      except Exception:pass
   seen[va]=row
   if ins.mnemonic.startswith('ret') or ins.mnemonic in ('int3','hlt'):break
   if ins.group(capstone.CS_GRP_JUMP):
    if ins.operands[0].type==capstone.x86.X86_OP_IMM:pending.append(ins.operands[0].imm)
    else:unknown.append(ins.op_str)
    if ins.mnemonic=='jmp':break
   va+=ins.size
 return {'entry':hex(start),'instructions':list(sorted(seen.values(),key=lambda x:int(x['va'],16))),'unresolved_or_out_of_scope':unknown,'budget':budget,'span_limit':span,'calls_followed':False}
records={}
vtable=exports['??_7UL2NEnvLight@@6B@']
for offset in [0xa4,0xb4]:
 va=struct.unpack('<I',read(vtable+offset,4))[0];resolved,chain=resolve(va)
 name=reverse.get(va,'vtable_'+hex(offset));records[name]={'pointer_va':hex(vtable+offset),'jump_chain':chain,**cfg(resolved)}
for name in exports:
 if any(x in name for x in ['GetSunLightDirection@ANMovableSunLight','GetSunModifierInfo@','GetMoonModifierInfo@','ChangeEnv@UL2NEnvManager','GetEnvColor@UL2NEnvManager','CalcEnvDelta@UL2NEnvManager','SetNTime@UL2NEnvManager','IsDay@UL2NEnvManager','SetShadowTick@UL2NEnvManager']):
  va,chain=resolve(exports[name]);records[name]={'jump_chain':chain,**cfg(va)}
out={'tool':'ordinary pefile/capstone static CFG; no REA Evidence or execution','target':str(P),'functions':records}
(ROOT/'native-interpolation-cfg.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf8')
for name,record in records.items():
 print('\nFUNCTION',name,record['entry'],len(record['instructions']),'instructions','unresolved',record['unresolved_or_out_of_scope'])
 print('\n'.join(i['va']+' '+i['asm']+(' '+str(i.get('constants') or i.get('import')) if i.get('constants') or i.get('import') else '') for i in record['instructions']))
