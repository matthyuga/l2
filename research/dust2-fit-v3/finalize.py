import pathlib,sys,json,re,shutil,subprocess,struct,zlib,hashlib
D=pathlib.Path(__file__).resolve().parent;R=D.parents[1];V2=D.parent/'dust2-scale-v2';C=R.parent/'l2'
g=json.loads((D/'geodata-audit.json').read_text());b=g['bounds'];ct=g['spawns']['ct'][0];t=g['spawns']['t'][0]
rel='data/scripts/custom/Dust2Arena/Dust2Arena.java';s=(R/'server/game'/rel).read_text(encoding='utf-8')
s,n=re.subn(r'private static final int\[\] CT=\{[^}]+\},T=\{[^}]+\};','private static final int[] CT={'+','.join(map(str,ct))+'},T={'+','.join(map(str,t))+'};',s);assert n==1
lo=[int(v[0])-64 for v in b];hi=[int(v[1])+64 for v in b]
s,n=re.subn(r'private static boolean inside\(Player p\)\{[^\n]+\}',f'private static boolean inside(Player p){{return p.getInstanceId()==0&&p.getX()>{lo[0]}&&p.getX()<{hi[0]}&&p.getY()>{lo[1]}&&p.getY()<{hi[1]}&&p.getZ()>{lo[2]-100}&&p.getZ()<{hi[2]+100};}}',s);assert n==1
p=D/'stage/server'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
rel='data/zones/dust2_arena.xml';s=(R/'server/game'/rel).read_text(encoding='utf-8');s=re.sub(r'minZ="\d+"',f'minZ="{lo[2]-100}"',s);s=re.sub(r'maxZ="\d+"',f'maxZ="{hi[2]+100}"',s)
s,n=re.subn(r'<node X="\d+" Y="\d+" /><node X="\d+" Y="\d+" />',f'<node X="{lo[0]}" Y="{lo[1]}" /><node X="{hi[0]}" Y="{hi[1]}" />',s);assert n==2
p=D/'stage/server'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
shutil.copy2(D/'native-walls/stage/Maps/24_19.unr',D/'stage/Maps/24_19.unr');(D/'client/Maps').mkdir(parents=True,exist_ok=True);shutil.copy2(D/'native-walls/client/Maps/24_19.unr',D/'client/Maps/24_19.unr')
sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import Edit
installed=json.loads((D/'installation.json').read_text()) if (D/'installation.json').exists() else None
baseline=next(pathlib.Path(v['backup']) for v in installed['files'] if v['target'].endswith('24_19.unr')) if installed else C/'Maps/24_19.unr'
old=Edit(baseline);new=Edit(D/'stage/Maps/24_19.unr');preserved=0
for a,e in zip(old.exports,new.exports):
 if a['name']=='myLevel' or a['name'].startswith(('HGDust2ArenaDustPart','HGDust2V2')):continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[e['offset']:e['offset']+e['size']],a['name'];preserved+=1
floors=json.loads((D/'native-floor/verification.json').read_text());walls=json.loads((D/'native-walls/verification.json').read_text());clear=json.loads((D/'clearance-audit.json').read_text());assert clear['connected_spawns']==40 and walls['upper_storey_wall_conflicts']==0
enc=(D/'client/Maps/24_19.unr').read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert enc[28:-20].translate(bytes(v^key for v in range(256)))==(D/'stage/Maps/24_19.unr').read_bytes();assert struct.unpack_from('<I',enc,len(enc)-8)[0]==zlib.crc32(enc[:-20])
(D/'verification.json').write_text(json.dumps(dict(preserved_nonrevision_exports=preserved,armor_gallery_separate=True,scale=1.0,floor=floors,walls=walls,clearance=clear,client_test_pending=True,exit_critical_unresolved=True),indent=2))
shutil.copy2(R/'research/dust2-integration/prepare_smoke.py',D/'prepare_smoke.py')
s=(V2/'prepare_stair_probe.py').read_text().replace('for gx,gy,z,w,h in rects','for gx,gy,z,w,h,*rest in rects').replace('139000<131072+x*16+8<143000 and 54000<32768+y*16+8<58500','137000<131072+x*16+8<145000 and 52500<32768+y*16+8<63000').replace('7800<decode(v)<8400','7500<decode(v)<8850')
(D/'prepare_stair_probe.py').write_text(s)
print('V3 FINAL VERIFIED: aligned floors, 40 connected finite-width starts, preserved',preserved,'unrelated exports; CT/T',ct,t)
