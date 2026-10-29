package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;

/** A shared command catalogue. Destination handlers retain their own permissions and guards. */
public final class RoomCommandHelp implements IVoicedCommandHandler {
 private record Entry(String page,String title,String command,boolean gm){}
 private static final List<Entry> ENTRIES=List.of(
  new Entry("salas","Menu de salas","salas",false),
  new Entry("salas","Libre","salas libre",false),new Entry("salas","Rojos vs Azules","salas equipos",false),
  new Entry("salas","Tres equipos","salas tres",false),new Entry("salas","Arena Top 10","salas arena",false),
  new Entry("salas","Marcador","salas top",false),new Entry("salas","Votacion","salas votar",false),new Entry("salas","Salir (4 segundos)","salas salir",false),
  new Entry("bots","Estado de bots","salas bots estado",true),new Entry("bots","Cerebro tactico","salas bots cerebro tactico",true),new Entry("bots","Cerebro clasico","salas bots cerebro clasico",true),
  new Entry("bots","Iniciar 6: Libre","salas bots iniciar libre 6",true),new Entry("bots","Iniciar 6: Dos equipos","salas bots iniciar equipos 6",true),new Entry("bots","Iniciar 6: Tres equipos","salas bots iniciar tres 6",true),new Entry("bots","Iniciar 6: Arena","salas bots iniciar arena 6",true),
  new Entry("retirar","Retirar bots de Libre","salas bots parar libre",true),new Entry("retirar","Retirar bots de Dos equipos","salas bots parar equipos",true),new Entry("retirar","Retirar bots de Tres equipos","salas bots parar tres",true),new Entry("retirar","Retirar bots de Arena","salas bots parar arena",true),new Entry("retirar","Retirar TODOS los bots","salas bots parar todas",true),
  new Entry("duelos","Lista de rivales NPC","arena lista",true),new Entry("duelos","Iniciar secuencia NPC","arena iniciar",true),new Entry("duelos","Estado secuencia","arena estado",true),new Entry("duelos","Cancelar secuencia","arena cancelar",true),
  new Entry("duelos","Piloto fisico","ia fisico",true),new Entry("duelos","Piloto mago","ia mago",true),new Entry("duelos","Estado piloto","ia estado",true),new Entry("duelos","Cancelar piloto","ia cancelar",true),
  new Entry("grupos","Preparar agite","agite preparar",true),new Entry("grupos","Iniciar agite","agite iniciar",true),new Entry("grupos","Estado agite","agite estado",true),new Entry("grupos","Cancelar agite","agite cancelar",true),
  new Entry("grupos","Cubrir","agite cubrir",true),new Entry("grupos","Asalto","agite asalto",true),new Entry("grupos","Senuelo","agite senuelo",true),new Entry("grupos","Seguir","agite seguir",true),
  new Entry("asedio","Panel asedio Giran","giran",true),new Entry("asedio","Estado roster","roster estado",true),new Entry("asedio","Preparar roster","roster preparar",true),
  new Entry("personaje","Catalogo habilidades","habilidades",true),new Entry("personaje","Encantar habilidades","encantar",true),new Entry("personaje","Personalizacion raza","raza",true),new Entry("personaje","Laboratorio clan","clanlab",true),new Entry("personaje","Contrato Amber","amber",true),new Entry("personaje","Prueba VFX","vfx prueba",true),
  new Entry("viajes","Muelle aereo","muelle",false),new Entry("viajes","Coliseo","muelle coliseo",false),new Entry("viajes","Nave","muelle nave",false),new Entry("viajes","Aurelia","muelle aurelia",false),new Entry("viajes","Vigilia del Dragon","muelle dragon",false),new Entry("viajes","Dust2 exploracion","dust2",false),new Entry("viajes","Salir de Dust2","dust2 salir",false),new Entry("viajes","Veilmar","veilmar",false)
 );
 public static void main(String[] args){register();}
 public static void register(){VoicedCommandHandler.getInstance().registerHandler(new RoomCommandHelp());}
 @Override public String[] getCommandList(){return new String[]{"ayuda","macros"};}
 @Override public boolean onCommand(String command,Player p,String params){
  if(p==null)return false;String page=params==null?"":params.trim();
  if(page.startsWith("usar ")){
   try{int id=Integer.parseInt(page.substring(5));Entry e=ENTRIES.get(id);
    if(e.gm()&&!p.isGM()){p.sendMessage("Acceso reservado a GM.");return true;}
    String[] action=e.command().split(" ",2);IVoicedCommandHandler handler=VoicedCommandHandler.getInstance().getHandler(action[0]);
    if(handler==null)p.sendMessage("Ese comando no esta disponible en esta sesion.");else handler.onCommand(action[0],p,action.length>1?action[1]:"");
   }catch(IndexOutOfBoundsException|NumberFormatException e){p.sendMessage("Acceso invalido. Usa .ayuda.");}return true;
  }
  // Stop the periodic room scoreboard from replacing the catalogue on the next tick.
  if(p.getInstanceId()>0){IVoicedCommandHandler rooms=VoicedCommandHandler.getInstance().getHandler("salas");if(rooms!=null)rooms.onCommand("salas",p,"cerrar");}
  p.sendPacket(new NpcHtmlMessage(render(p.isGM(),page)));return true;
 }
 static String render(boolean gm,String page){
  StringBuilder b=new StringBuilder("<html><body><center><font color=LEVEL>HELLGAMES - Comandos</font><br>");
  if(page.isBlank()){
   for(String category:new String[]{"salas","bots","retirar","duelos","grupos","asedio","personaje","viajes"})
    if(gm||category.equals("salas")||category.equals("viajes"))b.append(button(category.toUpperCase(Locale.ROOT),category));
   b.append("<br>.ayuda / .macros<br>Los botones ejecutan el comando indicado.");
  }else{
   b.append("<font color=LEVEL>").append(escape(page.toUpperCase(Locale.ROOT))).append("</font><br>");
   for(int i=0;i<ENTRIES.size();i++){Entry e=ENTRIES.get(i);if(e.page().equals(page)&&(!e.gm()||gm))b.append(button(e.title(),"usar "+i)).append("<font color=AAAAAA>.").append(e.command()).append("</font><br>");}
   if(page.equals("bots"))b.append("<br>Cantidad manual: 2..12.<br>.salas bots iniciar tres 6 parcial<br>Votos: mayoria, empate, parcial,<br>abstencion, duplicado, tardio.<br>");
   if(page.equals("duelos"))b.append("<br>Individual: .arena probar Noctis<br>.arena es el laboratorio de duelos.<br>.salas arena es el Top 10 PvP.<br>");
   if(page.equals("asedio"))b.append("<br>Las acciones del asedio estan<br>en su propio panel Giran.<br>");
   b.append(button("Volver",""));
  }
  return b.append("</center></body></html>").toString();
 }
 private static String escape(String s){return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;");}
 private static String button(String title,String action){return "<button value=\""+title+"\" action=\"bypass -h voice .ayuda "+action+"\" width=235 height=22 back=\"L2UI_CT1.Button_DF_Down\" fore=\"L2UI_CT1.Button_DF\">";}
}
