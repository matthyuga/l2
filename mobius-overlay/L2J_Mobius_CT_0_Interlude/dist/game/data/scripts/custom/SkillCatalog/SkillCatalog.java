package custom.SkillCatalog;

import java.util.List;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView;

/** Read-only class index and filter for the native draggable Alt+K catalog. */
public class SkillCatalog extends Script implements IVoicedCommandHandler
{
    public SkillCatalog(){VoicedCommandHandler.getInstance().registerHandler(this);java.util.logging.Logger.getLogger(getClass().getName()).info("SkillCatalog: .habilidades / .skills; class filters for native Alt+K, no grants.");}
    @Override public String[] getCommandList(){return new String[]{"habilidades","skills"};}
    @Override public boolean onCommand(String command,Player p,String params)
    {
        try{
            String[] args=params==null||params.isBlank()?new String[0]:params.trim().split("\\s+");int page=0;
            if(args.length>0&&args[0].equals("next"))
            {
                int selected=SkillCatalogView.nextClass(p);
                p.getVariables().set(SkillCatalogView.FILTER,selected);p.sendSkillList();
                var slots=new java.util.ArrayList<>(SkillCatalogView.classes(p).keySet());
                p.sendMessage("Habilidades ("+(slots.indexOf(selected)+1)+"/"+slots.size()+"): "+groupName(SkillCatalogView.model(p),selected));return true;
            }
            if(args.length>0&&args[0].equals("quick"))
            {
                int selected=Integer.parseInt(args[1]);
                if(selected<SkillCatalogView.ALL||selected>SkillCatalogView.OTHER||selected>=0&&selected<4&&!SkillCatalogView.classes(p).containsKey(selected))throw new IllegalArgumentException("Clase no disponible.");
                p.getVariables().set(SkillCatalogView.FILTER,selected);p.sendSkillList();
                p.sendMessage("Habilidades: "+groupName(SkillCatalogView.model(p),selected));return true;
            }
            if(args.length>0)switch(args[0]){
                case "filter"->{int selected=Integer.parseInt(args[1]);if(selected<SkillCatalogView.ALL||selected>SkillCatalogView.OTHER||selected>=0&&selected<4&&!SkillCatalogView.classes(p).containsKey(selected))throw new IllegalArgumentException("Clase no disponible.");p.getVariables().set(SkillCatalogView.FILTER,selected);p.sendSkillList();}
                case "order"->{if(!args[1].equals("main")&&!args[1].equals("active"))throw new IllegalArgumentException("Orden invalido.");p.getVariables().set(SkillCatalogView.ORDER,args[1]);p.sendSkillList();}
                case "page"->page=Integer.parseInt(args[1]);
                case "refresh"->p.sendSkillList();
                default->throw new IllegalArgumentException("Usa .habilidades");
            }
            NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(html(p,page));p.sendPacket(packet);
        }catch(RuntimeException e){p.sendMessage("Catalogo: "+e.getMessage());}
        return true;
    }
    public static String html(Player p,int requestedPage)
    {
        var model=SkillCatalogView.model(p);int filter=SkillCatalogView.filter(p);
        List<Skill> all=p.getAllSkills().stream().sorted(model.comparator()).toList();
        List<Skill> visible=all.stream().filter(s->model.visible(s.getId(),filter)).toList();
        int pages=Math.max(1,(visible.size()+5)/6),page=Math.clamp(requestedPage,0,pages-1);
        StringBuilder h=new StringBuilder("<html><body><center><font color=LEVEL>Habilidades por clase</font><br>");
        h.append("El filtro cambia la lista de Alt+K.<br1>Arrastra alli los iconos a la barra.<br1>No cambia clase, skills ni shortcuts.<br>");
        h.append(button("Todas agrupadas ("+all.size()+")","filter -1"));
        h.append(button("Siguiente clase ("+model.classes().size()+" clases)","next"));
        for(var entry:model.classes().entrySet()){
            int slot=entry.getKey();long count=all.stream().filter(s->model.visible(s.getId(),slot)).count();
            h.append(button((slot==0?"Main: ":"Sub "+slot+": ")+SkillCatalogView.className(entry.getValue())+" ("+count+")","filter "+slot));
        }
        for(int group:new int[]{SkillCatalogView.COMMON,SkillCatalogView.AMBER,SkillCatalogView.OTHER}){
            long count=all.stream().filter(s->model.group(s.getId())==group).count();
            if(count>0)h.append(button(groupName(model,group)+" ("+count+")","filter "+group));
        }
        h.append("<br1>Orden: ").append(p.getVariables().getString(SkillCatalogView.ORDER,"main").equals("active")?"clase activa primero":"main, sub1, sub2, sub3").append("<br1>")
            .append("<a action=\"bypass -h voice .habilidades order main\">Principal primero</a> | <a action=\"bypass -h voice .habilidades order active\">Activa primero</a><br>")
            .append("<font color=LEVEL>Filtro: ").append(escape(groupName(model,filter))).append("</font><br1>");
        long passives=visible.stream().filter(Skill::isPassive).count();
        h.append("Activas/activables: ").append(visible.size()-passives).append(" | Pasivas: ").append(passives).append("<br1>")
            .append("Compartidas figuran en cada clase compatible;<br1>en Todas se muestran una sola vez.<br>");
        for(Skill s:visible.subList(page*6,Math.min(visible.size(),page*6+6))){
            h.append("<table width=280><tr><td width=36><img src=\"").append(escape(s.getIcon())).append("\" width=32 height=32></td><td><font color=LEVEL>")
                .append(escape(s.getName())).append("</font><br1>").append(s.isPassive()?"Pasiva":s.isToggle()?"Activable":"Activa").append(" | Nv ").append(s.getLevel()).append("<br1>")
                .append(escape(model.origin(s.getId()))).append("</td></tr></table>");
        }
        h.append("<br1>Pagina ").append(page+1).append('/').append(pages).append("<br1>");
        if(page>0)h.append(button("Anterior","page "+(page-1)));
        if(page+1<pages)h.append(button("Siguiente","page "+(page+1)));
        h.append(button("Actualizar valores y Alt+K","refresh"));
        h.append("<br1>Si falta un icono, pulsa Todas agrupadas.<br1>Amber requiere contrato vigente.<br1>La lista muestra habilidades conocidas ahora;<br1>no concede skills de otras clases.</center></body></html>");
        if(h.length()>8100)throw new IllegalStateException("Pagina demasiado larga.");
        return h.toString();
    }
    private static String groupName(SkillCatalogView.Model model,int group){return switch(group){case -1->"Todas agrupadas";case 4->"Comunes";case 5->"Contrato Amber";case 6->"Especiales";default->SkillCatalogView.className(model.classes().get(group));};}
    private static String button(String title,String action){return "<button value=\""+escape(title)+"\" action=\"bypass -h voice .habilidades "+action+"\" width=280 height=22 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
    private static String escape(String s){return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;");}
    public static void main(String[] args){new SkillCatalog();}
}
