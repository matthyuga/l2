from pathlib import Path
import subprocess,sys,copy,struct,json,hashlib,re
root=Path(__file__).resolve().parents[4];s=Path(__file__).resolve().parent;out=s/'npc-hook-v2';out.mkdir(exist_ok=True)
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';client=root.parent/'l2/system-hud'
def run(*args):
 r=subprocess.run([str(codec),*map(str,args)],capture_output=True,timeout=30);assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace')
run('-o',out/'npcgrp.before.raw',client/'npcgrp.dat')
sys.path.insert(0,str(root/'research/amber-l2/scripts'));from contract_dat import Catalog
c=Catalog(out/'npcgrp.before.raw','npcgrp.xml','Interlude');parts=[struct.pack('<I',c.count)]
for r in c.rows:
 if r['npc_id']==59030:
  row=copy.deepcopy(r);row['class_name']='HGLabelNpcV2.Npc';row['deco_effect']=0;row['deco_effect_items']=[];parts.append(c.encode(row))
 else:parts.append(c.data[r['_start']:r['_end']])
parts.append(c.data[c.end:]);(out/'npcgrp.raw').write_bytes(b''.join(parts))
run('-c','encode','-p','413','-o',out/'npcgrp.dat',out/'npcgrp.raw');run('-o',out/'npcgrp.roundtrip.raw',out/'npcgrp.dat')
assert (out/'npcgrp.raw').read_bytes()==(out/'npcgrp.roundtrip.raw').read_bytes()
new=Catalog(out/'npcgrp.raw','npcgrp.xml','Interlude')
for a,b in zip(c.rows,new.rows):
 if a['npc_id']!=59030:assert c.data[a['_start']:a['_end']]==new.data[b['_start']:b['_end']]
run('-o',out/'LineageNpc.raw',client/'LineageNpc.int')
raw=(out/'LineageNpc.raw').read_bytes();match=re.search(rb'(?ms)^\[a_traderB_FHuman\]\s*\r?\n(.*?)(?=^\[[A-Za-z_][^\r\n]*\]|\Z)',raw)
assert match
(out/'HGLabelNpcV2.raw.int').write_bytes(b'[Npc]\r\n'+match[1])
run('-c','encode','-p','111','-o',out/'HGLabelNpcV2.int',out/'HGLabelNpcV2.raw.int')
run('-o',out/'int.roundtrip.raw',out/'HGLabelNpcV2.int');assert (out/'int.roundtrip.raw').read_bytes()==(out/'HGLabelNpcV2.raw.int').read_bytes()
# Encode the helper package to the client's usual script wrapper.
rawpackage=(out/'HGLabelNpcV2.u').read_bytes();(out/'HGLabelNpcV2.raw.u').write_bytes(rawpackage)
run('-c','encode','-p','111','-o',out/'HGLabelNpcV2.u',out/'HGLabelNpcV2.raw.u');run('-o',out/'package.roundtrip.raw',out/'HGLabelNpcV2.u');assert (out/'package.roundtrip.raw').read_bytes()==rawpackage
proof={'installed':False,'display_id':59030,'new_class':'HGLabelNpcV2.Npc','preserved_rows':c.count-1,'all_roundtrips':True,'spawn_hook':'PostSetPawnResource','attachment':'Bip01 Neck1','cleanup':['Detach','ClearL2Game','Destroyed'],'before':{n:hashlib.sha256((client/n).read_bytes()).hexdigest() for n in ['npcgrp.dat','HellgamesLabelsV1.u']},'visual_result':None}
(out/'verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
