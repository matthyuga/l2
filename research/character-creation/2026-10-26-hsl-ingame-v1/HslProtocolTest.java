import org.l2jmobius.gameserver.custom.HairColorHsl;
public class HslProtocolTest {
 public static void main(String[] args){
  int checks=0;for(int n=0;n<4096;n++){int c=n*0x9e3779&0xffffff;for(int legacy=0;legacy<4;legacy++){Object packet=new Object();int v=HairColorHsl.encode(c,legacy);if(!HairColorHsl.isCustom(v)||HairColorHsl.read(packet,v)!=legacy)throw new AssertionError();HairColorHsl.finish(packet,null);checks++;}}
  for(int n:new int[]{-1,4,128,256,0x44000000,0x7fffffff}){if(HairColorHsl.read(new Object(),n)!=-1)throw new AssertionError("Invalid color accepted");checks++;}
  for(int n=0;n<4;n++){if(HairColorHsl.read(new Object(),n)!=n||HairColorHsl.isCustom(n))throw new AssertionError();checks++;}
  System.out.println("PASS "+checks+" server protocol checks");
 }
}
