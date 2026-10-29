import java.nio.file.*;
import javax.xml.XMLConstants;
import javax.xml.validation.SchemaFactory;
import javax.xml.transform.stream.StreamSource;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.config.custom.FakePlayersConfig;
import org.l2jmobius.gameserver.config.ServerConfig;
import org.l2jmobius.gameserver.util.DocumentItem;
import org.l2jmobius.gameserver.entity.actor.instance.Folk;
import org.l2jmobius.gameserver.entity.item.ItemTemplate;
import java.util.*;
public class VerifyShowcase {
 static class DetachedNpcs extends NpcData { @Override public synchronized void load(){} }
 public static void main(String[] args)throws Exception {
  Path project=Path.of(args[0]),root=project.resolve("research/equipment-batches/showcase");
  ServerConfig.DATAPACK_ROOT=project.resolve("server/game").toFile();FakePlayersConfig.FAKE_PLAYERS_ENABLED=true;
  var sf=SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
  sf.newSchema(project.resolve("server/game/data/xsd/npcs.xsd").toFile()).newValidator().validate(new StreamSource(root.resolve("data/stats/npcs/custom/equipment_showcase.xml").toFile()));
  sf.newSchema(project.resolve("server/game/data/xsd/spawns.xsd").toFile()).newValidator().validate(new StreamSource(root.resolve("data/lab/world-spawns/EquipmentShowcase.xml").toFile()));
  var slots=new HashSet<Integer>();var report=new ArrayList<String>();
  var document=javax.xml.parsers.DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(root.resolve("data/stats/npcs/custom/equipment_showcase.xml").toFile());
  var nodes=document.getElementsByTagName("npc");if(nodes.getLength()!=157)throw new AssertionError("Expected 157 mannequins");
  for(int i=0;i<nodes.getLength();i++){
   var n=(org.w3c.dom.Element)nodes.item(i);if(!n.getAttribute("type").equals("Folk"))throw new AssertionError("Combat type");
   var status=(org.w3c.dom.Element)n.getElementsByTagName("status").item(0);
   if(!status.getAttribute("canMove").equals("false")||!status.getAttribute("undying").equals("true"))throw new AssertionError("Invalid status");
   var fp=(org.w3c.dom.Element)n.getElementsByTagName("fakePlayer").item(0);
   for(var key:new String[]{"equipHead","equipRHand","equipLHand","equipChest","equipLegs","equipGloves","equipFeet","equipHair","equipHair2"}){
    var val=fp.getAttribute(key);if(!val.isEmpty()&&Integer.parseInt(val)>0)slots.add(Integer.parseInt(val));
   }
  }
  var actual=new HashMap<Integer,ItemTemplate>();
  try(var files=Files.list(project.resolve("server/game/data/stats/items"))){for(var p:files.filter(p->p.toString().endsWith(".xml")).toList()){
   var doc=new DocumentItem(p.toFile());doc.parse();for(var item:doc.getItemList())if(slots.contains(item.getId()))actual.put(item.getId(),item);
  }}
  if(!actual.keySet().containsAll(slots))throw new AssertionError("Unknown display equipment IDs");
  report.add("SUCCESS: NPC/spawn XSD schemas valid; 157 display definitions static and undying; "+slots.size()+" equipment IDs resolve to native installed item templates. Live native NPC/packet verification is recorded separately in runtime-verification.txt.");
  Files.write(root.resolve("native-verification.txt"),report);System.out.println(report.getFirst());System.exit(0);
 }
}
