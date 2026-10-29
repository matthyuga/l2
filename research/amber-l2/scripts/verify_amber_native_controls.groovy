import java.util.zip.ZipFile
import java.security.MessageDigest

def root = new File(args[0]); def project = root.parentFile.parentFile
def client = new File(project.parentFile, 'l2/system-hud')
def stage = new File(root, 'exports/contract/native-controls')
def codec = new File(project, 'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def raw = new File(stage, 'actionname.installed.raw')
def p = new ProcessBuilder(codec.path, '-o', raw.path, new File(client, 'actionname-e.dat').path).redirectErrorStream(true).start()
def out = p.inputStream.text; assert p.waitFor() == 0:out
assert Arrays.equals(raw.bytes, new File(stage, 'actionname.raw').bytes)
def schemas = new File(root, 'tools/L2ClientDat/dist/data/structure/dats')
def before = new AmberCatalog(new File(stage, 'actionname.before.raw'), schemas, 'actionname.xml', 'ScionsOfDestiny')
def after = new AmberCatalog(raw, schemas, 'actionname.xml', 'ScionsOfDestiny')
assert after.rows*.id.unique().size() == after.count && after.count == before.count+2
assert after.rows.find{it.id==22}.category2_items.any{it.'class'==59002}
before.rows.each { old ->
 def fresh = after.rows.find{it.id == old.id}
 if(old.id == 22) assert fresh.category2_items.findAll{it.'class'!=59002} == old.category2_items
 else assert Arrays.equals(Arrays.copyOfRange(before.data, old._start, old._end), Arrays.copyOfRange(after.data, fresh._start, fresh._end))
}
[19021:'Fire',19022:'Rain'].each { id,icon ->
 def row = after.rows.find{it.id==id}
 assert row.category==5 && row.category2_items==[['class':59002]] && row.icon=='AmberIconsV1.'+icon
}
def hash = { byte[] data -> MessageDigest.getInstance('SHA-256').digest(data).encodeHex().toString() }
new ZipFile(new File(project,'backups/amber-native-controls-2026-10-10/GameServer.jar')).withCloseable { original ->
 new ZipFile(new File(project,'server/libs/GameServer.jar')).withCloseable { installed ->
  assert original.size()==installed.size()
  def changed=[]
  original.entries().each { old ->
   def fresh=installed.getEntry(old.name);assert fresh!=null
   if(hash(original.getInputStream(old).bytes)!=hash(installed.getInputStream(fresh).bytes)) changed<<old.name
  }
  assert changed==['org/l2jmobius/gameserver/network/clientpackets/RequestActionUse.class']
 }
}
println "PASS: native controls ${after.count} unique IDs, two Amber-only skill icons, Attack enabled; original action rows and unrelated core classes preserved."
