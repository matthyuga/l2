package custom.CameraObserver;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogin;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import org.l2jmobius.gameserver.network.serverpackets.ObservationEnter;

/** Dedicated local observer; native spectator mode, no GM account or core patch. */
public final class CameraObserver extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG = Logger.getLogger(CameraObserver.class.getName());
    private static final String MARKER = "LAB_CAMERA_OBSERVER_V1";
    private static final Location HOME = new Location(82698, 148638, -3473);
    private static final Map<String, Location> PLACES = Map.of(
        "giran", HOME,
        "coliseo", new Location(147450, 46728, -3410),
        "elven", new Location(46934, 51467, -2977));
    private static CameraObserver instance;
    private final String account;
    private final String name;
    private int characterId;

    public CameraObserver() throws Exception
    {
        Properties cfg = new Properties();
        try (InputStream in = Files.newInputStream(Path.of("config/CameraObserver.properties"))) { cfg.load(in); }
        account = cfg.getProperty("Account", "");
        name = cfg.getProperty("Character", "");
        String hash = cfg.getProperty("PasswordHash", "");
        boolean startFixedObserver = !"flight".equalsIgnoreCase(cfg.getProperty("StartMode", "flight"));
        if (!account.matches("[a-z0-9]{4,20}") || !name.matches("[A-Za-z]{4,16}") || !hash.matches("[A-Za-z0-9+/]{27}="))
            throw new IllegalArgumentException("Invalid local observer configuration");
        provision(hash);
        if (instance != null || VoicedCommandHandler.getInstance().getHandler("camara") != null)
            throw new IllegalStateException("Observer handler already registered");
        instance = this;
        VoicedCommandHandler.getInstance().registerHandler(this);
        Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_PLAYER_LOGIN,
            (OnPlayerLogin event) -> {
                Player p = event.getPlayer();
                if (startFixedObserver && authorized(p)) ThreadPool.schedule(() -> {
                    if (p.isOnline() && p.getClient() != null && World.getPlayer(characterId) == p) {
                        view(p, HOME, 0);
                        p.sendMessage("Camara conectada. Usa .camara para elegir destino. No estas controlando a Hellkevin.");
                    }
                }, 2000);
            }, this));
        LOG.info("CAMERA_OBSERVER READY character=" + name + " id=" + characterId + " account=" + account + " GM=false; .camara");
    }

    private void provision(String hash) throws Exception
    {
        try (Connection con = DatabaseFactory.getConnection()) {
            try (PreparedStatement q = con.prepareStatement("SELECT password,accessLevel FROM accounts WHERE login=?")) {
                q.setString(1, account);
                try (ResultSet rs = q.executeQuery()) {
                    if (rs.next()) {
                        if (!hash.equals(rs.getString(1)) || rs.getInt(2) != 0)
                            throw new IllegalStateException("Reserved observer account already exists with different settings");
                    } else {
                        try (PreparedStatement add = con.prepareStatement("INSERT INTO accounts (login,password,lastactive,accessLevel) VALUES (?,?,?,0)")) {
                            add.setString(1, account); add.setString(2, hash); add.setLong(3, System.currentTimeMillis()); add.executeUpdate();
                        }
                    }
                }
            }
            try (PreparedStatement q = con.prepareStatement("SELECT charId,account_name,online,accesslevel FROM characters WHERE char_name=?")) {
                q.setString(1, name);
                try (ResultSet rs = q.executeQuery()) {
                    if (rs.next()) {
                        if (!account.equals(rs.getString(2)) || rs.getInt(4) != 0)
                            throw new IllegalStateException("Reserved observer character is not owned by local observer account");
                        characterId = rs.getInt(1);
                        LOG.info("CAMERA_OBSERVER existing character retained id=" + characterId);
                        return;
                    }
                }
            }
            try (PreparedStatement q = con.prepareStatement("SELECT COUNT(*) FROM characters WHERE account_name=?")) {
                q.setString(1, account);
                try (ResultSet rs = q.executeQuery()) { rs.next(); if (rs.getInt(1) != 0) throw new IllegalStateException("Reserved account contains other characters"); }
            }
        }
        Player p = Player.create(PlayerTemplateData.getInstance().getTemplate(0), account, name,
            new PlayerAppearance((byte) 0, (byte) 0, (byte) 0, false));
        if (p == null) throw new IllegalStateException("Could not create observer character");
        characterId = p.getObjectId();
        p.setOnlineStatus(true, false);
        try {
            p.setTitle("Camara del mundo");
            p.setXYZ(HOME.getX(), HOME.getY(), HOME.getZ());
            p.getVariables().set(MARKER, true);
            p.setCurrentHpMp(p.getMaxHp(), p.getMaxMp());
            p.setCurrentCp(p.getMaxCp());
            p.storeMe();
        } finally {
            p.deleteMe();
            p.setOnlineStatus(false, true);
        }
        Player reloaded = Player.load(characterId);
        if (reloaded == null) throw new IllegalStateException("Observer persistence verification failed");
        try {
            if (reloaded.isGM() || !account.equals(reloaded.getAccountName()) || !name.equals(reloaded.getName()))
                throw new IllegalStateException("Observer identity/privileges verification failed");
            LOG.info("CAMERA_OBSERVER PROVISION VERIFIED id=" + characterId + " level=" + reloaded.getLevel() + " GM=false; original characters untouched");
        } finally { reloaded.deleteMe(); reloaded.setOnlineStatus(false, true); }
    }

    private boolean authorized(Player p)
    {
        return p != null && p.getObjectId() == characterId && account.equals(p.getAccountName()) && name.equals(p.getName()) && !p.isGM();
    }

    @Override public String[] getCommandList() { return new String[] {"camara"}; }

    @Override public boolean onCommand(String command, Player p, String params)
    {
        if (!authorized(p)) { if (p != null) p.sendMessage("Comando reservado a la cuenta local de camara."); return false; }
        String[] args = params == null || params.isBlank() ? new String[0] : params.trim().split("\\s+");
        try {
            if (args.length == 0 || args[0].equalsIgnoreCase("estado")) { menu(p); return true; }
            String action = args[0].toLowerCase(Locale.ROOT);
            if (PLACES.containsKey(action)) { view(p, PLACES.get(action), 0); menu(p); return true; }
            switch (action) {
                case "on" -> view(p, p.getLocation(), p.getInstanceId());
                case "salir", "off" -> {
                    if (p.inObserverMode()) p.leaveObserverMode();
                    p.sendMessage("Observacion detenida. .camara giran la activa nuevamente.");
                }
                case "ver" -> {
                    if (args.length != 2) throw new IllegalArgumentException("Usa .camara ver Nombre");
                    Player target = World.getPlayer(args[1]);
                    if (target == null || !target.isOnline() || target == p || target.inObserverMode())
                        throw new IllegalArgumentException("Jugador no disponible.");
                    if (target.getInstanceId() != 0) throw new IllegalArgumentException("Esta primera camara observa el mundo principal; salas privadas pendientes.");
                    view(p, new Location(target.getX(), target.getY(), target.getZ()), target.getInstanceId());
                    p.sendMessage("Camara en la posicion actual de " + target.getName() + ". Seguimiento continuo todavia no implementado.");
                }
                case "ir" -> {
                    if (args.length != 4) throw new IllegalArgumentException("Usa .camara ir X Y Z");
                    view(p, checkedLocation(Integer.parseInt(args[1]), Integer.parseInt(args[2]), Integer.parseInt(args[3])), p.getInstanceId());
                }
                default -> throw new IllegalArgumentException("Usa .camara, .camara giran, coliseo, elven, ver Nombre, ir X Y Z, salir.");
            }
        } catch (IllegalArgumentException e) { p.sendMessage(e.getMessage()); }
        catch (Exception e) { LOG.log(Level.WARNING, "Observer action", e); p.sendMessage("No se pudo mover la camara; revisar registro local."); }
        return true;
    }

    static Location checkedLocation(int x, int y, int z)
    {
        if (Math.abs((long) x) > 500000 || Math.abs((long) y) > 500000 || z < -30000 || z > 30000)
            throw new IllegalArgumentException("Coordenadas fuera del rango de laboratorio.");
        return new Location(x, y, z);
    }

    private void view(Player p, Location input, int instanceId)
    {
        Location loc = checkedLocation(input.getX(), input.getY(), input.getZ());
        if (p.hasSummon() || p.isInCombat() || p.isDead()) throw new IllegalArgumentException("La camara debe estar viva, sin summon y fuera de combate.");
        // Keep the first native return anchor while changing the observation point.
        p.setInstanceId(instanceId);
        if (p.inObserverMode()) {
            p.teleToLocation(loc, false);
            p.sendPacket(new ObservationEnter(loc));
        } else p.enterObserverMode(loc);
        if (!p.inObserverMode() || !p.isInvul() || !p.isParalyzed() || !p.isInvisible())
            throw new IllegalStateException("Native observer protections failed");
        LOG.info("CAMERA_OBSERVER VIEW id=" + p.getObjectId() + " instance=" + instanceId + " xyz=" + loc.getX() + "," + loc.getY() + "," + loc.getZ());
    }

    private void menu(Player p)
    {
        StringBuilder h = new StringBuilder("<html><body><center><font color=LEVEL>Camara del mundo</font><br>");
        h.append(p.inObserverMode() ? "Observador activo: invisible e invulnerable.<br>" : "Observador detenido.<br>");
        for (String place : new String[] {"giran", "coliseo", "elven"})
            h.append("<button value=\"").append(place).append("\" action=\"bypass -h voice .camara ").append(place)
                .append("\" width=180 height=22 back=\"L2UI_ch3.bigbutton_down\" fore=\"L2UI_ch3.bigbutton\"><br1>");
        h.append(".camara ver Nombre: ir al jugador<br1>.camara ir X Y Z: cambiar posicion<br1>.camara salir: terminar observacion<br>");
        h.append("Camara local, sin permisos GM.<br>Movimiento y alcance visual pendientes de prueba en vivo.</center></body></html>");
        NpcHtmlMessage msg = new NpcHtmlMessage(); msg.setHtml(h.toString()); p.sendPacket(msg);
    }

    public static void main(String[] args) throws Exception { if (instance == null) new CameraObserver(); }
}
