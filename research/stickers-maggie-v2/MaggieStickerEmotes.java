package custom.StickerEmotes;

import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.MagicSkillUse;

/** Cosmetic, server validated reactions. No skill execution or combat mutation. */
public final class MaggieStickerEmotes extends Script implements IVoicedCommandHandler {
    static final int FIRST_SKILL = 19720;
    static final long COOLDOWN = TimeUnit.SECONDS.toNanos(5);
    static final String[] NAMES = {"tesoro", "ataco", "duelo", "pergamino", "curame", "escondite", "elfa", "abrazo", "paladin", "gato", "magia", "asesino", "cocina", "orco", "arbol", "unicornio", "amor", "castillo", "furia"};
    private final ConcurrentHashMap<Integer, Long> lastUse = new ConcurrentHashMap<>();

    public MaggieStickerEmotes() {
        VoicedCommandHandler.getInstance().registerHandler(this);
        Logger.getLogger(getClass().getName()).info("STICKER_EMOTES READY: 19 Maggie Fess stickers, 3s visual, 5s server cooldown; .sticker 1..19");
    }
    @Override public String[] getCommandList() { return new String[]{"sticker", "stickers"}; }

    static int selection(String input) {
        String value = input == null ? "" : input.trim().toLowerCase(Locale.ROOT);
        for (int i = 0; i < NAMES.length; i++) if (value.equals(NAMES[i]) || value.equals(Integer.toString(i + 1))) return i;
        return -1;
    }
    static boolean elapsed(Long previous, long now) { return previous == null || now - previous >= COOLDOWN; }

    @Override public boolean onCommand(String command, Player player, String params) {
        if (player == null || !player.isOnline() || !player.isSpawned()) return true;
        int index = selection(params);
        if (index < 0) {
            player.sendMessage("Stickers: boton junto al minimapa. .sticker 1..19: tesoro, ataco, duelo, pergamino, curame, escondite, elfa, abrazo, paladin, gato, magia, asesino, cocina, orco, arbol, unicornio, amor, castillo, furia. Alt+E desactivado temporalmente.");
            return true;
        }
        if (player.isDead() || player.isTeleporting() || player.inObserverMode() || player.isInvisible()) {
            player.sendMessage("No podes enviar un sticker en este estado.");
            return true;
        }
        int id = player.getObjectId();
        long now = System.nanoTime();
        // Atomic reservation prevents simultaneous bypasses from evading the cooldown.
        boolean[] accepted = {false};
        lastUse.compute(id, (key, previous) -> {
            if (elapsed(previous, now)) { accepted[0] = true; return now; }
            return previous;
        });
        if (!accepted[0]) { player.sendMessage("Espera 5 segundos entre stickers."); return true; }
        player.broadcastPacket(new MagicSkillUse(player, player, FIRST_SKILL + index, 1, 0, 0));
        // Bound retained state to active cooldowns, including players who disconnect.
        ThreadPool.schedule(() -> lastUse.remove(id, now), 5100);
        return true;
    }
    public static void main(String[] args) { new MaggieStickerEmotes(); }
}
