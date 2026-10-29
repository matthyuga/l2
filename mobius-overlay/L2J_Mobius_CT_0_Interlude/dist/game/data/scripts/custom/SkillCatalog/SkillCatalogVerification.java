package custom.SkillCatalog;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.commons.network.pool.ResourcePool;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.holders.player.SubClassHolder;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView;
import org.l2jmobius.gameserver.network.serverpackets.SkillList;

/** Opt-in wire/catalog test using only the reserved offline AmberOwnerProbe, without saving grants. */
public class SkillCatalogVerification extends Script
{
    private static final Logger LOG=Logger.getLogger(SkillCatalogVerification.class.getName());
    private int checks;
    public SkillCatalogVerification(){if(Boolean.getBoolean("lab.catalog.verify"))ThreadPool.schedule(this::verify,30000);}
    private void check(boolean value,String message){if(!value)throw new IllegalStateException(message);checks++;}
    private void verify()
    {
        Player p=null;int base=0;Map<Integer,SubClassHolder> subs=null;
        try{
            int id;
            try(Connection c=DatabaseFactory.getConnection();PreparedStatement q=c.prepareStatement("SELECT charId,online FROM characters WHERE char_name='AmberOwnerProbe' AND account_name='ambercontracttest'"))
            {try(var r=q.executeQuery()){if(!r.next()||r.getInt(2)!=0||World.getPlayer(r.getInt(1))!=null)throw new IllegalStateException("Reserved offline probe unavailable");id=r.getInt(1);}}
            p=Player.load(id);if(p==null)throw new IllegalStateException("Probe load failed");
            check(p.validateHtmlAction("voice .habilidades quick 0")==-1&&SkillCatalogView.nativeWindowAction("voice .habilidades quick 0"),"Native filter works without an HTML cache");
            for(String action:new String[]{"voice .habilidades","voice .habilidades next","voice .habilidades quick -1","voice .habilidades quick 0","voice .habilidades quick 1","voice .habilidades quick 2","voice .habilidades quick 3","voice .habilidades quick 4","voice .habilidades quick 5","voice .amber toggle"})check(SkillCatalogView.nativeWindowAction(action),"Native window exact action permitted "+action);
            for(String action:new String[]{"voice .raza apply","voice .amber contract","voice .amber toggle other","voice .habilidades quick 0 extra","voice .habilidades quick 99","admin_give_item","npc_123_Quest",null})check(!SkillCatalogView.nativeWindowAction(action),"Other actions retain existing HTML validation");
            base=p.getBaseClass();subs=new HashMap<>(p.getSubClasses());
            p.setBaseClass(116);p.getSubClasses().clear();
            p.getSubClasses().put(1,new SubClassHolder(103,1));p.getSubClasses().put(2,new SubClassHolder(90,2));p.getSubClasses().put(3,new SubClassHolder(97,3));
            var model=SkillCatalogView.model(p);
            for(var c:model.classes().values())for(int skillId:SkillCatalogView.tree(c))
                if(p.getKnownSkill(skillId)==null){var s=SkillData.getInstance().getSkill(skillId,1);if(s!=null)p.addSkill(s,false);}
            for(int skillId:new int[]{19001,19002,19003,19004,19014})p.addSkill(SkillData.getInstance().getSkill(skillId,1),false);
            var before=p.getAllSkills().stream().collect(java.util.stream.Collectors.toMap(s->s.getId(),s->s.getLevel()));
            int activeClass=p.getClassIndex();var shortcutCount=p.getAllShortcuts().size();
            SkillList packet=new SkillList();for(var s:p.getAllSkills())packet.addSkill(s.getId(),s.getLevel(),s.isPassive(),s.getId()==19003);
            p.getVariables().set(SkillCatalogView.FILTER,-1);
            var all=packet.presentedSkillIds(p);
            check(all.size()==before.size()&&new HashSet<>(all).size()==all.size(),"All learned skills preserved without duplicates");
            check(p.getAllSkills().stream().filter(s->!s.isPassive()).count()>80,"Fixture exceeds the original 80 active-skill client cap");
            check(all.contains(19014),"Native all-skills presentation includes Amber toggle beyond the old cap");
            for(int group=0;group<=6;group++){
                p.getVariables().set(SkillCatalogView.FILTER,group);
                var ids=packet.presentedSkillIds(p);final int selected=group;
                check(ids.stream().allMatch(skillId->model.visible(skillId,selected)),"Filter "+group+" contains only matching skills");
                check(ids.size()==before.keySet().stream().filter(skillId->model.visible(skillId,selected)).count(),"Filter "+group+" is complete");
            }
            p.getVariables().set(SkillCatalogView.FILTER,5);
            check(packet.presentedSkillIds(p).equals(java.util.List.of(19014,19002,19001,19003,19004)),"Amber filter presents five named contract skills including toggle");
            String html=SkillCatalog.html(p,0);
            check(html.contains("Asistencia de Amber")&&html.contains("Activable")&&html.contains("Alt+K")&&html.length()<8100,"Amber index shows activable and native catalog instructions");
            p.getVariables().set(SkillCatalogView.FILTER,-1);
            int previous=-1;for(int skillId:packet.presentedSkillIds(p)){int rank=model.rank(skillId);check(rank>=previous,"Native packet class groups are contiguous");previous=rank;}
            int shared=model.origins().entrySet().stream().filter(e->e.getValue().size()>1&&!SkillCatalogView.amber(e.getKey())&&before.containsKey(e.getKey())).findFirst().orElseThrow().getKey();
            check(model.group(shared)==SkillCatalogView.COMMON,"Shared skills grouped as Common globally");
            for(int slot:model.origins().get(shared))check(model.visible(shared,slot),"Shared skill remains visible in compatible class "+slot);
            p.getVariables().set(SkillCatalogView.FILTER,99);check(SkillCatalogView.filter(p)==-1,"Invalid filter falls back to all");
            p.getVariables().set(SkillCatalogView.ORDER,"active");check(SkillCatalogView.model(p).firstSlot()==p.getClassIndex(),"Active-first order follows active slot");
            var activeFirst=new SkillCatalogView.Model(model.classes(),model.origins(),2);
            int uniquePaladin=before.keySet().stream().filter(skillId->model.group(skillId)==2).findFirst().orElseThrow();
            check(activeFirst.rank(uniquePaladin)==0,"A non-main active slot can receive first priority");
            p.getVariables().set(SkillCatalogView.FILTER,-1);
            ResourcePool pool=new ResourcePool();WriteBuffer wire=new WriteBuffer(pool,SkillList.class);packet.writeForPlayer(p,wire);
            wire.mark();
            ByteBuffer data=ByteBuffer.wrap(wire.toByteArray()).order(ByteOrder.LITTLE_ENDIAN);
            wire.releaseResources();
            var ids=packet.wireSkillIds(p);
            check((data.get()&255)==0x58&&data.getInt()==ids.size(),"Native Interlude SkillList opcode and actual count beyond original cap");
            check(p.getAllSkills().stream().anyMatch(s->s.isPassive()),"Native wire includes real passive skills");
            int[] cells={0,0},headerRemaining={0,0},groups={-1,-1};java.util.Set<Integer> real=new HashSet<>();
            for(int skillId:ids){
                int passive=data.getInt(),level=data.getInt(),wireId=data.getInt(),disabled=data.get()&255;
                check(passive>=0&&passive<=1&&wireId==skillId,"Wire entry and passive flag "+skillId);
                if(SkillCatalogView.decoration(skillId)){
                    check(level==1&&disabled==1&&p.getKnownSkill(skillId)==null&&SkillData.getInstance().getMaxLevel(skillId)==0,"Decoration is disabled and is never a real learned skill");
                    if(skillId!=SkillCatalogView.PADDING){
                        int group=(skillId-SkillCatalogView.HEADER_BASE)/6,tile=(skillId-SkillCatalogView.HEADER_BASE)%6;
                        if(tile==0){check(cells[passive]%6==0,"Section begins on a fresh row for active/passive "+passive);groups[passive]=group;headerRemaining[passive]=6;}
                        check(headerRemaining[passive]==6-tile&&groups[passive]==group,"Six consecutive decorative tiles form the thick separator");headerRemaining[passive]--;
                    }else check(headerRemaining[passive]==0,"Padding stays outside the header");
                }else{
                    var skill=p.getKnownSkill(skillId);check(passive==(skill.isPassive()?1:0)&&level==skill.getLevel()&&disabled==(skillId==19003?1:0),"Wire preserves real skill level/type/disabled state "+skillId);
                    check(headerRemaining[passive]==0&&groups[passive]==model.group(skillId),"Real skill follows its complete class separator");real.add(skillId);
                }
                cells[passive]++;
            }
            check(real.equals(before.keySet()),"Every learned skill occurs after a header with no lost real skill");
            check(!data.hasRemaining(),"Wire count exactly matches serialized skill records");
            // Cycle only actual owned slots, for characters with one through four classes.
            var fixtureSubs=new HashMap<>(p.getSubClasses());
            var handler=org.l2jmobius.gameserver.handler.BypassHandler.getInstance().getHandler("voice .habilidades next");
            check(handler!=null,"Native voice bypass handler is registered");
            for(int classCount=1;classCount<=4;classCount++){
                p.getSubClasses().clear();for(int slot=1;slot<classCount;slot++)p.getSubClasses().put(slot,fixtureSubs.get(slot));
                p.getVariables().set(SkillCatalogView.FILTER,-1);
                for(int step=0;step<classCount*2+1;step++){
                    int expected=step%classCount;
                    check(SkillCatalogView.nextClass(p)==expected,"Next class skips missing slots; count="+classCount);
                    check(handler.onCommand("voice .habilidades next",p,null)&&SkillCatalogView.filter(p)==expected,"Actual native voice bypass selects class "+expected);
                    var cycleModel=SkillCatalogView.model(p);
                    check(packet.presentedSkillIds(p).stream().allMatch(skillId->cycleModel.visible(skillId,expected)),"Class cycle filters only compatible skills");
                }
            }
            p.getSubClasses().clear();p.getSubClasses().putAll(fixtureSubs);
            p.getVariables().set(SkillCatalogView.FILTER,-1);
            check(before.equals(p.getAllSkills().stream().collect(java.util.stream.Collectors.toMap(s->s.getId(),s->s.getLevel())))&&p.getClassIndex()==activeClass&&p.getAllShortcuts().size()==shortcutCount,"Filtering changes no skills, levels, active class or shortcuts");
            LOG.info("SkillCatalogVerification SUCCESS: "+checks+" checks; native wire, thick section headers, active/passive row alignment, Next for 1-4 classes, shared skills, Amber toggle, filters and no gameplay mutations.");
        }catch(Exception e){LOG.log(java.util.logging.Level.SEVERE,"SkillCatalogVerification FAILED after "+checks+" checks",e);}
        finally{if(p!=null){p.getVariables().remove(SkillCatalogView.FILTER);p.getVariables().remove(SkillCatalogView.ORDER);p.setBaseClass(base);p.getSubClasses().clear();if(subs!=null)p.getSubClasses().putAll(subs);p.setOnlineStatus(true,false);p.deleteMe();}}
    }
    public static void main(String[] args){new SkillCatalogVerification();}
}
