import pathlib,json,re,hashlib,shutil
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];OLD=ROOT/'research/dust2-integration';g=json.loads((D/'geodata-audit.json').read_text());bounds=g['bounds'];live=ROOT/'server/game';stage=D/'stage/server'
ct=g['spawns']['ct'][0];t=g['spawns']['t'][0];rel='data/scripts/custom/Dust2Arena/Dust2Arena.java';s=(live/rel).read_text(encoding='utf-8')
s,n=re.subn(r'private static final int\[\] CT=\{[^}]+\},T=\{[^}]+\};','private static final int[] CT={'+','.join(map(str,ct))+'},T={'+','.join(map(str,t))+'};',s);assert n==1
lo=[int(b[0])-64 for b in bounds];hi=[int(b[1])+64 for b in bounds]
s,n=re.subn(r'private static boolean inside\(Player p\)\{[^\n]+\}',f'private static boolean inside(Player p){{return p.getInstanceId()==0&&p.getX()>{lo[0]}&&p.getX()<{hi[0]}&&p.getY()>{lo[1]}&&p.getY()<{hi[1]}&&p.getZ()>{lo[2]-100}&&p.getZ()<{hi[2]+100};}}',s);assert n==1
p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
rel='data/zones/dust2_arena.xml';s=(live/rel).read_text(encoding='utf-8');s=re.sub(r'minZ="\d+"',f'minZ="{lo[2]-100}"',s);s=re.sub(r'maxZ="\d+"',f'maxZ="{hi[2]+100}"',s)
s,n=re.subn(r'<node X="\d+" Y="\d+" /><node X="\d+" Y="\d+" />',f'<node X="{lo[0]}" Y="{lo[1]}" /><node X="{hi[0]}" Y="{hi[1]}" />',s);assert n==2
p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
smoke=(OLD/'prepare_smoke.py').read_text(encoding='utf-8');(D/'prepare_smoke.py').write_text(smoke,encoding='utf-8')
(D/'client/Maps').mkdir(parents=True,exist_ok=True)
shutil.copy2(D/'native-walls/stage/Maps/24_19.unr',D/'stage/Maps/24_19.unr');shutil.copy2(D/'native-walls/client/Maps/24_19.unr',D/'client/Maps/24_19.unr')
print('Prepared rescaled CT/T, matching peace/respawn extent, final client map',ct,t)
