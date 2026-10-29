import java.nio.file.*;
import org.l2jmobius.gameserver.util.DocumentItem;
public class VerifyItems {
 public static void main(String[] args)throws Exception{
  int count=0;var ids=new java.util.HashSet<Integer>();var report=new java.util.ArrayList<String>();
  try(var files=Files.list(Path.of(args[0]))){for(var file:files.filter(p->p.getFileName().toString().startsWith("equipment-")).sorted().toList()){
   var doc=new DocumentItem(file.toFile());doc.parse();if(doc.getItemList().size()!=1)throw new AssertionError("Native parse failed: "+file);
   var item=doc.getItemList().getFirst();if(!ids.add(item.getId()))throw new AssertionError("Duplicate ID");
   if(item.getId()>=32768)throw new AssertionError("Unsafe display ID");
   report.add(item.getId()+"\t"+item.getName()+"\t"+item.getClass().getSimpleName());count++;
  }}
  report.add("SUCCESS: "+count+" item templates accepted by native DocumentItem parser");Files.write(Path.of(args[1]),report);System.out.println(report.getLast());System.exit(0);
 }
}
