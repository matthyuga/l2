package custom.GroupAgite;
import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.gameserver.network.GameClient;
import org.l2jmobius.gameserver.network.ServerPackets;
import org.l2jmobius.gameserver.network.serverpackets.ServerPacket;
/** Existing client enemy-damage messages 2204..2207; no new client patch. */
final class AgiteDamageMessage extends ServerPacket
{
    private final int id,damage;private final String attacker;
    AgiteDamageMessage(int id,String attacker,int damage) {this.id=id;this.attacker=attacker;this.damage=damage;}
    @Override public void writeImpl(GameClient client,WriteBuffer buffer)
    {
        ServerPackets.SYSTEM_MESSAGE.writeId(this,buffer);
        buffer.writeInt(id);buffer.writeInt(2);buffer.writeInt(0);buffer.writeString(attacker);buffer.writeInt(1);buffer.writeInt(damage);
    }
}
