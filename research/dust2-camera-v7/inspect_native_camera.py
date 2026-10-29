from pathlib import Path
import pefile,capstone
D=Path(__file__).resolve().parent
p=pefile.PE('E:/l2/system-hud/Engine.dll');base=p.OPTIONAL_HEADER.ImageBase
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
es={base+s.address:s.name.decode() for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
def target(a):
 i=next(md.disasm(p.get_data(a-base,16),a),None)
 if i is None:return a
 return int(i.op_str,16) if i.mnemonic=='jmp' and i.op_str.startswith('0x') else a
es.update({target(a):n for a,n in list(es.items())})
for part in ['CalcVolumeCamera@ALineage','CalcBehindView@ALineage','PlayerCalcView@ALineage','SingleLineCheck@ULevel','L2SingleLineCheck@ULevel','ActorLineCheck@FCollisionOctree','ActorZeroExtentLineCheck@FOctreeNode','ActorNonZeroExtentLineCheck@FOctreeNode','ShouldTrace@AActor']:
 a=next(a for a,n in es.items() if n.startswith('?'+part));a=target(a);out=[]
 end=min((addr for addr in es if addr>a),default=a+15000)
 for i in md.disasm(p.get_data(a-base,end-a),a):
  annotation=''
  if i.mnemonic=='call' and i.op_str.startswith('0x'):annotation=es.get(int(i.op_str,16),'')
  out.append(f'{i.address:x} {i.mnemonic} {i.op_str} {annotation}')
 f=D/(part.split('@')[0]+'.asm.txt');f.write_text('\n'.join(out));print(f.name,len(out))
