package custom.RaceCustomization;

import java.util.Arrays;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.custom.ModularAppearance;
import org.l2jmobius.gameserver.custom.ModularAppearance.Profile;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;

/** Same GM laboratory authorization as .raza. Future VIP can call the same core. */
public class ModularBodyMenu extends Script implements IVoicedCommandHandler {
 private static final Logger LOG=Logger.getLogger(ModularBodyMenu.class.getName());
 private static final Map<Integer,Selection> SELECTED=new ConcurrentHashMap<>();
 private static final String[] ATTR={"STR","DEX","CON","INT","WIT","MEN"};
 private static final int[] ROWS={0,1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,19,20,27};
 private static final String[] LABEL={"STR base","DEX base","CON base","INT base","WIT base","MEN base","STR final","DEX final","CON final","INT final","WIT final","MEN final","HP","MP","P. Atk.","M. Atk.","Atk. Speed","Casting Speed","Correr"};
 private static class Selection {
  Profile profile;int origin,page;String token,fingerprint;long captured,touched;boolean restore;
  Selection(Player p){profile=ModularAppearance.current(p);origin=ModularAppearance.origin(p.getRacialStatRace(),p.isRacialMage());touched=System.currentTimeMillis();}
 }
 public ModularBodyMenu(){VoicedCommandHandler.getInstance().registerHandler(this);LOG.info("ModularBodyMenu: .cuerpo GM; race/body/sex preview and personal rollback ready.");}
 @Override public String[] getCommandList(){return new String[]{"cuerpo"};}
 private static String action(String label,String command){return "<button value=\""+label+"\" action=\"bypass -h voice .cuerpo "+command+"\" width=280 height=20 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
 private static String header(){return "<html><body><center><font color=LEVEL>Raza, cuerpo y sexo</font><br1>Laboratorio GM | Precio: 0<br>";}
 private static void send(Player p,String text){if(text.length()>7800)throw new IllegalStateException("Menu demasiado largo");NpcHtmlMessage html=new NpcHtmlMessage();html.setHtml(text);p.sendPacket(html);}
 private static String traits(int[] values){StringBuilder b=new StringBuilder();for(int i=0;i<6;i++)if(values[i]!=0)b.append(ATTR[i]).append(values[i]>0?" +":" ").append(values[i]).append(' ');return b.toString();}
 private static String fingerprint(Player p){return RaceCustomization.fingerprint(p)+"|"+ModularAppearance.state(p)+"|"+p.getVariables().getString(ModularAppearance.SNAPSHOT,"");}
 private static Race race(int origin){return ModularAppearance.bodyRace(origin);}
 private static boolean mage(int origin){return origin<8&&origin%2==1;}
 private static double[] projection(Player p,Selection s){return ModularAppearance.preview(p,race(s.origin),mage(s.origin),s.profile,()->RaceCustomization.readStats(p));}
 private static void show(Player p,Selection s,boolean confirmed){
  double[] before=RaceCustomization.readStats(p),after=projection(p,s);
  s.fingerprint=fingerprint(p);s.captured=System.currentTimeMillis();
  StringBuilder h=new StringBuilder(header());
  h.append("Profesion conservada: ").append(p.getPlayerClass().name()).append("<br1>");
  h.append(action("Origen: "+ModularAppearance.name(s.origin),"origins"));
  h.append(action("Cuerpo: "+ModularAppearance.name(s.profile.body()),"bodies"));
  h.append(action("Sexo: "+(s.profile.female()?"Femenino":"Masculino"),"sex"));
  h.append(action("Sistema modular: "+(s.profile.enabled()?"ACTIVO":"HEREDADO"),"toggle"));
  h.append("<br1>Cuerpo: ").append(traits(ModularAppearance.bodyBonuses(s.profile.body()))).append("<br1>Sexo: ").append(traits(ModularAppearance.sexBonuses(s.profile.female()))).append("<br1>");
  if(!s.profile.enabled())h.append("Modo heredado: no se suman bonos; cuerpo ligado a la principal.<br1>");
  if(s.restore)h.append("<font color=LEVEL>Restaurar seleccion anterior guardada.</font><br1>");
  h.append("<a action=\"bypass -h voice .cuerpo page 0\">Atributos</a> | <a action=\"bypass -h voice .cuerpo page 1\">Combate</a><br1>");
  h.append("<table width=290><tr><td>Stat</td><td>Actual</td><td>Nuevo</td><td>Dif.</td></tr>");
  for(int i=s.page==0?0:12;i<(s.page==0?12:ROWS.length);i++){int row=ROWS[i];double diff=after[row]-before[row];h.append("<tr><td>").append(LABEL[i]).append("</td><td>").append(Math.round(before[row]*100)/100.0).append("</td><td>").append(Math.round(after[row]*100)/100.0).append("</td><td>").append(diff>0?"+":"").append(Math.round(diff*100)/100.0).append("</td></tr>");}
  h.append("</table><br>");
  if(confirmed){s.token=UUID.randomUUID().toString();h.append(action(s.restore?"Aplicar restauracion":"Aplicar seleccion","apply "+s.token));}
  else h.append(action("Confirmar y revisar","review"));
  if(confirmed)h.append(action("Volver a comparar","refresh"));
  h.append(action("Cancelar cambios","cancel"));
  if(ModularAppearance.canRestore(p)&&!s.restore)h.append(action("Restaurar estado anterior","restore"));
  h.append("No cambia profesion, skills, equipo ni progreso.<br1>No repone HP/CP/MP. Al cambiar cuerpo o sexo, cara y pelo vuelven a A.<br1>");
  h.append("<a action=\"bypass -h voice .raza\">Volver a razas</a></center></body></html>");send(p,h.toString());
 }
 private static void choose(Player p,boolean bodies){StringBuilder h=new StringBuilder(header());h.append(bodies?"Cuerpo y su aporte a atributos<br>":"Origen racial de los atributos<br>");for(int i=0;i<9;i++)h.append(action(ModularAppearance.name(i),(bodies?"body ":"origin ")+i));h.append(action("Volver","refresh")).append("</center></body></html>");send(p,h.toString());}
 @Override public boolean onCommand(String command,Player p,String params){
  if(!p.isGM()){p.sendMessage("Personalizacion modular: prueba GM solamente.");return true;}
  SELECTED.entrySet().removeIf(e->System.currentTimeMillis()-e.getValue().touched>900000);
  Selection s=SELECTED.computeIfAbsent(p.getObjectId(),id->new Selection(p));
  synchronized(s){
   try{
    String[] a=params==null||params.isBlank()?new String[]{"open"}:params.trim().split("\\s+");String op=a[0];s.touched=System.currentTimeMillis();
    if(op.equals("apply")){
     if(a.length!=2||s.token==null||!s.token.equals(a[1]))throw new IllegalArgumentException("Confirmacion caducada");s.token=null;
     String blocked=RaceCustomization.blockedReason(p);if(blocked!=null)throw new IllegalStateException(blocked);
     if(System.currentTimeMillis()-s.captured>60000||!s.fingerprint.equals(fingerprint(p)))throw new IllegalStateException("Tu estado cambio; vuelve a confirmar");
     int principal=p.getBaseClass(),active=p.getPlayerClass().getId(),slot=p.getClassIndex();double[] expected=projection(p,s);
     if(s.restore)ModularAppearance.restore(p);else ModularAppearance.apply(p,race(s.origin),mage(s.origin),s.profile);
     if(principal!=p.getBaseClass()||active!=p.getPlayerClass().getId()||slot!=p.getClassIndex())throw new IllegalStateException("Cambio de clase inesperado");
     if(!RaceCustomization.close(expected,RaceCustomization.readStats(p)))LOG.warning("Modular stats changed while applying; inspect buffs/conditions for "+p.getObjectId());
     p.broadcastUserInfo();p.sendMessage("Seleccion modular guardada. Las clases y habilidades se conservaron.");
     s=new Selection(p);SELECTED.put(p.getObjectId(),s);show(p,s,false);return true;
    }
    s.token=null;
    switch(op){
     case "open","cancel" -> {s=new Selection(p);SELECTED.put(p.getObjectId(),s);}
     case "bodies" -> {choose(p,true);return true;}
     case "origins" -> {choose(p,false);return true;}
     case "body","origin" -> {if(a.length!=2)throw new IllegalArgumentException("Seleccion invalida");int n=Integer.parseInt(a[1]);if(n<0||n>8)throw new IllegalArgumentException("Seleccion invalida");if(op.equals("body"))s.profile=new Profile(true,n,s.profile.female());else s.origin=n;s.restore=false;}
     case "sex" -> {s.profile=new Profile(s.profile.enabled(),s.profile.body(),!s.profile.female());s.restore=false;}
     case "toggle" -> {s.profile=new Profile(!s.profile.enabled(),s.profile.body(),s.profile.female());s.restore=false;}
     case "page" -> {if(a.length!=2)throw new IllegalArgumentException("Pagina invalida");s.page=Integer.parseInt(a[1]);if(s.page<0||s.page>1)throw new IllegalArgumentException("Pagina invalida");}
     case "restore" -> {
      String saved=p.getVariables().getString(ModularAppearance.SNAPSHOT,null);if(saved==null)throw new IllegalStateException("No hay estado anterior");String[] v=saved.split(",");
      s.profile=new Profile(Boolean.parseBoolean(v[7]),Integer.parseInt(v[8]),Boolean.parseBoolean(v[3]));s.origin=ModularAppearance.origin(Race.values()[Integer.parseInt(v[1])],Boolean.parseBoolean(v[2]));s.restore=true;show(p,s,true);return true;
     }
     case "review" -> {show(p,s,true);return true;}
     case "refresh" -> {}
     default -> throw new IllegalArgumentException("Usa .cuerpo");
    }
    show(p,s,false);
   }catch(Exception e){p.sendMessage("Personalizacion: "+e.getMessage());LOG.log(Level.WARNING,"Modular body command failed",e);}
  }
  return true;
 }
 public static void main(String[] args){new ModularBodyMenu();}
}
