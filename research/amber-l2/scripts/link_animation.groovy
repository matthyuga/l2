import acmi.l2.clientmod.io.UnrealPackage

def root = new File(args[0])
def input = new File(root, 'tools/l2editor/L2Editor/L2AmberNPC.u')
def output = new File(root, 'exports/L2AmberNPCv4.ukx')
output.bytes = input.bytes
def compact = { int value ->
    def bytes = []
    boolean negative = value < 0
    value = Math.abs(value)
    int b = value & 0x3f
    value >>>= 6
    bytes << (byte)(b | (negative ? 0x80 : 0) | (value ? 0x40 : 0))
    while (value) {
        b = value & 0x7f
        value >>>= 7
        bytes << (byte)(b | (value ? 0x80 : 0))
    }
    return bytes as byte[]
}
def decode = { byte[] data, int position ->
    int b = data[position++] & 0xff
    boolean negative = (b & 0x80) != 0
    int value = b & 0x3f
    boolean more = (b & 0x40) != 0
    int shift = 6
    while (more) {
        b = data[position++] & 0xff
        value |= (b & 0x7f) << shift
        more = (b & 0x80) != 0
        shift += 7
        if (shift > 34) throw new IllegalArgumentException('Invalid compact int')
    }
    return [negative ? -value : value, position]
}
def expected = new File(root,'reports/expected-bones.txt').readLines()
// Retain the original native animation bytes and dependencies; only add NPC-friendly sequence aliases.
def motion = new File(root,'exports/L2AmberMotionv3.ukx')
motion.bytes = new File('E:/l2/animations/Fighter.ukx').bytes
// Match the sequence names actually exported by a_traderB_FHuman_anim.
def aliases = ['Wait_Hand_FFighter':'Wait_Hand', 'Walk_Hand_FFighter':'walk_hand', 'Run_Hand_FFighter':'Run_Hand',
               'AtkWait_Hand_FFighter':'AtkWait_Hand', 'Atk01_Hand_FFighter':'atk01_Hand',
               'Death_FFighter':'Death_Hand', 'DeathWait_FFighter':'deathwait_Hand',
               'Damage_FFighter':'Damage_Hand', 'Wait_1HS_FFighter':'Wait_1HS',
               'Walk_1HS_FFighter':'Walk_1HS', 'Run_1HS_FFighter':'Run_1HS',
               'Atk01_1HS_FFighter':'Atk01_1HS', 'AtkWait_1HS_FFighter':'AtkWait_1HS']
new UnrealPackage(motion,false).withCloseable { up ->
    up.updateNameTable { names ->
        for(int i=0;i<names.size();i++) {
            def name=names[i]
            if(aliases.containsKey(name.name)) names[i]=new UnrealPackage.NameEntry(up,i,aliases[name.name],name.flags)
        }
    }
}
new UnrealPackage(output, false).withCloseable { up ->
    up.addImportEntries(['L2AmberMotionv3.FFighter_anim':'Engine.MeshAnimation'])
    def animation = up.importTable.find { it.objectFullName == 'L2AmberMotionv3.FFighter_anim' }
    assert animation != null
    def mesh = up.exportTable.find { it.objectInnerFullName == 'AmberNPC' }
    byte[] data = mesh.objectRawData
    byte[] marker = compact(expected.size())
    def matches = []
    for (int offset=0; offset < data.length-marker.length; offset++) {
        if (data[offset] != marker[0] || data[offset+1] != marker[1]) continue
        try {
            def count = decode(data,offset)
            if (count[0] != expected.size()) continue
            int position=count[1]
            boolean valid=true
            for (String name:expected) {
                def item=decode(data,position)
                if (item[0] != up.nameReference(name)) { valid=false; break }
                position=item[1]+56
            }
            if (valid) matches << position
        } catch(Exception ignored) { }
    }
    assert matches.size()==1 : 'Cannot uniquely locate reference skeleton: '+matches
    int position=matches[0]
    def old=decode(data,position)
    assert old[0]==0 : 'Mesh already has an animation'
    byte[] replacement=compact(animation.objectReference)
    def stream=new ByteArrayOutputStream()
    stream.write(data,0,position)
    stream.write(replacement)
    stream.write(data,old[1],data.length-old[1])
    mesh.setObjectRawData(stream.toByteArray())
    up.addNameEntries(['Diffuse','SelfIllumination','Opacity','TwoSided','OutputBlending','ZWrite','AlphaTest','AlphaRef'].collectEntries { [(it):UnrealPackage.DEFAULT_NAME_FLAGS] })
    for (String textureName:['AmberBody','AmberOutfit']) {
        def texture=up.exportTable.find { it.objectInnerFullName==textureName }
        def shader=new ByteArrayOutputStream()
        // Both atlases contain baked toon colors. Keep consistent lighting across skin, hair and clothing.
        def properties=['Diffuse','SelfIllumination','Opacity']
        for (String property:properties) {
            shader.write(compact(up.nameReference(property)))
            shader.write(5) // Object property, one byte value.
            shader.write(compact(texture.objectReference))
        }
        for (String property:['TwoSided','ZWrite','AlphaTest']) {
            shader.write(compact(up.nameReference(property)))
            shader.write(0xD3) // Boolean true; explicit zero data size.
            shader.write(0)
        }
        shader.write(compact(up.nameReference('AlphaRef')))
        shader.write(1)
        shader.write(128)
        shader.write(compact(up.nameReference('OutputBlending')))
        shader.write(1) // Byte property, one byte value.
        shader.write(1) // OB_Masked.
        shader.write(compact(up.nameReference('None')))
        up.addExportEntry(textureName+'Shader','Engine.Shader',null,shader.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
    }
    new File(root,'reports/animation-link.txt').text="Source: ${input.path}\nOutput: ${output.path}\nAnimation: L2AmberMotionv3.FFighter_anim (original Fighter animation bytes, exact trader sequence names)\nReference: ${animation.objectReference}\nSkeleton bones: ${expected.size()}\nNative byte offset: ${position}\nSize before: ${data.length}\nSize after: ${stream.size()}\n"
    println 'Linked original FFighter animations at native mesh offset '+position
}
