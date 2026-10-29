package org.l2jmobius.gameserver.network.serverpackets;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import org.l2jmobius.gameserver.data.xml.SkillTreeData;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.mechanics.skill.Skill;

/** Presentation only: never mutates known skills, shortcuts or the active class. */
public final class SkillCatalogView
{
    public static final String FILTER="LAB_SKILL_CATALOG_FILTER", ORDER="LAB_SKILL_CATALOG_ORDER";
    public static final int ALL=-1, COMMON=4, AMBER=5, OTHER=6;
    // Client-only decoration IDs: never learned, registered as skills or saved.
    public static final int HEADER_BASE=19100, PADDING=19199, COLUMNS=6;
    public static boolean decoration(int id){return id>=HEADER_BASE&&id<HEADER_BASE+7*COLUMNS||id==PADDING;}
    public static int nextClass(Player p)
    {
        List<Integer> slots=new ArrayList<>(classes(p).keySet());
        int index=slots.indexOf(filter(p));
        return slots.get((index+1)%slots.size());
    }
    /** Exact actions emitted by our native windows, which have no HTML action cache. */
    public static boolean nativeWindowAction(String action)
    {
        return action!=null&&Set.of(
            "voice .habilidades",
            "voice .habilidades next",
            "voice .habilidades quick -1",
            "voice .habilidades quick 0",
            "voice .habilidades quick 1",
            "voice .habilidades quick 2",
            "voice .habilidades quick 3",
            "voice .habilidades quick 4",
            "voice .habilidades quick 5",
            "voice .amber toggle",
            "voice .sticker 1",
            "voice .sticker 2",
            "voice .sticker 3",
            "voice .sticker 4",
            "voice .sticker 5",
            "voice .sticker 6",
            "voice .sticker 7",
            "voice .sticker 8",
            "voice .sticker 9",
            "voice .sticker 10",
            "voice .sticker 11",
            "voice .sticker 12",
            "voice .sticker 13",
            "voice .sticker 14",
            "voice .sticker 15",
            "voice .sticker 16",
            "voice .sticker 17",
            "voice .sticker 18",
            "voice .sticker 19"
        ).contains(action);
    }
    private static final Map<PlayerClass,Set<Integer>> TREES=new ConcurrentHashMap<>();
    private SkillCatalogView(){}
    public static Map<Integer,PlayerClass> classes(Player p)
    {
        Map<Integer,PlayerClass> result=new LinkedHashMap<>();
        result.put(0,PlayerClass.getPlayerClass(p.getBaseClass()));
        p.getSubClasses().entrySet().stream().sorted(Map.Entry.comparingByKey())
            .forEach(e->result.put(e.getKey(),PlayerClass.getPlayerClass(e.getValue().getId())));
        return result;
    }
    public static boolean amber(int id){return id>=19001&&id<=19014;}
    public static Set<Integer> tree(PlayerClass c)
    {
        return TREES.computeIfAbsent(c,key->SkillTreeData.getInstance().getCompleteClassSkillTree(key).values().stream()
            .map(s->s.getSkillId()).collect(Collectors.toUnmodifiableSet()));
    }
    public static Model model(Player p)
    {
        Map<Integer,PlayerClass> classes=classes(p);
        Map<Integer,List<Integer>> origins=new HashMap<>();
        for(var entry:classes.entrySet())for(int id:tree(entry.getValue()))
            origins.computeIfAbsent(id,key->new ArrayList<>()).add(entry.getKey());
        return new Model(classes,origins,p.getVariables().getString(ORDER,"main").equals("active")?p.getClassIndex():0);
    }
    public static int filter(Player p)
    {
        int selected=p.getVariables().getInt(FILTER,ALL);
        return selected<ALL||selected>OTHER||selected>=0&&selected<=3&&!classes(p).containsKey(selected)?ALL:selected;
    }
    public record Model(Map<Integer,PlayerClass> classes,Map<Integer,List<Integer>> origins,int firstSlot)
    {
        public int group(int id)
        {
            if(amber(id))return AMBER;
            List<Integer> slots=origins.getOrDefault(id,List.of());
            return slots.size()>1?COMMON:slots.isEmpty()?OTHER:slots.getFirst();
        }
        public boolean visible(int id,int filter)
        {
            if(filter==ALL)return true;
            if(filter>=0&&filter<=3)return origins.getOrDefault(id,List.of()).contains(filter)&&!amber(id);
            return group(id)==filter;
        }
        public int rank(int id)
        {
            int group=group(id);
            return group==firstSlot?0:group+1;
        }
        public String origin(int id)
        {
            if(amber(id))return "Contrato Amber";
            List<Integer> slots=origins.getOrDefault(id,List.of());
            return slots.isEmpty()?"Especial / sin clase":slots.stream().map(s->className(classes.get(s))).collect(Collectors.joining(" / "));
        }
        public Comparator<Skill> comparator()
        {
            return Comparator.comparingInt((Skill skill)->rank(skill.getId()))
                .thenComparing(Skill::getName,String.CASE_INSENSITIVE_ORDER).thenComparingInt(Skill::getId);
        }
    }
    public static String className(PlayerClass c)
    {
        if(c==null)return "Clase";
        return switch(c.getId()){
            case 103->"Mystic Muse / Spellsinger";case 116->"Dominator / Overlord";case 97->"Cardinal / Bishop";
            case 90->"Phoenix Knight / Paladin";case 91->"Hell Knight / Dark Avenger";
            default->java.util.Arrays.stream(c.name().split("_")).map(s->s.charAt(0)+s.substring(1).toLowerCase()).collect(Collectors.joining(" "));
        };
    }
}
