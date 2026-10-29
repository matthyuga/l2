import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.nio.file.*;
import org.l2jmobius.gameserver.util.DDSConverter;
public class PrepareNewCrests {
 public static void main(String[] args)throws Exception{
  for(String key:new String[]{"fury","waves"})for(String kind:new String[]{"clan","ally"}){
   int w=kind.equals("clan")?16:8;var src=ImageIO.read(Path.of("crest/prepared/"+key+"-"+kind+".png").toFile());
   if(src.getWidth()!=w||src.getHeight()!=12)throw new IllegalStateException("Source dimensions");
   var padded=new BufferedImage(w,16,BufferedImage.TYPE_INT_RGB);var g=padded.createGraphics();g.drawImage(src,0,0,null);g.dispose();
   byte[] data=DDSConverter.convertToDDS(padded).array();var h=java.nio.ByteBuffer.wrap(data).order(java.nio.ByteOrder.LITTLE_ENDIAN);
   if(data.length!=128+w*8||h.getInt(12)!=16||h.getInt(16)!=w)throw new IllegalStateException("DDS dimensions/length");
   Files.write(Path.of("crest/prepared/"+key+"-"+kind+".dds"),data);System.out.println(key+" "+kind+" "+w+"x16 "+data.length+" bytes");
  }
 }
}
