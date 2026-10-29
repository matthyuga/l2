RACES=['MFighter','FFighter','MDarkElf','FDarkElf','MDwarf','FDwarf','MElf','FElf','MMagic','FMagic','MOrc','FOrc','MShaman','FShaman']
t1_textures=[f'NexusHairMaterialsV2.{r}_Hair{v+1}_Color{c}' for r in RACES for v in range(2) for c in range(4)]
for c in range(4):t1_textures[20+c]='NexusHairGRepairV12.MDarkElf_G_Color'+str(c)
def repair_source(source):
 old="table(0x3100,[f'NexusHairMaterialsV2.{r}_Hair{v+1}_Color{c}' for r in RACES for v in range(2) for c in range(4)])"
 assert source.count(old)==2;source=source.replace(old,'table(0x3100,REPAIR_T1_TEXTURES)')
 old='''cmp eax,9; jne mesh_hair; cmp edi,2; jne fallback;
   mov esi,dword ptr [ebx+0x248]; sub esi,3; cmp esi,3; jae fallback;
   lea edx,[ebp+{p.rva+0x8100}]; jmp named; mesh_hair:'''
 new='''cmp eax,9; jne mesh_hair;
   mov esi,dword ptr [ebx+0x248]; sub esi,3; cmp esi,3; jae fallback;
   cmp edi,2; je dark_face; cmp edi,10; jne fallback;
   lea edx,[ebp+{p.rva+0x8200}]; jmp named;
   dark_face: lea edx,[ebp+{p.rva+0x8100}]; jmp named; mesh_hair:'''
 assert source.count(old)==1;source=source.replace(old,new)
 old="p.put(0x8100,('NexusDarkFaceV7.MDarkElf_ModernFace'+'\\0').encode('utf-16le'))"
 assert source.count(old)==1;source=source.replace(old,old+"\n p.put(0x8200,('Orc.MOrc_m000_f'+'\\0').encode('utf-16le'))")
 source=source.replace("table(0x6a00,[f'NexusAppearanceV1.{r}_Face{v+3}' for r in RACES for v in range(3)])", "table(0x6a00,[('MOrc.MOrc_m000_t00_f' if r=='MOrc' else f'NexusAppearanceV1.{r}_Face{v+3}') for r in RACES for v in range(3)])")
 return source
