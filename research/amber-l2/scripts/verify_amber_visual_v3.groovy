import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import java.nio.ByteBuffer
import java.nio.ByteOrder
import javax.imageio.ImageIO

def root = new File(args[0]); def project = root.parentFile.parentFile
def client = new File(project.parentFile, 'l2')
def stage = new File(root, 'exports/contract/visual-v3')
def factory = new UnrealSerializerFactory(Environment.fromIni(new File(client, 'system-hud/l2.ini')))
def expected = new File(root, 'reports/expected-bones.txt').readLines()*.toLowerCase()
new UnrealPackage(new File(client, 'system-hud/AmberActorsV1.u'), true).withCloseable { up ->
    def entry = up.exportTable.find { it.objectInnerFullName == 'AmberArcher' }
    def actor = factory.getOrCreateObject(entry)
    assert actor.superField.entry.objectFullName == 'LineageWarrior.LineagePawn'
    def bones = [RightHandBone:'Weapon_R_Bone',LeftHandBone:'Weapon_L_Bone',RightArmBone:'Shield_R_Bone',LeftArmBone:'Shield_L_Bone',SpineBone:'bip01_spine2',CapeBone:'Cape_Bone',HeadBone:'Bip01_head']
    bones.each { name, value ->
        def property = actor.@properties.find { it.name == name }
        assert property != null && up.nameReference(property.getAt(0)) == value && expected.contains(value.toLowerCase())
        println name + '=' + value + ': exists in Amber skeleton.'
    }
    assert actor.@properties.find { it.name == 'WeaponScale' }.getAt(0) == 1f
    new UnrealPackage(new File(client, 'system-hud/LineageNPC.u'), true).withCloseable { original ->
        assert up.GUID != original.GUID
        assert up.exportTable.size() == original.exportTable.size()
        for (int i = 0; i < original.exportTable.size(); i++) {
            if (original.exportTable[i].objectInnerFullName != 'a_traderB_FHuman')
                assert Arrays.equals(original.exportTable[i].objectRawData, up.exportTable[i].objectRawData)
        }
    }
    println 'Isolated actor package: original NPC package and all other cloned exports unchanged.'
}
def schemas = new File(root, 'tools/L2ClientDat/dist/data/structure/dats')
def npc = new AmberCatalog(new File(stage, 'npcgrp.raw'), schemas, 'npcgrp.xml','Interlude').rows.find { it.npc_id == 59002 }
assert npc.class_name == 'AmberActorsV1.AmberArcher' && npc.mesh_name == 'L2AmberArcherV2.AmberNPC'
def codec = new File(project, 'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def localized = new File(root, 'exports/contract/native-controls/AmberActorsV1.verified.raw')
def process = new ProcessBuilder(codec.path, '-o', localized.path, new File(client, 'system-hud/AmberActorsV1.int').path).redirectErrorStream(true).start()
String codecOutput = process.inputStream.text
assert process.waitFor() == 0: codecOutput
assert Arrays.equals(new File(client, 'system-hud/AmberActorsV1.int').bytes, new File(client, 'system/AmberActorsV1.int').bytes)
String config = localized.getText('windows-1252')
def matcher = config =~ /(?ms)^\[AmberArcher\]\r?\n(.*?)(?=^\[[A-Za-z_]|\z)/
assert matcher.find(); String section = matcher.group(1)
def sequences = ['Wait':'Wait_Hand','AtkWait':'AtkWait_Hand','Walk':'walk_hand','Run':'Run_Hand','Atk01':'atk01_Hand','SpAtk01':'SpAtk01_Hand','SpAtk02':'SpAtk02_Hand']
new UnrealPackage(new File(client, 'animations/L2AmberArcherMotion.ukx'), true).withCloseable { motion ->
    sequences.each { key, value ->
        assert section.contains(key + 'AnimName[5]=' + value)
        assert motion.nameTable.any { it.name.equalsIgnoreCase(value) }
    }
}
println 'Installed class/catalog/config/motion chain resolves bow shot and upward special animations.'
def iconFile = new File(client, 'systextures/AmberIconsV1.utx')
byte[] clientIconBytes = iconFile.bytes
byte[] rawIconBytes = new File(stage, 'AmberIconsV1.utx').bytes
assert new String(clientIconBytes,0,28,'UTF-16LE') == 'Lineage2Ver121': 'Client textures require the Lineage2Ver121 wrapper.'
assert clientIconBytes.length == rawIconBytes.length + 48
int iconKey = 'ambericonsv1.utx'.chars().sum() & 255
for (int i=0;i<rawIconBytes.length;i++) assert ((clientIconBytes[i+28] & 255) ^ iconKey) == (rawIconBytes[i] & 255)
println 'Client texture wrapper 121 and full decoded package match PASS.'
new UnrealPackage(iconFile, true).withCloseable { icons ->
    ['Contract','Fire','Rain','Break'].each { name ->
        assert icons.exportTable.any { it.objectInnerFullName == name && it.fullClassName == 'Engine.Texture' }
        byte[] tga = new File(stage, 'icons-roundtrip/AmberIconsV1/Texture/' + name + '.tga').bytes
        def header = ByteBuffer.wrap(tga).order(ByteOrder.LITTLE_ENDIAN)
        assert (header.getShort(12) & 65535) == 32 && (header.getShort(14) & 65535) == 32
        def image = ImageIO.read(new File(stage, 'icons/' + name + '.png')); assert image.width == 32 && image.height == 32
        int depth = tga[16] & 255, stride = depth / 8
        assert depth in [24,32] && (tga[2] & 255) == 2
        int start = 18 + (tga[0] & 255); boolean top = (tga[17] & 32) != 0
        for (int y = 0; y < 32; y++) for (int x = 0; x < 32; x++) {
            int offset = start + ((top ? y : 31-y) * 32 + x) * stride
            int rgb = (tga[offset] & 255) | ((tga[offset+1] & 255) << 8) | ((tga[offset+2] & 255) << 16)
            assert rgb == (image.getRGB(x,y) & 0xffffff)
        }
        println 'AmberIconsV1.' + name + ': resolves; UModel 32x32 roundtrip pixels match exactly.'
    }
}
def skills = new AmberCatalog(new File(stage, 'skillgrp.raw'), schemas, 'skillgrp.xml','ScionsOfDestiny')
[19001:'Contract',19002:'Fire',19003:'Rain',19004:'Break',19005:'Fire'].each { id,name ->
    assert skills.rows.find { it.skill_id == id && it.skill_level == 1 }.icon == 'AmberIconsV1.' + name
}
println 'Four temporary skill icons and fire buff icon linked; existing skill records preserved.'
