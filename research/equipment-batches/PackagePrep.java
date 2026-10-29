import org.sedona.l2tool.io.UnrealPackage;
import java.nio.file.*;
import java.util.*;
import java.security.*;
public class PackagePrep {
 static class SafePackage extends UnrealPackage {
  SafePackage(java.io.File f){super(f,false);}
  void rename(Map<String,String> map,int end){
   var ns=new ArrayList<>(getNameTable());
   for(int i=0;i<ns.size();i++){var n=ns.get(i);var replacement=map.get(n.getName().toLowerCase(Locale.ROOT));if(replacement!=null)ns.set(i,new NameEntry(this,i,replacement,n.getFlags()));}
   getFile().setPosition(end);writeNameTable(ns);
   getFile().setPosition(NAME_OFFSET_OFFSET);getFile().writeInt(end);
  }
 }
 public static void main(String[] args) throws Exception {
  var lines=Files.readAllLines(Path.of(args[0]));
  var maps=new HashMap<String,Map<String,String>>();
  for(String line:lines){var f=line.split("\t"); maps.computeIfAbsent(f[0],k->new HashMap<>()).put(f[3].toLowerCase(Locale.ROOT),f[4]);}
  var output=new ArrayList<String>();
  for(String line:lines){var f=line.split("\t");if(f[1].isEmpty())continue;var dest=Path.of(f[2]); try{Files.createDirectories(dest.getParent());var bytes=Files.readAllBytes(Path.of(f[1]));
   if(bytes.length>28 && new String(bytes,0,28,java.nio.charset.StandardCharsets.UTF_16LE).startsWith("Lineage2Ver")){
    var header=new String(bytes,0,28,java.nio.charset.StandardCharsets.UTF_16LE);int v=Integer.parseInt(header.substring(11));int key=172;
    if(v==121){key=0;for(char c:Path.of(f[1]).getFileName().toString().toLowerCase(Locale.ROOT).toCharArray())key+=c;key&=255;}
    else if(v!=111)throw new Exception("Unsupported encryption "+header+" "+f[1]);
    bytes=Arrays.copyOfRange(bytes,28,bytes.length);for(int j=0;j<bytes.length;j++)bytes[j]^=(byte)key;
   }
   Files.write(dest,bytes);
   var before=new ArrayList<byte[]>();
   try(var up=new SafePackage(dest.toFile())){
    for(var e:up.getExportTable())before.add(MessageDigest.getInstance("SHA-256").digest(e.getObjectRawData()));
    up.rename(maps.get(f[0]),bytes.length);
   }
   try(var up=new UnrealPackage(dest.toFile(),true)){
    int i=0;for(var e:up.getExportTable()){
     if(!Arrays.equals(before.get(i++),MessageDigest.getInstance("SHA-256").digest(e.getObjectRawData())))throw new Exception("Object bytes changed: "+dest);
     output.add(f[0]+"\tE\t"+up.getPackageName()+"."+e.getObjectInnerFullName()+"\t"+e.getFullClassName());
    }
    for(var e:up.getImportTable())output.add(f[0]+"\tI\t"+e.getObjectFullName()+"\t"+e.getFullClassName());
   }
   System.out.println("OK "+dest.getFileName());
   }catch(Exception ex){System.out.println("BLOCKED "+f[0]+" "+dest.getFileName()+" "+ex.toString());}
  }
  Files.write(Path.of(args[1]),output);
 }
}
