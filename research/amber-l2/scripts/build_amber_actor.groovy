import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder

def root = new File(args[0])
def client = new File(root.parentFile.parentFile.parentFile, 'l2')
def output = new File(root, 'exports/contract/visual-v3/AmberActorsV1.u')
output.parentFile.mkdirs()
output.bytes = new File(client, 'system-hud/LineageNPC.u').bytes
def compact = { int v ->
    boolean negative = v < 0; v = Math.abs(v)
    def bytes = [(byte)((v & 63) | (negative ? 128 : 0) | (v > 63 ? 64 : 0))]; v >>>= 6
    while (v) { bytes << (byte)((v & 127) | (v > 127 ? 128 : 0)); v >>>= 7 }
    bytes as byte[]
}
new UnrealPackage(output, false).withCloseable { up ->
    // setGUID in this tool version writes its previous UUID; setUUID writes the argument.
    up.setUUID(UUID.randomUUID())
    up.updateNameTable { names ->
        int index = up.nameReference('a_traderB_FHuman')
        names[index] = new UnrealPackage.NameEntry(up, index, 'AmberArcher', names[index].flags)
    }
    def bones = [RightHandBone:'Weapon_R_Bone', LeftHandBone:'Weapon_L_Bone',
        RightArmBone:'Shield_R_Bone', LeftArmBone:'Shield_L_Bone',
        SpineBone:'bip01_spine2', CapeBone:'Cape_Bone', HeadBone:'Bip01_head']
    def expected = new File(root, 'reports/expected-bones.txt').readLines()*.toLowerCase()
    assert bones.values().every { expected.contains(it.toLowerCase()) }
    up.addNameEntries((bones.keySet() + bones.values() + ['WeaponScale']).collectEntries { [(it):UnrealPackage.DEFAULT_NAME_FLAGS] })
    def entry = up.exportTable.find { it.objectInnerFullName == 'AmberArcher' }
    byte[] original = entry.objectRawData
    byte[] none = compact(up.nameReference('None'))
    assert original[-none.length..-1] as byte[] == none
    def data = new ByteArrayOutputStream(); data.write(original, 0, original.length - none.length)
    bones.each { name, bone ->
        byte[] value = compact(up.nameReference(bone))
        data.write(compact(up.nameReference(name))); data.write(0x56); data.write(value.length); data.write(value)
    }
    data.write(compact(up.nameReference('WeaponScale'))); data.write(0x24)
    data.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(1f).array())
    data.write(none)
    entry.setObjectRawData(data.toByteArray())
    println 'AmberActorsV1.AmberArcher: isolated class, seven Fighter skeleton attachments, WeaponScale=1.'
    println 'Original LineageNPC.u remains untouched.'
}
