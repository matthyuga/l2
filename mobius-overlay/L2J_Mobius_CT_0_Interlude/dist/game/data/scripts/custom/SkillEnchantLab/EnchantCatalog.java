package custom.SkillEnchantLab;

import java.nio.file.*;
import java.util.*;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

/** Read actual enchant endpoints, never synthesize skill levels. */
public final class EnchantCatalog
{
    public record Route(int id,int level,int base,int step,String name,String kind,String changes) {}
    private final Map<Integer,List<Route>> routes=new TreeMap<>();
    public EnchantCatalog(Path data) throws Exception
    {
        var factory=DocumentBuilderFactory.newInstance();
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
        factory.setFeature("http://xml.org/sax/features/external-general-entities",false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities",false);
        Map<String,Route> ends=new TreeMap<>();
        NodeList entries=factory.newDocumentBuilder().parse(data.resolve("EnchantSkillTreeData.xml").toFile()).getElementsByTagName("skill");
        for(int i=0;i<entries.getLength();i++)
        {
            Element e=(Element)entries.item(i);String desc=e.getAttribute("desc");
            if(!desc.matches("\\+\\d+ .+")) continue;
            int space=desc.indexOf(' '),step=Integer.parseInt(desc.substring(1,space));
            Route r=new Route(Integer.parseInt(e.getAttribute("id")),Integer.parseInt(e.getAttribute("level")),Integer.parseInt(e.getAttribute("baseLevel")),step,e.getAttribute("name"),desc.substring(space+1),"");
            String key=r.id()+":"+(r.level()-r.step());Route old=ends.get(key);
            if(old==null || r.step()>old.step()) ends.put(key,r);
        }
        Map<Integer,Element> definitions=new HashMap<>();
        try(var files=Files.list(data.resolve("stats/skills")))
        {
            for(Path file:files.filter(p->p.toString().endsWith(".xml")).toList())
            {
                NodeList skills=factory.newDocumentBuilder().parse(file.toFile()).getElementsByTagName("skill");
                for(int i=0;i<skills.getLength();i++) {Element e=(Element)skills.item(i);definitions.put(Integer.parseInt(e.getAttribute("id")),e);}
            }
        }
        for(Route r:ends.values())
        {
            Element def=definitions.get(r.id());if(def==null) continue;
            int group=(r.level()-101)/40+1;List<String> changes=new ArrayList<>();
            for(Element e:children(def,"enchant"+group))
            {
                String property=e.getAttribute("name");
                String before="";for(Element original:children(def,property)) before=resolve(def,original.getTextContent(),r.base());
                String after=resolve(def,e.getTextContent(),r.step());
                if(!before.equals(after)) changes.add(label(property)+": "+before+" -> "+after);
            }
            for(Element effects:children(def,"enchant"+group+"effects"))
                for(String operation:List.of("add","mul","sub"))
                {
                    NodeList stats=effects.getElementsByTagName(operation);
                    for(int i=0;i<stats.getLength();i++)
                    {
                        Element stat=(Element)stats.item(i);String name=stat.getAttribute("stat");
                        String after=resolve(def,stat.getElementsByTagName("value").getLength()>0?stat.getElementsByTagName("value").item(0).getTextContent():stat.getTextContent(),r.step());
                        String before=operation.equals("mul")?"1":"0";
                        for(Element originalEffects:children(def,"effects"))
                        {
                            NodeList originals=originalEffects.getElementsByTagName(operation);
                            for(int j=0;j<originals.getLength();j++)
                            {
                                Element original=(Element)originals.item(j);
                                if(original.getAttribute("stat").equals(name)) before=resolve(def,original.getElementsByTagName("value").getLength()>0?original.getElementsByTagName("value").item(0).getTextContent():original.getTextContent(),r.base());
                            }
                        }
                        if(!before.equals(after)) changes.add(operation+" "+name+": "+before+" -> "+after+(stat.getElementsByTagName("using").getLength()>0?" ("+((Element)stat.getElementsByTagName("using").item(0)).getAttribute("kind")+")":""));
                    }
                }
            Route full=new Route(r.id(),r.level(),r.base(),r.step(),r.name(),r.kind(),String.join("; ",changes));
            routes.computeIfAbsent(r.id(),id->new ArrayList<>()).add(full);
        }
        routes.replaceAll((id,list)->List.copyOf(list));
    }
    private static List<Element> children(Element parent,String tag)
    {
        List<Element> result=new ArrayList<>();
        for(Node n=parent.getFirstChild();n!=null;n=n.getNextSibling()) if(n instanceof Element e && e.getTagName().equals(tag)) result.add(e);
        return result;
    }
    private static String resolve(Element def,String text,int level)
    {
        text=text.trim();if(!text.startsWith("#")) return text;
        for(Element table:children(def,"table")) if(table.getAttribute("name").equals(text))
        {String[] values=table.getTextContent().trim().split("\\s+");return values[Math.min(values.length,level)-1];}
        return text;
    }
    private static String label(String property)
    {
        return switch(property){case "power"->"Potencia";case "activateRate"->"Activacion base (no chance final)";case "magicLevel"->"Nivel magico";case "mpConsume"->"MP de casteo";case "mpInitialConsume"->"MP inicial";case "abnormalTime"->"Duracion (s)";case "reuseDelay"->"Reuse (ms)";default->property;};
    }
    public List<Route> forSkill(int id){return routes.getOrDefault(id,List.of());}
    public Route find(int id,int level){return forSkill(id).stream().filter(r->r.level()==level).findFirst().orElse(null);}
    public int size(){return routes.values().stream().mapToInt(List::size).sum();}
    public static String explanation(String kind)
    {
        return switch(kind.toLowerCase(Locale.ROOT)){
            case "power"->"Mejora potencia/efecto segun la skill; revisar cambios y condiciones.";
            case "cost"->"Reduce consumo de MP; no suma la ruta Power.";
            case "chance"->"Mejora aplicacion del efecto; depende de las reglas y resistencias.";
            case "time"->"Aumenta duracion; no implica mayor intensidad del buff.";
            case "recovery"->"Reduce tiempo de reutilizacion.";
            default->"Ruta definida por el datapack; revisar los cambios indicados.";
        };
    }
}
