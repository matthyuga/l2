"""Fix the live-client GetNpcTexName index<5 limit without changing UV/pixels.
All original8 shader slots have identical render properties; group by4 diffuse textures.
"""
from pathlib import Path
import json,struct,shutil
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'exports/mmd-variants-20261023';OUT=ROOT/'exports/mmd-variants-fix4-20261023';OUT.mkdir(parents=True,exist_ok=True)
groups={'FaceTex':('Face',0),'HairTex':('Hair',1),'OutfitTex':('Outfit',2),'ExpressionTex':('Expression',3)}
for label in ['v10','v14']:
 src=SOURCE/label;dest=OUT/label;dest.mkdir(exist_ok=True);build=json.loads((src/'build.json').read_text());old=build['materials'];mapping={m['slot']:groups[m['texture']][1] for m in old}
 raw=(src/'AmberNPC.psk').read_bytes();pos=0;result=bytearray()
 while pos<len(raw):
  header=raw[pos:pos+32];name,kind,size,count=struct.unpack('<20siii',header);pos+=32;data=bytearray(raw[pos:pos+size*count]);pos+=size*count;tag=name.rstrip(b'\0')
  if tag==b'FACE0000':
   for i in range(count):data[i*size+6]=mapping[data[i*size+6]]
  elif tag==b'VTXW0000':
   for i in range(count):data[i*size+12]=mapping[data[i*size+12]]
  elif tag==b'MATT0000':
   entries=[]
   for texture,(semantic,index) in groups.items():
    source=next(m['slot'] for m in old if m['texture']==texture);entry=bytearray(data[source*size:(source+1)*size]);entry[:64]=semantic.encode().ljust(64,b'\0');struct.pack_into('<i',entry,64,index);entries.append(entry)
   count=4;data=bytearray().join(entries);header=struct.pack('<20siii',name,kind,size,count)
  result.extend(header);result.extend(data)
 (dest/'AmberNPC.psk').write_bytes(result)
 build['original_materials']=old;build['materials']=[dict(slot=index,name=name,texture=texture,triangles=sum(m['triangles'] for m in old if m['texture']==texture)) for texture,(name,index) in groups.items()]
 build['client_texture_limit']=5;build['slot_remap']=mapping;build['fix']='GetNpcTexName index<5:8 shader slots grouped to4 identical render/texture groups'
 (dest/'build.json').write_text(json.dumps(build,indent=2))
 print(label,'original triangles/UV/vertices/weights retained; material mapping',mapping)
# Dedicated compiler/linker use immutable original staging as source.
for source,target in [('compile_amber_mmd_variants.py','compile_amber_mmd_four_slots.py'),('link_amber_mmd_variants.groovy','link_amber_mmd_four_slots.groovy')]:
 text=(ROOT/'scripts'/source).read_text().replace('exports/mmd-variants-20261023','exports/mmd-variants-fix4-20261023').replace('eight original material slots','four client-safe material slots').replace('eight separate masked/self-lit shaders','four client-safe masked/self-lit shaders')
 if source.endswith('.py'):text=text.replace('timeout=180','timeout=600')
 (ROOT/'scripts'/target).write_text(text)
