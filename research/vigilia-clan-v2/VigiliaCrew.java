package custom.GludioSky;

import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import java.util.logging.Logger;

/** Stationary crew lift between physical supported decks; local NPC interaction only. */
public final class VigiliaCrew extends Script
{
 public static final int NPC=902710;
 public static VigiliaCrew instance;
 public final java.util.List<Npc> crew=new java.util.ArrayList<>();
 public VigiliaCrew()
 {
  instance=this;addStartNpc(NPC);addTalkId(NPC);addFirstTalkId(NPC);
  for(int[] p:new int[][]{{146650,52200,12056},{146650,52200,12760},{145450,52100,12384}})
  {
   int floor=GeoEngine.getInstance().getHeight(p[0],p[1],p[2]);
   if(Math.abs(floor-p[2])>40)throw new IllegalStateException("Vigilia crew floor missing");
   Npc n=addSpawn(NPC,p[0],p[1],floor,32768,false,0,false,0);n.setInvul(true);crew.add(n);
  }
  Logger.getLogger(getClass().getName()).info("VigiliaCrew V2: three local deck stewards, gallery/captain/cabin/cubierta.");
 }
 private String menu()
 {
  StringBuilder b=new StringBuilder("<html><body><center><font color=LEVEL>Vigilia del Dragon</font><br>Contramaestre del clan<br><br>Elige una cubierta:<br>");
  String[] ids={"cubierta","galeria","capitan","habitacion"},names={"Cubierta principal","Galeria de observacion","Puesto del capitan","Aposento del clan"};
  for(int i=0;i<ids.length;i++)b.append("<button value=\"").append(names[i]).append("\" action=\"bypass -h Quest VigiliaCrew ").append(ids[i]).append("\" width=230 height=24 back=\"L2UI_CT1.Button_DF_Down\" fore=\"L2UI_CT1.Button_DF\"><br>");
  return b.append("Nave estacionada. Traslado gratuito.<br>Habla con otro contramaestre para volver.</center></body></html>").toString();
 }
 @Override public String onFirstTalk(Npc n,Player p){return menu();}
 @Override public String onTalk(Npc n,Player p){return menu();}
 @Override public String onEvent(String event,Npc n,Player p)
 {
  if(n==null||p==null||n.getId()!=NPC||n.getInstanceId()!=0||p.getInstanceId()!=0||!p.isInsideRadius2D(n,250)||Math.abs(p.getZ()-n.getZ())>140)return null;
  if(p.isDead()||p.isInCombat()||p.isTeleporting()||p.isFlying()||p.isInOlympiadMode()||p.getPvpFlag()>0||p.getKarma()>0){p.sendMessage("Debes estar vivo y fuera de combate, PvP, vuelo e instancias.");return null;}
  int x=146500,y=52000,z=12056;
  switch(event)
  {
   case "cubierta":break;
   case "galeria":x=146700;z=12760;break;
   case "capitan":x=145500;z=12384;break;
   case "habitacion":x=145650;break;
   default:return menu();
  }
  int floor=GeoEngine.getInstance().getHeight(x,y,z);
  if(Math.abs(floor-z)>40){p.sendMessage("La cubierta no esta disponible. Avisa al administrador.");return null;}
  p.teleToLocation(x,y,floor+24,0,0,false);return null;
 }
 public static void main(String[] args){new VigiliaCrew();}
}
