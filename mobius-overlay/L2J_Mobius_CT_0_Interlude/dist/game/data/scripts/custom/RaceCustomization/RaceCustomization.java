package custom.RaceCustomization;

import java.security.MessageDigest;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.stats.Stat;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import org.l2jmobius.commons.database.DatabaseFactory;
import custom.LabTelemetry.LabTelemetry;

/** GM prototype; .raza and the future NPC share this service. No fee or public access. */
public class RaceCustomization extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(RaceCustomization.class.getName());
    private static final Map<Integer,Selection> SELECTIONS=new ConcurrentHashMap<>();
    private static final DateTimeFormatter TIME=DateTimeFormatter.ofPattern("HH:mm:ss").withZone(ZoneId.of("America/Buenos_Aires"));
    private static final String[] RACES={"Humano","Elfo","Elfo oscuro","Orco","Enano"};
    private static final Race[] ORIGIN_RACES={Race.HUMAN,Race.HUMAN,Race.ELF,Race.ELF,Race.DARK_ELF,Race.DARK_ELF,Race.ORC,Race.ORC,Race.DWARF};
    private static final String[] ORIGINS={"Humano guerrero","Humano mistico","Elfo guerrero","Elfo mistico","Elfo oscuro guerrero","Elfo oscuro mistico","Orco guerrero","Orco mistico","Enano"};
    private static final String[] LABELS={"STR base","DEX base","CON base","INT base","WIT base","MEN base","STR final","DEX final","CON final","INT final","WIT final","MEN final","HP max","CP max","MP max","P. Atk.","M. Atk.","P. Def.","M. Def.","Atk. Speed","Casting Speed","Precision","Evasion","Critico fisico","Critico magico","Multip. critico","Bonus critico","Correr","Caminar","Alcance"};
    private static final int[][] PAGES={{0,12},{12,21},{21,30}};

    public RaceCustomization()
    {
        VoicedCommandHandler.getInstance().registerHandler(this);
        LOG.info("RaceCustomization v2: .raza GM, selector principal/subclases, Confirmar/Cancelar/Aplicar.");
    }
    @Override public String[] getCommandList(){return new String[]{"raza"};}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        if(!p.isGM()){p.sendMessage("Personalizacion racial: prueba GM solamente.");return true;}
        SELECTIONS.entrySet().removeIf(e->System.currentTimeMillis()-e.getValue().touched>900000);
        Selection s=SELECTIONS.computeIfAbsent(p.getObjectId(),id->new Selection(p));
        synchronized(s)
        {
            if(System.currentTimeMillis()-s.touched<200 && params!=null){return true;}
            s.touched=System.currentTimeMillis();
            try
            {
                String[] parts=params==null?new String[0]:params.trim().split("\\s+");
                String action=parts.length==0?"open":parts[0].toLowerCase(Locale.ROOT);
                if(action.equals("apply")){apply(p,s,parts.length==2?parts[1]:"");return true;}
                s.token=null;
                switch(action)
                {
                    case "open" -> {s=new Selection(p);SELECTIONS.put(p.getObjectId(),s);}
                    case "cancel" -> {s=new Selection(p);SELECTIONS.put(p.getObjectId(),s);p.sendMessage("Seleccion cancelada. No se aplico ningun cambio.");}
                    case "visual" -> s.visual=!s.visual;
                    case "stats" -> s.stats=!s.stats;
                    case "source" -> s.selectClass(p,number(parts,1,3));
                    case "choose-class" -> {chooseClass(p,s);return true;}
                    case "choose-manual" -> {chooseManual(p,s);return true;}
                    case "look" -> {int id=number(parts,1,4);s.visualRace=Race.values()[id];s.fromClass=false;}
                    case "origin" -> {s.origin=number(parts,1,8);s.fromClass=false;}
                    case "page" -> s.page=number(parts,1,2);
                    case "refresh" -> {}
                    case "choose-look" -> {choose(p,s,false);return true;}
                    case "choose-origin" -> {choose(p,s,true);return true;}
                    case "review" -> {review(p,s);return true;}
                    case "unconfirmed" -> p.sendMessage("Primero pulsa Confirmar para revisar el resumen. Luego podras Aplicar.");
                    default -> throw new IllegalArgumentException("Comando desconocido. Usa .raza");
                }
                show(p,s);
            }
            catch(Exception e){p.sendMessage("Personalizacion: "+e.getMessage());LOG.log(Level.WARNING,"RaceCustomization command failed",e);}
        }
        return true;
    }
    private static int number(String[] parts,int at,int max)
    {
        if(parts.length!=at+1)throw new IllegalArgumentException("Seleccion invalida");
        int id=Integer.parseInt(parts[at]);if(id<0||id>max)throw new IllegalArgumentException("Seleccion invalida");return id;
    }
    public static int originIndex(Player p)
    {
        return p.getRacialStatRace()==Race.DWARF?8:p.getRacialStatRace().ordinal()*2+(p.isRacialMage()?1:0);
    }
    /** The selected slot is a source of native racial traits, never a class switch. */
    public static PlayerClass classAtSlot(Player p,int slot)
    {
        if(slot<0||slot>3)throw new IllegalArgumentException("Clase invalida");
        if(slot==0)return PlayerClass.getPlayerClass(p.getBaseClass());
        var sub=p.getSubClasses().get(slot);
        if(sub==null)throw new IllegalArgumentException("No tienes esa subclase");
        return PlayerClass.getPlayerClass(sub.getId());
    }
    public static int originForClass(PlayerClass clazz)
    {
        if(clazz==null||clazz.getRace()==null||clazz.getRace().ordinal()>4)throw new IllegalArgumentException("Clase sin origen racial disponible");
        return clazz.getRace()==Race.DWARF?8:clazz.getRace().ordinal()*2+(clazz.getRootClass().isMage()?1:0);
    }
    private static String className(PlayerClass clazz)
    {
        StringBuilder b=new StringBuilder();
        for(String word:clazz.name().toLowerCase(Locale.ROOT).split("_")){if(b.length()>0)b.append(' ');b.append(Character.toUpperCase(word.charAt(0))).append(word.substring(1));}
        return b.toString();
    }
    static Race destinationRace(Player p,Selection s){return s.visual?s.visualRace:p.getRace();}
    static Race destinationStats(Player p,Selection s){return s.stats?ORIGIN_RACES[s.origin]:p.getRacialStatRace();}
    static boolean destinationMage(Player p,Selection s){return s.stats?s.origin<8 && s.origin%2==1:p.isRacialMage();}
    private static boolean effective(Player p,Selection s)
    {
        return destinationRace(p,s)!=p.getRace()||destinationStats(p,s)!=p.getRacialStatRace()||destinationMage(p,s)!=p.isRacialMage();
    }
    /** Reusable by an NPC entry point later; current authorization remains GM-only. */
    public static String blockedReason(Player p)
    {
        if(!p.isGM())return "Acceso GM requerido";
        if(p.isDead()||p.isInCombat()||p.isAttackingNow()||p.isCastingNow())return "Debes estar vivo y fuera de combate";
        if(p.isInDuel()||p.isInOlympiadMode()||p.getInstanceId()!=0)return "No disponible en duelos, olimpiadas o instancias";
        if(!p.isInsideZone(org.l2jmobius.gameserver.entity.zone.ZoneId.PEACE)||p.isInsideZone(org.l2jmobius.gameserver.entity.zone.ZoneId.PVP))return "Para aplicar, ve a una ciudad en zona de paz";
        if(p.isInStoreMode()||p.isProcessingTransaction()||p.isFishing()||p.isMounted())return "Termina comercio, pesca o montura antes de aplicar";
        return null;
    }
    public static double[] readStats(Player p)
    {
        var t=p.getRacialBaseTemplate();
        return new double[]{org.l2jmobius.gameserver.custom.ModularAppearance.base(p,0),org.l2jmobius.gameserver.custom.ModularAppearance.base(p,1),org.l2jmobius.gameserver.custom.ModularAppearance.base(p,2),org.l2jmobius.gameserver.custom.ModularAppearance.base(p,3),org.l2jmobius.gameserver.custom.ModularAppearance.base(p,4),org.l2jmobius.gameserver.custom.ModularAppearance.base(p,5),p.getSTR(),p.getDEX(),p.getCON(),p.getINT(),p.getWIT(),p.getMEN(),p.getMaxHp(),p.getMaxCp(),p.getMaxMp(),p.getPAtk(null),p.getMAtk(null,null),p.getPDef(null),p.getMDef(null,null),p.getPAtkSpd(),p.getMAtkSpd(),p.getAccuracy(),p.getEvasionRate(null),p.getCriticalHit(null,null),p.getMCriticalHit(null,null),2*p.calcStat(Stat.CRITICAL_DAMAGE,1,null,null)*p.calcStat(Stat.CRITICAL_DAMAGE_POS,1,null,null),p.calcStat(Stat.CRITICAL_DAMAGE_ADD,0,null,null),p.getRunSpeed(),p.getWalkSpeed(),p.getPhysicalAttackRange()};
    }
    public static double[] project(Player p,Race race,boolean mage)
    {
        return p.previewRacialStats(race,mage,()->readStats(p));
    }
    public static String fingerprint(Player p)
    {
        StringBuilder b=new StringBuilder().append(p.getRace()).append('/').append(p.getRacialStatRace()).append('/').append(p.isRacialMage()).append('/').append(p.getLevel()).append('/').append(p.getBaseClass()).append('/').append(p.getPlayerClass().getId()).append('/').append(p.getClassIndex());
        p.getSubClasses().entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e->b.append(";sub:").append(e.getKey()).append(':').append(e.getValue().getId()).append(':').append(e.getValue().getLevel()));
        p.getInventory().getItems().stream().filter(i->i.isEquipped()).sorted(java.util.Comparator.comparingInt(i->i.getObjectId())).forEach(i->b.append(";item:").append(i.getObjectId()).append(':').append(i.getEnchantLevel()));
        p.getAllSkills().stream().sorted(java.util.Comparator.comparingInt(i->i.getId())).forEach(i->b.append(";skill:").append(i.getId()).append(':').append(i.getLevel()));
        p.getEffectList().getEffects().stream().map(i->i.getSkill().getId()+":"+i.getSkill().getLevel()).sorted().forEach(i->b.append(";effect:").append(i));
        b.append(Arrays.toString(readStats(p))); // Includes dyes, temporary effects and calculated values.
        try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8)));}
        catch(Exception e){throw new IllegalStateException(e);}
    }
    private static void capture(Player p,Selection s)
    {
        if(s.fromClass&&classAtSlot(p,s.sourceSlot).getId()!=s.sourceClassId)throw new IllegalStateException("La clase elegida cambio. Vuelve a seleccionarla.");
        String first=fingerprint(p);
        double[] actual=readStats(p), projected=project(p,destinationStats(p,s),destinationMage(p,s));
        if(!first.equals(fingerprint(p)))throw new IllegalStateException("Tu estado cambio durante la lectura. Pulsa Actualizar valores.");
        s.current=actual;s.projected=projected;s.fingerprint=first;s.captured=System.currentTimeMillis();
    }
    private static String header(Player p,Selection s)
    {
        return "<html><body><center><font color=LEVEL>Apariencia y atributos raciales</font><br1>GM gratis | Activa: "+className(p.getPlayerClass())+"<br1>Actual: "+RACES[p.getRace().ordinal()]+" / "+ORIGINS[originIndex(p)]+"<br>";
    }
    private static String button(String label,String action,int width)
    {
        return "<button value=\""+label+"\" action=\"bypass -h voice .raza "+action+"\" width="+width+" height=21 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";
    }
    private static String link(String label,String action)
    {
        return "<a action=\"bypass -h voice .raza "+action+"\">"+label+"</a>";
    }
    private static String controls(Selection s,boolean confirmed)
    {
        return "<table width=280><tr><td>"+button("Confirmar","review",90)+"</td><td>"+button("Cancelar","cancel",90)+"</td><td>"+button("Aplicar",confirmed?"apply "+s.token:"unconfirmed",90)+"</td></tr></table>";
    }
    private static String n(double value){return String.format(Locale.US,"%.2f",value);}
    private static void show(Player p,Selection s)
    {
        send(p,comparisonHtml(p,s));
    }
    static String comparisonHtml(Player p,Selection s)
    {
        capture(p,s);
        StringBuilder h=new StringBuilder(header(p,s));
        h.append(button(s.fromClass?"Clase: "+className(classAtSlot(p,s.sourceSlot)):"Clase de referencia / elegir","choose-class",280));
        h.append(s.fromClass?"Origen nativo: "+ORIGINS[s.origin]:"Seleccion manual").append("<br1>");
        h.append("<table width=280><tr><td>").append(button((s.visual?"[X]":"[ ]")+" Apariencia","visual",135)).append("</td><td>").append(button((s.stats?"[X]":"[ ]")+" Atributos","stats",135)).append("</td></tr></table>");
        h.append("Aspecto: ").append(RACES[destinationRace(p,s).ordinal()]).append(" | Stats: ").append(ORIGINS[s.stats?s.origin:originIndex(p)]).append("<br1>");
        h.append("<button value=\"Cuerpo y sexo modular\" action=\"bypass -h voice .cuerpo\" width=280 height=21 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">");
        h.append(controls(s,false));
        h.append(link("Actualizar valores","refresh")).append(" | ").append(TIME.format(Instant.ofEpochMilli(s.captured))).append("<br1>");
        h.append(link("Atributos","page 0")).append(" | ").append(link("Combate","page 1")).append(" | ").append(link("Otros","page 2")).append("<br>");
        if(!effective(p,s))h.append("Sin cambios efectivos.<br1>");
        h.append("<table width=290 cellspacing=0 cellpadding=0><tr><td fixwidth=82>Stat</td><td fixwidth=64>Actual</td><td fixwidth=64>Nuevo</td><td fixwidth=80>Dif. / %</td></tr>");
        for(int i=PAGES[s.page][0];i<PAGES[s.page][1];i++)
        {
            double diff=s.projected[i]-s.current[i];String color=Math.abs(diff)<0.00001?"AAAAAA":diff>0?"66CCFF":"FF9999";
            String delta=(diff>0?"+":"")+n(diff);String pct=s.current[i]==0?"--":n(diff/s.current[i]*100)+"%";
            h.append("<tr><td>").append(LABELS[i]).append("</td><td>").append(n(s.current[i])).append("</td><td>").append(n(s.projected[i])).append("</td><td><font color=").append(color).append('>').append(delta).append("<br>").append(pct).append("</font></td></tr>");
        }
        h.append("</table><br>").append(link("Elegir razas manualmente","choose-manual"));
        h.append("<br1>Criticos: valores del servidor, no % directos.<br1>Comparacion con tu clase activa; no cambia de subclase.<br>");
        h.append("</center></body></html>");return h.toString();
    }
    private static void chooseClass(Player p,Selection s)
    {
        StringBuilder h=new StringBuilder(header(p,s));
        h.append("Elige de que clase tomar el origen racial.<br1>No cambia tu clase activa ni tus skills.<br>");
        for(int slot=0;slot<=3;slot++)
        {
            if(slot>0&&!p.getSubClasses().containsKey(slot))continue;
            PlayerClass clazz=classAtSlot(p,slot);
            h.append(button((slot==0?"Principal":("Sub "+slot))+": "+className(clazz),"source "+slot,280));
            h.append(ORIGINS[originForClass(clazz)]).append(slot==p.getClassIndex()?" (activa)":"").append("<br1>");
        }
        h.append("<br>").append(button("Volver","refresh",280)).append(button("Cancelar","cancel",280)).append("</center></body></html>");send(p,h.toString());
    }
    private static void choose(Player p,Selection s,boolean stats)
    {
        StringBuilder h=new StringBuilder(header(p,s));
        h.append(stats?"Elegir origen completo de atributos<br>":"Elegir apariencia racial<br>");
        String[] names=stats?ORIGINS:RACES;
        for(int i=0;i<names.length;i++)h.append(button(names[i],(stats?"origin ":"look ")+i,280));
        h.append(button("Volver","refresh",280)).append("<br>Activa la casilla correspondiente para cambiar.<br></center></body></html>");send(p,h.toString());
    }
    private static void chooseManual(Player p,Selection s)
    {
        StringBuilder h=new StringBuilder(header(p,s));
        h.append("Opcional: elegir destinos distintos a tus clases.<br>");
        h.append(button("Aspecto: "+RACES[s.visualRace.ordinal()],"choose-look",280));
        h.append(button("Origen: "+ORIGINS[s.origin],"choose-origin",280));
        h.append(button("Volver a comparar","refresh",280)).append(button("Cancelar","cancel",280)).append("</center></body></html>");send(p,h.toString());
    }
    private static void review(Player p,Selection s)
    {
        if(!effective(p,s)){p.sendMessage("Selecciona apariencia, atributos o ambos y un destino distinto al actual.");show(p,s);return;}
        capture(p,s);s.token=UUID.randomUUID().toString();
        String reason=blockedReason(p);
        StringBuilder h=new StringBuilder(header(p,s));
        h.append("<font color=LEVEL>Seleccion confirmada; falta Aplicar</font><br>");
        if(s.fromClass)h.append("Referencia: ").append(className(classAtSlot(p,s.sourceSlot))).append("<br1>");
        h.append("Aspecto: ").append(RACES[p.getRace().ordinal()]).append(" -&gt; ").append(RACES[destinationRace(p,s).ordinal()]).append("<br1>Origen: ").append(ORIGINS[originIndex(p)]).append(" -&gt; ").append(ORIGINS[s.stats?s.origin:originIndex(p)]).append("<br>");
        h.append(controls(s,true));
        if(reason!=null)h.append("<font color=FF9999>").append(reason).append("</font><br>");
        h.append("Precio: 0 (laboratorio GM)<br1>No cura ni repone HP, CP o MP.<br1>Al cambiar aspecto, rostro y cabello vuelven a 0.<br1>Conserva sexo, clases, equipo y progreso.<br>");
        h.append(button("Volver a comparar","refresh",280)).append("</center></body></html>");send(p,h.toString());
    }
    private static void apply(Player p,Selection s,String token)
    {
        if(s.token==null||!s.token.equals(token))throw new IllegalArgumentException("Confirmacion caducada. Revisa el cambio nuevamente.");
        s.token=null;
        String reason=blockedReason(p);if(reason!=null)throw new IllegalStateException(reason);
        if(System.currentTimeMillis()-s.captured>60000||!s.fingerprint.equals(fingerprint(p)))
        {
            p.sendMessage("Tu estado cambio o la lectura caduco. Revisa la nueva comparacion y confirma otra vez.");show(p,s);return;
        }
        if(!effective(p,s)){show(p,s);return;}
        Race visual=destinationRace(p,s),origin=destinationStats(p,s);boolean mage=destinationMage(p,s);
        double[] expected=s.projected.clone();
        applyConfiguration(p,visual,origin,mage);
        double[] actual=readStats(p);
        if(!close(expected,actual))LOG.warning("RaceCustomization: condiciones variaron durante aplicacion a "+p.getName()+"; revisar telemetria.");
        LOG.info("RaceCustomization APPLIED "+p.getName()+" visual="+visual+" stats="+origin+" mage="+mage);
        LabTelemetry.capturePilotStatsNow(p);
        p.broadcastUserInfo();p.sendMessage("Cambio racial aplicado. Prueba GM gratuita.");
        Selection fresh=new Selection(p);SELECTIONS.put(p.getObjectId(),fresh);show(p,fresh);
    }
    /** Applies only racial choices. Technical integration tests call the same path. */
    public static void applyConfiguration(Player p,Race visual,Race origin,boolean mage)
    {
        if(org.l2jmobius.gameserver.custom.ModularAppearance.current(p).enabled()&&visual!=p.getRace())throw new IllegalArgumentException("Para cambiar el cuerpo usa .cuerpo");
        if(visual.ordinal()>4||origin.ordinal()>4||visual.ordinal()<0||origin.ordinal()<0||origin==Race.DWARF&&mage)throw new IllegalArgumentException("Origen invalido");
        Race oldVisual=p.getRace(),oldOrigin=p.getRacialStatRace();boolean oldMage=p.isRacialMage();
        int face=p.getAppearance().getFace(),hair=p.getAppearance().getHairStyle(),color=p.getAppearance().getHairColor();
        double hp=p.getCurrentHp(),cp=p.getCurrentCp(),mp=p.getCurrentMp();
        try
        {
            p.setAppearanceRace(visual);p.setRacialStatsOrigin(origin,mage);
            if(visual!=oldVisual){p.getAppearance().setFace(0);p.getAppearance().setHairStyle(0);p.getAppearance().setHairColor(0);}
            p.setCurrentHp(Math.min(hp,p.getMaxHp()));p.setCurrentCp(Math.min(cp,p.getMaxCp()));p.setCurrentMp(Math.min(mp,p.getMaxMp()));p.storeMe();
            verifyStored(p,visual,origin,mage);
        }
        catch(RuntimeException e)
        {
            p.setAppearanceRace(oldVisual);p.setRacialStatsOrigin(oldOrigin,oldMage);
            p.getAppearance().setFace(face);p.getAppearance().setHairStyle(hair);p.getAppearance().setHairColor(color);
            p.setCurrentHp(hp);p.setCurrentCp(cp);p.setCurrentMp(mp);p.storeMe();throw e;
        }
    }
    private static void verifyStored(Player p,Race visual,Race origin,boolean mage)
    {
        try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT c.race,(SELECT val FROM character_variables WHERE charId=c.charId AND var='RACIAL_STAT_RACE') stat_race,(SELECT val FROM character_variables WHERE charId=c.charId AND var='RACIAL_PROFILE') profile FROM characters c WHERE c.charId=?"))
        {
            ps.setInt(1,p.getObjectId());
            try(var rs=ps.executeQuery())
            {
                if(!rs.next()||rs.getInt("race")!=visual.ordinal()||!String.valueOf(origin.ordinal()).equals(rs.getString("stat_race"))||!(mage?"MYSTIC":"FIGHTER").equals(rs.getString("profile")))throw new IllegalStateException("No se confirmo el guardado; se restaura la seleccion anterior");
            }
        }
        catch(java.sql.SQLException e){throw new IllegalStateException("No se pudo verificar el guardado",e);}
    }
    public static boolean close(double[] a,double[] b)
    {
        if(a.length!=b.length)return false;
        for(int i=0;i<a.length;i++)if(Math.abs(a[i]-b[i])>0.00001)return false;return true;
    }
    private static void send(Player p,String html)
    {
        if(html.length()>7800)throw new IllegalStateException("Menu demasiado largo");
        NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(html);p.sendPacket(packet);
    }
    static final class Selection
    {
        boolean visual,stats,fromClass;Race visualRace;int origin,page,sourceSlot,sourceClassId;
        long captured,touched;String token,fingerprint;double[] current,projected;
        Selection(Player p){selectClass(p,p.getClassIndex());touched=System.currentTimeMillis();}
        void selectClass(Player p,int slot){PlayerClass clazz=classAtSlot(p,slot);origin=originForClass(clazz);visualRace=clazz.getRace();sourceSlot=slot;sourceClassId=clazz.getId();fromClass=true;}
    }
    public static void main(String[] args){new RaceCustomization();}
}
