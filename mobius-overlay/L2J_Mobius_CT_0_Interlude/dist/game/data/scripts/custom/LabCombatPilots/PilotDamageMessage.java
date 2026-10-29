package custom.LabCombatPilots;

import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.gameserver.network.GameClient;
import org.l2jmobius.gameserver.network.ServerPackets;
import org.l2jmobius.gameserver.network.serverpackets.ServerPacket;

/** Standard SystemMessage wire format; client records 2204..2207 supplied with this feature. */
final class PilotDamageMessage extends ServerPacket
{
    private final int id,damage;
    private final String attacker;
    PilotDamageMessage(int id,String attacker,int damage) {this.id=id;this.attacker=attacker;this.damage=damage;}
    @Override public void writeImpl(GameClient client,WriteBuffer buffer)
    {
        ServerPackets.SYSTEM_MESSAGE.writeId(this,buffer);
        buffer.writeInt(id);buffer.writeInt(2);
        buffer.writeInt(0);buffer.writeString(attacker);
        buffer.writeInt(1);buffer.writeInt(damage);
    }
}
