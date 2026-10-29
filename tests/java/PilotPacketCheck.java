package custom.LabCombatPilots;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.commons.network.pool.ResourcePool;
public class PilotPacketCheck
{
    public static void main(String[] args)
    {
        for(int id=2204;id<=2207;id++)
        {
            WriteBuffer buffer=new WriteBuffer(new ResourcePool(),PilotDamageMessage.class);
            new PilotDamageMessage(id,"Noctis",1234).writeImpl(null,buffer);
            buffer.limit(buffer.position());
            ByteBuffer bytes=ByteBuffer.wrap(buffer.toByteArray()).order(ByteOrder.LITTLE_ENDIAN);
            if((bytes.get()&255)!=0x64 || bytes.getInt()!=id || bytes.getInt()!=2 || bytes.getInt()!=0) throw new AssertionError("Header");
            StringBuilder name=new StringBuilder();char c;while((c=bytes.getChar())!=0) name.append(c);
            if(!name.toString().equals("Noctis") || bytes.getInt()!=1 || bytes.getInt()!=1234 || bytes.hasRemaining()) throw new AssertionError("Parameters");
            buffer.releaseResources();
        }
        System.out.println("PASS4 incoming damage packet variants: IDs, string/int parameters and complete wire length.");
    }
}
