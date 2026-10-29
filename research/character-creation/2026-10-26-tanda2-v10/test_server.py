from pathlib import Path
import re,itertools,json
D=Path(__file__).resolve().parent;text=(D/'CharacterCreate.javap.txt').read_text(encoding='utf-8-sig').split('protected void runImpl();',1)[1].split('private ',1)[0];code={};switch={}
for line in text.splitlines():
 m=re.match(r'\s*(\d+):\s+(\w+)\s*(.*)',line)
 if m:code[int(m[1])]=(m[2],m[3])
block=text.split('lookupswitch',1)[1].split('}',1)[0]
for key,dest in re.findall(r'(\d+|default):\s*(\d+)',block):switch[key]=int(dest)
offsets=sorted(code);nxt=dict(zip(offsets,offsets[1:]));tests=0
def run(fields):
 pc=169;stack=[];locals={}
 for _ in range(150):
  if pc in [184,387,431]:return False
  if pc==460:return True
  op,arg=code[pc];dest=nxt[pc]
  if op=='aload_0':stack.append('this')
  elif op=='getfield':assert stack.pop()=='this';stack.append(fields[re.search(r'Field (\w+):',arg)[1]])
  elif op.startswith('iconst_'):stack.append(int(op[7:]))
  elif op in ['bipush','sipush']:stack.append(int(arg))
  elif op=='goto':dest=int(arg)
  elif op=='lookupswitch':dest=switch.get(str(stack.pop()),switch['default'])
  elif op.startswith('istore_'):locals[int(op[-1])]=stack.pop()
  elif op.startswith('iload_'):stack.append(locals[int(op[-1])])
  elif op.startswith('if'):
   a=stack.pop();b=stack.pop() if op.startswith('if_icmp') else 0;suffix=op[7:] if op.startswith('if_icmp') else op[2:]
   yes={'gt':b>a,'le':b<=a,'lt':b<a,'ge':b>=a,'eq':b==a,'ne':b!=a}[suffix] if op.startswith('if_icmp') else {'gt':a>0,'le':a<=0,'lt':a<0,'ge':a>=0,'eq':a==0,'ne':a!=0}[suffix]
   if yes:dest=int(arg)
  else:raise AssertionError((pc,op,arg))
  pc=dest
 raise AssertionError('loop')
# Independent expectation from the agreed model selection.
male={0:6,10:6,18:8,25:8,31:7,38:7,44:7,49:7,53:6};female={0:8,10:8,18:8,25:8,31:8,38:8,44:9,49:8,53:9}
for cls,sex,face,hair,color in itertools.product(male,[0,1],range(-1,8),range(-1,13),range(-1,6)):
 maximum=(female if sex else male)[cls];expected=0<=face<=5 and 0<=hair<=maximum and 0<=color<=3
 result=run(dict(_classId=cls,_isFemale=sex,_face=face,_hairStyle=hair,_hairColor=color));assert result==expected,(cls,sex,face,hair,color,result,expected);tests+=1
(D/'server-test-results.json').write_text(json.dumps(dict(passed=tests,compiled_bytecode=True,all_creation_roots=True,no_database_writes=True),indent=2))
print('PASS',tests,'actual Java bytecode validation cases; no characters or database touched.')
