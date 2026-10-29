from pathlib import Path
import json,types
D=Path(__file__).resolve().parent;OLD=Path('E:/l2-local/research/character-creation/2026-10-24/orca-hair-v8')
assets=json.loads((D/'assets-manifest.json').read_text());items=assets['items']
source=(OLD/'build_native.py').read_text()
source=source.replace("p.section=bytearray(0x9000)","p.section=bytearray(0xc000)")
source=source.replace("table(0x6a00,", "table(0x9000,T2_MESHES)\n table(0xa000,T2_TEXTURES)\n table(0x6a00,")
source=source.replace('sub esi,edx; cmp esi,2; jae fallback;','sub esi,edx; cmp esi,2; jae second_batch;')
source=source.replace(' result=p.finish();result.update(mesh_hook=', ' count_info=add_count_hook(p)\n result=p.finish();result.update(**count_info);result.update(mesh_hook=')
source=source.replace("  ret=8 if kind=='mesh' else 12", "  body+='jmp named; second_batch: '+t2_dispatch(p,kind)\n  ret=8 if kind=='mesh' else 12")
ns={'__file__':str(D/'build_native.py'),'__name__':'tanda2_native'}
exec(compile(source,str(OLD/'build_native.py'),'exec'),ns)
def t2_dispatch(p,kind):
 out=''
 for i,item in enumerate(items):out+=f'cmp edi,{item["race_index"]}; jne next_{i}; cmp esi,{item["index"]-ns["BASE"][item["race_index"]]}; je t2_{i}; next_{i}: '
 out+='jmp fallback; '
 for i,item in enumerate(items):
  out+=f't2_{i}: cmp eax,4; je empty; '
  if kind=='mesh':out+=f'lea edx,[ebp+{p.rva+0x9000+i*128}]; jmp named; '
  else:
   out+=f'cmp dword ptr [ebx+0x244],4; jae empty; mov eax,dword ptr [esp+28]; cmp eax,{len(item["materials"])}; jae empty; shl eax,7; lea edx,[ebp+eax+{p.rva+0xa000+i*3*128}]; jmp named; '
 return out
def add_count_hook(p):
 start=p.base+p.rva;entry=0x10484240;offset=0x1800;tramp=start+0x1200;asm=ns['asm']
 code=f"""push ebx; push esi; push edi; push ebp; mov ebx,ecx;
 call anchor; anchor: pop ebp; sub ebp,{p.rva+offset+11};
 mov eax,dword ptr [esp+20]; cmp eax,4; je hair_slot; cmp eax,5; jne fallback;
 hair_slot: mov edx,dword ptr [ebx+0x204]; test edx,edx; je fallback; mov ecx,dword ptr [edx+0x718]; test ecx,ecx; je actual_pawn; mov edx,ecx; actual_pawn:
 mov edi,dword ptr [edx+0x698]; mov esi,dword ptr [ebx+0x240];"""
 for i,item in enumerate(items):code+=f'cmp edi,{item["race_index"]}; jne next_{i}; cmp esi,{item["index"]}; je match_{i}; next_{i}: '
 code+='jmp fallback; '
 for i,item in enumerate(items):code+=f'match_{i}: cmp eax,4; je disabled; mov eax,{len(item["materials"])}; jmp done; '
 code+=f"""disabled: xor eax,eax; done: pop ebp; pop edi; pop esi; pop ebx; ret 4;
 fallback: mov ecx,ebx; pop ebp; pop edi; pop esi; pop ebx; jmp {tramp};"""
 code=asm(code,start+offset);assert len(code)<0x800;p.put(offset,code);old=p.hook(entry,start+offset,5);p.put(0x1200,old+asm(f'jmp {entry+5}',tramp+5))
 return dict(count_hook=start+offset,count_trampoline=tramp,count_entry=entry)
