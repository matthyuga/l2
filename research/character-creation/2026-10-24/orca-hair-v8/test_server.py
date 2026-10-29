"""Interpret compiled validation bytecode only; no server, account or DB writes."""
from pathlib import Path
import re,itertools,json
D=Path(__file__).resolve().parent
text=(D/'CharacterCreate.javap.txt').read_text(encoding='utf-16').split('protected void runImpl();',1)[1].split('private ',1)[0]
code={}
for line in text.splitlines():
 m=re.match(r'\s*(\d+):\s+(\w+)\s*(.*)',line)
 if m:code[int(m[1])]=(m[2],m[3])
offsets=sorted(code);nextpc=dict(zip(offsets,offsets[1:]));tests=0
def execute(fields):
 pc=169;stack=[]
 for _ in range(100):
  if pc in (184,252,296):return False
  if pc==325:return True
  op,arg=code[pc];dest=nextpc[pc]
  if op=='aload_0':stack.append('this')
  elif op=='getfield':assert stack.pop()=='this';stack.append(fields[re.search(r'Field (\w+):',arg)[1]])
  elif op.startswith('iconst_'):stack.append(int(op[7:]))
  elif op=='bipush':stack.append(int(arg))
  elif op=='goto':dest=int(arg)
  elif op.startswith('if_') or op in ['ifge','iflt','ifeq','ifne']:
   a=stack.pop();b=stack.pop() if op.startswith('if_icmp') else 0
   suffix=op[7:] if op.startswith('if_icmp') else op[2:]
   yes={'gt':b>a,'le':b<=a,'lt':b<a,'ge':b>=a,'eq':b==a,'ne':b!=a}[suffix] if op.startswith('if_icmp') else {'gt':a>0,'le':a<=0,'lt':a<0,'ge':a>=0,'eq':a==0,'ne':a!=0}[suffix]
   if yes:dest=int(arg)
  else:raise AssertionError((pc,op,arg))
  pc=dest
 raise AssertionError('Infinite validation')
for cls,female,face,hair,color in itertools.product([0,10,18,25,31,38,44,49,53],[0,1],range(-1,8),range(-1,11),range(-1,6)):
 expected=0<=face<6 and 0<=color<4 and 0<=hair<(7 if not female else 9)
 result=execute(dict(_classId=cls,_isFemale=female,_face=face,_hairStyle=hair,_hairColor=color))
 assert result==expected,(cls,female,face,hair,color,result,expected)
 tests+=1
(D/'server-test-results.json').write_text(json.dumps(dict(passed=tests,compiled_bytecode=True,no_database_writes=True),indent=2))
print('PASS',tests,'compiled server validation scenarios')
