import pathlib,json,hashlib,re
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];live=ROOT/'server/game';stage=D/'stage/server';geo=json.loads((D/'geodata-audit.json').read_text());ct=geo['spawns']['ct'][0];t=geo['spawns']['t'][0]
def put(rel,text):p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
text=(D/'Dust2Arena.java').read_text().replace('@CT@',','.join(map(str,ct))).replace('@T@',','.join(map(str,t)))
put('data/scripts/custom/Dust2Arena/Dust2Arena.java',text)
rel='config/Custom/WorldContent.ini';hashes=[]
for label,root in [('live',live),('source',ROOT/'source/L2J_Mobius_CT_0_Interlude/dist/game'),('cloud',ROOT/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude/dist/game')]:
 p=root/rel;text=p.read_text();assert 'Dust2Arena' not in text
 text,n=re.subn(r'(?m)^(CustomScriptFolders\s*=\s*)([^\r\n]+)',lambda m:m[1]+m[2]+';Dust2Arena',text);assert n==1
 q=D/'mirror-configs'/label/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text)
 hashes.append(dict(target=str(p),stage=str(q),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(D/'server-source-hashes.json').write_text(json.dumps(hashes,indent=2))
lo=[int(b[0])-64 for b in geo['bounds']];hi=[int(b[1])+64 for b in geo['bounds']]
races='\n'.join('  <race name="'+r+'" point="gludio_sky" />' for r in ['HUMAN','ELF','DARK_ELF','ORC','DWARF'])
put('data/zones/dust2_arena.xml',f'''<?xml version="1.0" encoding="UTF-8"?>
<list enabled="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../xsd/zones.xsd">
 <zone name="Dust2 Exploration Peace" type="PeaceZone" shape="Cuboid" minZ="{lo[2]-100}" maxZ="{hi[2]+100}">
  <node X="{lo[0]}" Y="{lo[1]}" /><node X="{hi[0]}" Y="{hi[1]}" />
 </zone>
 <zone name="Dust2 Exploration Respawn" type="RespawnZone" shape="Cuboid" minZ="{lo[2]-100}" maxZ="{hi[2]+100}">
  <node X="{lo[0]}" Y="{lo[1]}" /><node X="{hi[0]}" Y="{hi[1]}" />
{races}
 </zone>
</list>
''')
print('Dust2 commands and exploration peace/respawn zones staged',ct,t)