ns['add_count_hook']=add_count_hook
ns.update(T2_MESHES=[i['mesh'] for i in items],T2_TEXTURES=[name for i in items for name in i['materials']+['None']*(3-len(i['materials']))],t2_dispatch=t2_dispatch)
def ui():
 p=ns['Patch']('NWindow.dll');start=p.base+p.rva;asm=ns['asm'];tramp=start+0x800;append=0x10198e40
 extra=[2+sum(x['race_index']==r for x in items) for r in range(14)];p.put(0x1800,bytes(extra))
 code=asm(f'''push ebx; push esi; push edi; push ebp; mov ebx,ecx;
 call anchor; anchor: pop ebp; sub ebp,{p.rva+11};
 push dword ptr [esp+20]; call {tramp}; push eax;
 mov ecx,dword ptr [ebx+0x1d8]; cmp dword ptr [ecx+0x2f4],5; je fresh; cmp dword ptr [ecx+0x2f4],7; jne faces;
 fresh: mov eax,dword ptr [ebx+0x1f0]; cmp eax,4; ja faces;
 mov edi,dword ptr [ebx+0x1f8]; cmp edi,1; ja faces;
 test edi,edi; je male_count; cmp dword ptr [ecx+0x2f4],7; jne faces; jmp count_ok;
 male_count: cmp dword ptr [ecx+0x2f4],5; jne faces; count_ok:
 cmp eax,0; je human; cmp eax,1; je elf; cmp eax,2; je dark; cmp eax,3; je orc;
 mov esi,4; jmp model;
 human: mov esi,dword ptr [ebx+0x1f4]; cmp esi,1; ja faces; shl esi,3; jmp model;
 elf: mov esi,6; jmp model; dark: mov esi,2; jmp model;
 orc: mov esi,dword ptr [ebx+0x1f4]; cmp esi,1; ja faces; lea esi,[esi*2+10];
 model: add esi,edi; movzx esi,byte ptr [ebp+esi+{p.rva+0x1800}]; xor edi,edi;
 add_hair: lea eax,[edi+28000]; push eax; mov ecx,dword ptr [ebx+0x1d8]; call {append}; inc edi; cmp edi,esi; jb add_hair;
 faces: mov ecx,dword ptr [ebx+0x1e0]; cmp dword ptr [ecx+0x2f4],3; jne done;
 push 182; call {append}; mov ecx,dword ptr [ebx+0x1e0]; push 186; call {append}; mov ecx,dword ptr [ebx+0x1e0]; push 187; call {append};
 done: pop eax; pop ebp; pop edi; pop esi; pop ebx; ret 4;''',start)
 assert len(code)<0x800;p.put(0,code);old=p.hook(0x10199630,start,6);p.put(0x800,old+asm(f'jmp {0x10199630+6}',tramp+6))
 for i,letter in enumerate('FGHIJK'):p.put(0x1400+i*32,('Type '+letter+'\0').encode('utf-16le'))
 draw=0x10197507;resume=0x1019751c;helper=start+0x1000
 code=asm(f'''call origin; origin: pop ecx; sub ecx,{p.rva+0x1000+5};
 cmp eax,28000; jb native_label; cmp eax,28003; ja native_label;
 mov eax,dword ptr [esi+0x2ec]; sub eax,5; cmp eax,5; ja empty_label; shl eax,5; lea eax,[ecx+eax+{p.rva+0x1400}]; jmp {resume};
 empty_label: lea eax,[ecx+{p.rva+0x1500}]; jmp {resume};
 native_label: push ebp; mov ebp,ecx; lea edx,[eax+eax*2]; mov eax,dword ptr [ebp+0x22c790]; lea ecx,[eax+edx*4+0x6a8dc]; call dword ptr [ebp+0x22c3e4]; pop ebp; jmp {resume};''',helper)
 p.put(0x1000,code);p.patch(draw,asm(f'jmp {helper}',draw)+b'\x90'*16,bytes.fromhex('8d1440a190c722108d8c90dca80600ff15e4c32210'))
 result=p.finish();result.update(selector_hook=start,selector_trampoline=tramp,add_choice_function=append,new_hair_label_ids=list(range(28000,28004)),extra_counts=extra,model_fields=dict(race='0x1f0',archetype='0x1f4',gender='0x1f8'));return result
data=dict(engine=ns['build_engine'](),ui=ui(),race_names=ns['RACES'],original_hair_counts=ns['BASE'],new_hair_counts=[b+2+sum(i['race_index']==r for i in items) for r,b in enumerate(ns['BASE'])],original_face_count=3,new_face_count=6,tanda2=items)
(D/'native-manifest.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print('BUILT engine/UI with model-specific new counts:',data['new_hair_counts'])
