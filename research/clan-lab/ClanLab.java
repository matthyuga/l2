package custom.ClanLab;

import java.sql.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.SocialClass;
import org.l2jmobius.gameserver.entity.clan.*;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.skill.holders.SkillLearn;
import org.l2jmobius.gameserver.network.serverpackets.*;

/** Personal GM laboratory. Uses native clan APIs and the installed pledge tree. */
public class ClanLab extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(ClanLab.class.getName());
    private static final int MAX_LEVEL=8, PAGE_SIZE=4;
    private final Map<Integer,Pending> pending=new ConcurrentHashMap<>();
    record Pending(String token,long expires,int clanId,int oldClanLevel,int id,int oldSkill,int newValue,int filter,int page){}
    public ClanLab(){VoicedCommandHandler.getInstance().registerHandler(this);LOG.info("ClanLab: .clanlab / .clannivel / .clanskills; Hellkevin GM, own clan leader, free laboratory, native level/skill rules.");}
    public String[] getCommandList(){return new String[]{"clanlab","clannivel","clanskills"};}
    static boolean authorized(Player p){return p!=null&&p.isGM()&&p.getName().equals("Hellkevin")&&p.getClan()!=null&&p.isClanLeader();}
    public boolean onCommand(String command,Player p,String params)
    {
        if(!authorized(p)){p.sendMessage("Panel de prueba reservado a Hellkevin GM y lider de su propio clan.");return true;}
        pending.entrySet().removeIf(e->e.getValue().expires()<System.currentTimeMillis());
        Clan clan=p.getClan();
        synchronized(clan){try{
            String[] a=params==null||params.isBlank()?new String[0]:params.trim().split("\\s+");
            String action=a.length==0?(command.equals("clannivel")?"levels":command.equals("clanskills")?"skills":"home"):a[0];
            if(action.equals("apply")){
                if(a.length!=2)throw new IllegalArgumentException("Confirmacion invalida.");
                Pending q=pending.remove(p.getObjectId());
                if(q==null||!q.token().equals(a[1])||q.expires()<System.currentTimeMillis())throw new IllegalArgumentException("Confirmacion vencida. Abre el panel de nuevo.");
                if(q.clanId()!=clan.getId()||q.oldClanLevel()!=clan.getLevel())throw new IllegalArgumentException("Cambio el clan o su nivel; revisa de nuevo.");
                if(q.id()==0){upgrade(p,clan,q.clanId(),q.oldClanLevel(),q.newValue());p.sendMessage("Clan nivel "+clan.getLevel()+": guardado.");send(p,levels(p));}
                else{learn(p,clan,q.clanId(),q.id(),q.oldSkill(),q.newValue());p.sendMessage("Skill de clan aprendida y guardada.");send(p,skills(p,q.filter(),q.page()));}
                return true;
            }
            pending.remove(p.getObjectId());
            switch(action){
                case "home","cancel" -> send(p,home(p));
                case "levels" -> send(p,levels(p));
                case "skills" -> send(p,skills(p,a.length>1?Integer.parseInt(a[1]):0,a.length>2?Integer.parseInt(a[2]):0));
                case "level" -> {
                    if(a.length!=2)throw new IllegalArgumentException("Nivel invalido.");int n=Integer.parseInt(a[1]);validateUpgrade(clan,n);
                    confirm(p,new Pending(UUID.randomUUID().toString(),System.currentTimeMillis()+120000,clan.getId(),clan.getLevel(),0,0,n,0,0),"Subir "+escape(clan.getName())+" del nivel "+clan.getLevel()+" al "+n+".<br>No aprende habilidades automaticamente.");
                }
                case "skill" -> {if(a.length!=4)throw new IllegalArgumentException("Skill invalida.");detail(p,Integer.parseInt(a[1]),Integer.parseInt(a[2]),Integer.parseInt(a[3]));}
                case "learn" -> {
                    if(a.length!=5)throw new IllegalArgumentException("Skill invalida.");int id=Integer.parseInt(a[1]),lv=Integer.parseInt(a[2]),f=Integer.parseInt(a[3]),page=Integer.parseInt(a[4]);
                    SkillLearn row=available(clan,id,lv);int old=known(clan,id);
                    confirm(p,new Pending(UUID.randomUUID().toString(),System.currentTimeMillis()+120000,clan.getId(),clan.getLevel(),id,old,lv,f,page),escape(row.getName())+": nivel "+old+" &gt; "+lv+".<br>Requiere clan "+row.getGetLevel()+".<br>Efectos solo para miembros con rango "+rank(row)+" o superior.");
                }
                default -> throw new IllegalArgumentException("Usa .clanlab");
            }
        }catch(IllegalArgumentException|IllegalStateException e){p.sendMessage(e.getMessage());}
        catch(Exception e){p.sendMessage("No se pudo completar el cambio; revisa el registro del laboratorio.");LOG.log(Level.SEVERE,"ClanLab action",e);}}
        return true;
    }
    static int known(Clan c,int id){Skill s=c.getSkills().get(id);return s==null?0:s.getLevel();}
    static List<SkillLearn> catalog(int filter){
        if(filter<0||filter>8)throw new IllegalArgumentException("Filtro de nivel invalido.");
        Map<Integer,SkillLearn> rows=new HashMap<>();
        for(SkillLearn s:SkillTreeData.getInstance().getPledgeSkillTree().values())if(!s.isResidencialSkill()&&(filter==0||s.getGetLevel()==filter))
            rows.merge(s.getSkillId(),s,(x,y)->x.getSkillLevel()>y.getSkillLevel()?x:y);
        return rows.values().stream().sorted(Comparator.comparingInt(SkillLearn::getGetLevel).thenComparing(SkillLearn::getName)).toList();
    }
    static SkillLearn available(Clan c,int id,int level){return SkillTreeData.getInstance().getAvailablePledgeSkills(c).stream().filter(s->s.getSkillId()==id&&s.getSkillLevel()==level).findFirst().orElseThrow(()->new IllegalArgumentException("Skill bloqueada, ya aprendida o nivel fuera de secuencia."));}
    static void validateUpgrade(Clan c,int n){if(n<=c.getLevel()||n>MAX_LEVEL)throw new IllegalArgumentException("Elige un nivel superior al actual, hasta 8.");}
    static void checkContext(Player p,Clan c,int clanId){
        if(p.getClan()!=c||c.getId()!=clanId||!p.isClanLeader())throw new IllegalArgumentException("El clan o el lider cambiaron.");
        if(p.isDead()||p.isInCombat()||p.isCastingNow()||p.isAttackingNow()||p.getInstanceId()!=0||p.isInOlympiadMode())throw new IllegalArgumentException("Sal del combate, casteo y evento primero.");
        if(c.getDissolvingExpiryTime()!=0)throw new IllegalArgumentException("El clan esta en proceso de disolucion.");
    }
    static void upgrade(Player p,Clan c,int clanId,int old,int n)throws Exception{
        checkContext(p,c,clanId);if(c.getLevel()!=old)throw new IllegalArgumentException("Cambio el nivel del clan.");validateUpgrade(c,n);
        c.changeLevel(n);
        try(Connection db=DatabaseFactory.getConnection();PreparedStatement q=db.prepareStatement("SELECT clan_level FROM clan_data WHERE clan_id=?")){q.setInt(1,c.getId());try(var rs=q.executeQuery()){if(!rs.next()||rs.getInt(1)!=n){c.changeLevel(old);throw new IllegalStateException("No se guardo el nivel; se restauro el anterior.");}}}
        refresh(c,p);LOG.info("CLAN_LAB LEVEL char="+p.getObjectId()+" clan="+c.getId()+" old="+old+" new="+n);
    }
    static void learn(Player p,Clan c,int clanId,int id,int old,int n)throws Exception{
        checkContext(p,c,clanId);if(known(c,id)!=old)throw new IllegalArgumentException("Cambio el nivel de la skill; revisa de nuevo.");available(c,id,n);
        // Native upgrades update by clan+skill; avoid touching a separate subunit copy.
        try(Connection db=DatabaseFactory.getConnection();PreparedStatement q=db.prepareStatement("SELECT sub_pledge_id FROM clan_skills WHERE clan_id=? AND skill_id=?")){q.setInt(1,c.getId());q.setInt(2,id);try(var rs=q.executeQuery()){while(rs.next())if(rs.getInt(1)!=-2)throw new IllegalArgumentException("Esta skill tiene una copia de subunidad; usa el maestro de clan.");}}
        Skill previous=c.getSkills().get(id),next=SkillData.getInstance().getSkill(id,n);if(next==null)throw new IllegalArgumentException("Skill inexistente.");
        c.addNewSkill(next);
        try(Connection db=DatabaseFactory.getConnection();PreparedStatement q=db.prepareStatement("SELECT skill_level FROM clan_skills WHERE clan_id=? AND skill_id=? AND sub_pledge_id=-2")){
            q.setInt(1,c.getId());q.setInt(2,id);try(var rs=q.executeQuery()){if(!rs.next()||rs.getInt(1)!=n){
                if(previous==null)c.getSkills().remove(id);else c.addSkill(previous);
                for(Player member:c.getOnlineMembers(0))member.removeSkill(id,false);
                p.removeSkill(id,false);refresh(c,p);throw new IllegalStateException("No se guardo la skill; se restauro el estado anterior.");
            }}
        }
        refresh(c,p);LOG.info("CLAN_LAB SKILL char="+p.getObjectId()+" clan="+c.getId()+" skill="+id+" old="+old+" new="+n);
    }
    static void refresh(Clan c,Player actor){
        Set<Player> online=new HashSet<>(c.getOnlineMembers(0));online.add(actor);
        for(Player member:online){member.setPledgeClass(ClanMember.calculatePledgeClass(member));c.removeSkillEffects(member);c.addSkillEffects(member);member.sendPacket(new PledgeSkillList(c));member.sendSkillList();member.broadcastUserInfo();}
    }
    private void confirm(Player p,Pending q,String summary){pending.put(p.getObjectId(),q);send(p,end(header(p,"Confirmar cambio de clan").append(summary).append("<br><br>Prueba GM gratuita. Cambio permanente.<br>").append(button("Aplicar","apply "+q.token())).append(button("Cancelar","cancel"))));}
    static String home(Player p){return end(header(p,"Laboratorio de clan").append("Prueba GM gratuita, solo tu clan.<br>Sin adena, objetos ni reputacion.<br><br>").append(button("Niveles del clan","levels")).append("<br>").append(button("Skills por nivel","skills 0 0")));}
    static String levels(Player p){
        Clan c=p.getClan();StringBuilder h=header(p,"Niveles del clan").append("Maximo Interlude: 8.<br>Subir no aprende skills automaticamente.<br><br>");
        for(int n=1;n<=8;n++){h.append("Nivel ").append(n).append(": ").append(catalog(n).size()).append(" habilidades desbloqueadas<br>");if(n>c.getLevel())h.append(button("Subir a nivel "+n,"level "+n));}
        if(c.getLevel()==8)h.append("<font color=LEVEL>Clan al nivel maximo.</font><br>");
        return end(h.append(button("Skills por nivel","skills 0 0")).append(button("Volver","home")));
    }
    static String skills(Player p,int filter,int requested){
        List<SkillLearn> list=catalog(filter);int pages=Math.max(1,(list.size()+PAGE_SIZE-1)/PAGE_SIZE),page=Math.clamp(requested,0,pages-1);
        Clan c=p.getClan();StringBuilder h=header(p,"Skills del clan").append("Ver desbloqueos por nivel:<br><table><tr>");
        for(int n=5;n<=8;n++)h.append("<td>").append(button("Nivel "+n,"skills "+n+" 0",62)).append("</td>");
        h.append("</tr></table>").append(button("Todos los niveles","skills 0 0")).append("<br>Pagina ").append(page+1).append('/').append(pages).append("<br>");
        for(SkillLearn row:list.subList(page*PAGE_SIZE,Math.min(list.size(),(page+1)*PAGE_SIZE))){
            int current=known(c,row.getSkillId());h.append("<font color=LEVEL>").append(escape(row.getName())).append("</font><br>Clan ").append(row.getGetLevel()).append(" | Aprendida ").append(current).append('/').append(row.getSkillLevel()).append("<br>");
            h.append(button(c.getLevel()<row.getGetLevel()?"Ver (bloqueada)":current>=row.getSkillLevel()?"Ver (completa)":"Ver / aprender","skill "+row.getSkillId()+" "+filter+" "+page)).append("<br>");
        }
        if(list.isEmpty())h.append("Sin habilidades para ese nivel.<br>");
        h.append("<table><tr>");if(page>0)h.append("<td>").append(button("Anterior","skills "+filter+" "+(page-1),125)).append("</td>");if(page+1<pages)h.append("<td>").append(button("Siguiente","skills "+filter+" "+(page+1),125)).append("</td>");
        return end(h.append("</tr></table>").append(button("Actualizar","skills "+filter+" "+page)).append(button("Volver","home")));
    }
    private void detail(Player p,int id,int filter,int page){
        SkillLearn max=catalog(filter).stream().filter(s->s.getSkillId()==id).findFirst().orElseThrow(()->new IllegalArgumentException("Skill fuera del catalogo."));
        int old=known(p.getClan(),id);Skill s=SkillData.getInstance().getSkill(id,Math.max(1,old));
        StringBuilder h=header(p,max.getName()).append("<img src=\"").append(escape(s.getIcon())).append("\" width=32 height=32><br>").append(escape(description(id))).append("<br><br>Clan requerido: ").append(max.getGetLevel()).append("<br>Aprendida: ").append(old).append('/').append(max.getSkillLevel()).append("<br>Rango minimo: ").append(rank(max)).append("<br>");
        boolean receives=SocialClass.values()[Math.clamp(p.getPledgeClass()+1,0,SocialClass.values().length-1)].ordinal()>=(max.getSocialClass()==null?0:max.getSocialClass().ordinal());
        h.append("Tu rango: ").append(SocialClass.values()[Math.clamp(p.getPledgeClass()+1,0,SocialClass.values().length-1)]).append(receives?" (cumple)<br>":" (no cumple)<br>");
        if(p.getClan().getLevel()<max.getGetLevel())h.append("<font color=FF7777>Sube el clan para aprenderla.</font><br>");
        else if(old>=max.getSkillLevel())h.append("Ya aprendida al maximo.<br>");
        else h.append(button("Aprender nivel "+(old+1),"learn "+id+" "+(old+1)+" "+filter+" "+page));
        h.append("<br>Son pasivas, salvo funciones especiales.<br>No requieren volver a buffearte.<br>").append(button("Volver","skills "+filter+" "+page));send(p,end(h));
    }
    static String description(int id){return switch(id){
        case 370->"Aumenta HP maximo.";case 371->"Aumenta CP maximo.";case 372->"Aumenta MP maximo.";
        case 373->"Mejora regeneracion de HP.";case 374->"Mejora regeneracion de CP.";case 375->"Mejora regeneracion de MP.";
        case 376->"Aumenta P. Atk.";case 377->"Aumenta P. Def.";case 378->"Aumenta M. Atk.";case 379->"Aumenta M. Def.";
        case 380->"Aumenta precision.";case 381->"Aumenta evasion.";case 382->"Mejora probabilidad de bloqueo con escudo.";case 383->"Mejora defensa del escudo.";
        case 384->"Resistencia a viento y agua.";case 385->"Resistencia a fuego y tierra.";case 386->"Resistencia a stun.";case 387->"Resistencia a root.";case 388->"Resistencia a sleep.";
        case 389->"Aumenta velocidad de movimiento.";case 390->"Reduce penalizaciones por muerte.";case 391->"Permite las funciones de clan para organizar una alianza de asedio.";default->"Habilidad nativa de clan.";};}
    private static String rank(SkillLearn s){return s.getSocialClass()==null?"Todos":s.getSocialClass().name();}
    private static StringBuilder header(Player p,String title){return new StringBuilder("<html><body><center><font color=LEVEL>").append(escape(title)).append("</font><br>").append(escape(p.getClan().getName())).append(" | Nivel ").append(p.getClan().getLevel()).append("<br>Reputacion: ").append(p.getClan().getReputationScore()).append("<br><br>");}
    private static String button(String title,String action){return button(title,action,260);}
    private static String button(String title,String action,int width){return "<button value=\""+escape(title)+"\" action=\"bypass -h voice .clanlab "+action+"\" width="+width+" height=22 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
    private static String escape(String s){return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;");}
    private static String end(StringBuilder h){return h.append("</center></body></html>").toString();}
    private static void send(Player p,String html){if(html.getBytes(java.nio.charset.StandardCharsets.UTF_8).length>8000)throw new IllegalStateException("Panel demasiado grande.");NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(html);p.sendPacket(packet);}
    public static void main(String[] args){new ClanLab();}
}
