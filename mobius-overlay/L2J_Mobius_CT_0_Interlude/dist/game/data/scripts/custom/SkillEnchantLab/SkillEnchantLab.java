package custom.SkillEnchantLab;

import java.nio.file.Path;
import java.sql.*;
import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.data.xml.SkillTreeData;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.ShortcutType;
import org.l2jmobius.gameserver.entity.actor.holders.player.Shortcut;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.network.serverpackets.*;

/** GM-only endpoint grant. Standard enchant probabilities remain unchanged. */
public class SkillEnchantLab extends Script implements IVoicedCommandHandler
{
    private static final Logger LOG=Logger.getLogger(SkillEnchantLab.class.getName());
    private final EnchantCatalog catalog;
    public SkillEnchantLab() throws Exception
    {
        catalog=new EnchantCatalog(Path.of("data"));
        try(Connection c=DatabaseFactory.getConnection();Statement s=c.createStatement())
        {s.executeUpdate("CREATE TABLE IF NOT EXISTS lab_skill_enchant_actions(action_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,observed_ms BIGINT NOT NULL,char_id INT NOT NULL,class_index INT NOT NULL,skill_id INT NOT NULL,old_level INT NOT NULL,new_level INT NOT NULL,route_name VARCHAR(80) NOT NULL) ENGINE=InnoDB");}
        VoicedCommandHandler.getInstance().registerHandler(this);
        LOG.info("SkillEnchantLab v1: .enchantskills / .encantar; Hellkevin GM; routes="+catalog.size());
    }
    public String[] getCommandList(){return new String[]{"enchantskills","encantar"};}
    public boolean onCommand(String command,Player p,String params)
    {
        if(!p.isGM() || !p.getName().equals("Hellkevin")){p.sendMessage("Enchant directo reservado a Hellkevin GM.");return true;}
        synchronized(p)
        {
            try
            {
                String[] args=params==null || params.isBlank()?new String[0]:params.trim().split("\\s+");
                if(args.length==0){showList(p,0);return true;}
                switch(args[0])
                {
                    case "page" -> showList(p,Integer.parseInt(args[1]));
                    case "skill" -> showSkill(p,Integer.parseInt(args[1]));
                    case "max" -> {apply(p,Integer.parseInt(args[1]),Integer.parseInt(args[2]),Integer.parseInt(args[3]));showSkill(p,Integer.parseInt(args[1]));}
                    default -> p.sendMessage("Usa .enchantskills");
                }
            }
            catch(Exception e){p.sendMessage("Enchant: "+e.getMessage());LOG.log(Level.WARNING,"SkillEnchantLab",e);}
        }
        return true;
    }
    private boolean eligible(Player p,EnchantCatalog.Route r)
    {
        Skill known=p.getKnownSkill(r.id());
        if(known==null || (known.getLevel()<100 && known.getLevel()<r.base())) return false;
        return SkillTreeData.getInstance().getCompleteClassSkillTree(p.getPlayerClass()).values().stream()
            .anyMatch(s->s.getSkillId()==r.id() && s.getSkillLevel()>=r.base()) && SkillData.getInstance().getSkill(r.id(),r.level())!=null;
    }
    private void apply(Player p,int id,int level,int slot) throws Exception
    {
        if(p.isDead() || p.isInCombat() || p.isCastingNow() || p.isAttackingNow() || p.getInstanceId()!=0) throw new IllegalStateException("Sal del combate, casteo y evento primero.");
        if(p.getLevel()<76 || p.getPlayerClass().level()!=3) throw new IllegalStateException("Activa una tercera profesion de nivel76 o mas.");
        if(slot!=p.getClassIndex()) throw new IllegalStateException("Cambio la clase activa; abre el menu de nuevo.");
        EnchantCatalog.Route r=catalog.find(id,level);
        if(r==null || !eligible(p,r)) throw new IllegalArgumentException("Skill/ruta no disponible para la clase activa.");
        Skill old=p.getKnownSkill(id),next=SkillData.getInstance().getSkill(id,level);
        if(old.getLevel()==level){p.sendMessage("Esa ruta ya esta al maximo.");return;}
        // Record intent before grant so a telemetry failure cannot silently change the character.
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement s=c.prepareStatement("INSERT INTO lab_skill_enchant_actions(observed_ms,char_id,class_index,skill_id,old_level,new_level,route_name) VALUES(?,?,?,?,?,?,?)"))
        {s.setLong(1,System.currentTimeMillis());s.setInt(2,p.getObjectId());s.setInt(3,slot);s.setInt(4,id);s.setInt(5,old.getLevel());s.setInt(6,level);s.setString(7,r.kind());s.executeUpdate();}
        p.addSkill(next,true);
        // Verify persistence; Player.addSkill logs database errors instead of throwing.
        try(Connection c=DatabaseFactory.getConnection();PreparedStatement s=c.prepareStatement("SELECT skill_level FROM character_skills WHERE charId=? AND class_index=? AND skill_id=?"))
        {s.setInt(1,p.getObjectId());s.setInt(2,slot);s.setInt(3,id);try(ResultSet rs=s.executeQuery()){if(!rs.next() || rs.getInt(1)!=level){p.addSkill(old,true);throw new IllegalStateException("No se pudo guardar; se restauro la skill previa.");}}}
        for(Shortcut sc:p.getAllShortcuts()) if(sc.getType()==ShortcutType.SKILL && sc.getId()==id)
        {Shortcut updated=new Shortcut(sc.getSlot(),sc.getPage(),sc.getType(),id,level);p.registerShortcut(updated);p.sendPacket(new ShortcutRegister(updated));}
        p.sendSkillList();p.broadcastUserInfo();
        p.sendMessage(r.name()+" +"+r.step()+" "+r.kind()+": aplicado y guardado. Sin EXP/SP, libros ni fallo.");
        LOG.info("ENCHANT_LAB APPLIED char="+p.getObjectId()+" slot="+slot+" skill="+id+" old="+old.getLevel()+" new="+level);
    }
    private void showList(Player p,int requested)
    {
        List<Skill> skills=p.getAllSkills().stream().filter(s->catalog.forSkill(s.getId()).stream().anyMatch(r->eligible(p,r)))
            .sorted(Comparator.comparing(Skill::getName)).toList();
        int pages=Math.max(1,(skills.size()+7)/8),page=Math.clamp(requested,0,pages-1);
        StringBuilder h=header("Enchant directo de skills");
        h.append("100% directo, sin libros, EXP ni SP.<br>Clase activa solamente; no otorga skills nuevas.<br>Pagina ").append(page+1).append('/').append(pages).append("<br>");
        for(Skill s:skills.subList(page*8,Math.min(skills.size(),page*8+8)))
            h.append(button(s.getName(),"skill "+s.getId())).append("<br>");
        if(skills.isEmpty()) h.append("Sin skills elegibles. Aprende el nivel normal maximo y activa su clase.<br>");
        if(page>0) h.append(button("Anterior","page "+(page-1)));
        if(page+1<pages) h.append(button("Siguiente","page "+(page+1)));
        send(p,h.append("</center></body></html>").toString());
    }
    private void showSkill(Player p,int id)
    {
        Skill known=p.getKnownSkill(id);if(known==null) throw new IllegalArgumentException("Skill no aprendida.");
        StringBuilder h=header(known.getName());
        h.append("Icono: <img src=\"").append(escape(known.getIcon())).append("\" width=32 height=32><br>");
        String current=catalog.forSkill(id).stream().filter(r->r.level()==known.getLevel()).map(r->"+"+r.step()+" "+r.kind()).findFirst().orElse("nivel interno "+known.getLevel());
        h.append("Actual: ").append(escape(current)).append("<br>Una ruta reemplaza la anterior; no se acumulan.<br>No modifica buffs ya activos: reaplica la skill.<br><br>");
        for(EnchantCatalog.Route r:catalog.forSkill(id)) if(eligible(p,r))
        {
            h.append("<font color=LEVEL>+").append(r.step()).append(' ').append(escape(r.kind())).append("</font><br>")
                .append(escape(EnchantCatalog.explanation(r.kind()))).append("<br>").append(escape(r.changes())).append("<br>")
                .append(button("Max "+r.kind()+" ruta "+((r.level()-101)/40+1),"max "+id+" "+r.level()+" "+p.getClassIndex())).append("<br><br>");
        }
        h.append(button("Volver","page 0"));send(p,h.append("</center></body></html>").toString());
    }
    private static StringBuilder header(String title){return new StringBuilder("<html><body><center><font color=LEVEL>").append(escape(title)).append("</font><br>");}
    private static String button(String title,String action){return "<button value=\""+escape(title)+"\" action=\"bypass -h voice .enchantskills "+action+"\" width=260 height=22 back=\"L2UI_ch3.smallbutton2_over\" fore=\"L2UI_ch3.smallbutton2\">";}
    private static String escape(String s){return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;");}
    private static void send(Player p,String h){NpcHtmlMessage packet=new NpcHtmlMessage();packet.setHtml(h);p.sendPacket(packet);}
    public static void main(String[] args) throws Exception{new SkillEnchantLab();}
}
