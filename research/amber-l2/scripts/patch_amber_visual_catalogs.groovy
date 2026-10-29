import java.nio.charset.StandardCharsets

def root = new File(args[0]); def project = root.parentFile.parentFile
def client = new File(project.parentFile, 'l2/system-hud')
def stage = new File(root, 'exports/contract/visual-v3'); stage.mkdirs()
def schemas = new File(root, 'tools/L2ClientDat/dist/data/structure/dats')
def codec = new File(project, 'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run = { List<String> command ->
    def process = new ProcessBuilder(command).redirectErrorStream(true).start()
    String output = process.inputStream.text
    if (process.waitFor() != 0) throw new IllegalStateException(output)
}
def decode = { File source, File output -> run([codec.path, '-o', output.path, source.path]) }
def encode = { File raw, File encoded, int protocol ->
    run([codec.path, '-c', 'encode', '-p', protocol.toString(), '-o', encoded.path, raw.path])
    def check = new File(stage, encoded.name + '.roundtrip'); decode(encoded, check)
    assert Arrays.equals(raw.bytes, check.bytes)
}
def specs = [
    ['npcgrp','npcgrp.dat','npcgrp.xml','Interlude'],
    ['skillgrp','skillgrp.dat','skillgrp.xml','ScionsOfDestiny']
]
specs.each { spec ->
    def before = new File(stage, spec[0] + '.before.raw'); decode(new File(client, spec[1]), before)
    def cat = new AmberCatalog(before, schemas, spec[2], spec[3])
    assert Arrays.equals(cat.data, cat.patch { null })
    def changes = []
    byte[] data = cat.patch { row ->
        if (spec[0] == 'npcgrp' && row.npc_id == 59002) {
            assert row.mesh_name == 'L2AmberArcherV2.AmberNPC'
            assert row.class_name in ['LineageNPC.a_traderB_FHuman','AmberActorsV1.AmberArcher']
            row.class_name = 'AmberActorsV1.AmberArcher'; changes << 59002; return row
        }
        def icons = [19001:'Contract',19002:'Fire',19003:'Rain',19004:'Break',19005:'Fire',19006:'Rain',19007:'Rain',19008:'Rain',19009:'Fire',19010:'Rain']
        if (spec[0] == 'skillgrp' && icons.containsKey(row.skill_id.intValue())) {
            row.icon = 'AmberIconsV1.' + icons[row.skill_id.intValue()]; changes << row.skill_id
            return row
        }
        null
    }
    assert changes.size() == (spec[0] == 'npcgrp' ? 1 : 10)
    def raw = new File(stage, spec[0] + '.raw'); raw.bytes = data
    def verified = new AmberCatalog(raw, schemas, spec[2], spec[3]); assert verified.count == cat.count
    cat.rows.eachWithIndex { row, i ->
        if (!changes.contains(spec[0] == 'npcgrp' ? row.npc_id.intValue() : row.skill_id))
            assert Arrays.equals(Arrays.copyOfRange(cat.data,row._start,row._end),Arrays.copyOfRange(verified.data,verified.rows[i]._start,verified.rows[i]._end))
    }
    encode(raw, new File(stage, spec[1]), 413)
    println spec[0] + ': changed ' + changes + '; all other records preserved; roundtrip verified.'
}
def configBefore = new File(stage, 'LineageNpc.before.raw'); decode(new File(client, 'LineageNpc.int'), configBefore)
String config = configBefore.getText('windows-1252')
def section = config =~ /(?ms)^\[a_traderB_FHuman\]\r?\n(.*?)(?=^\[[A-Za-z_]|\z)/
assert section.find()
String amber = '[AmberArcher]\r\n' + section.group(1)
if (!config.contains('[AmberArcher]')) config += '\r\n' + amber + '\r\n'
assert config.contains('[AmberArcher]') && amber.contains('Atk01AnimName[5]=atk01_Hand') && amber.contains('SpAtk01AnimName[5]=SpAtk01_Hand')
def configRaw = new File(stage, 'LineageNpc.raw'); configRaw.setText(config, 'windows-1252')
encode(configRaw, new File(stage, 'LineageNpc.int'), 111)
println 'AmberArcher config: dedicated section with native bow shot and upward special mappings.'
