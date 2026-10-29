import org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView;
public final class VerifyColdStickerGate {
 public static void main(String[] args){
  for(int i=1;i<=19;i++)if(!SkillCatalogView.nativeWindowAction("voice .sticker "+i))throw new AssertionError("Startup sticker "+i);
  for(String s:new String[]{"voice .sticker 0","voice .sticker 20","voice .sticker 1 extra","admin_shutdown","voice .raza"})if(SkillCatalogView.nativeWindowAction(s))throw new AssertionError("Unexpected startup action "+s);
  if(!SkillCatalogView.nativeWindowAction("voice .amber toggle"))throw new AssertionError("Previous action");
  System.out.println("PASS: fresh JVM startup agent accepts exact sticker actions 1..19, preserves existing action and rejects unrelated/malformed inputs.");
 }
}
