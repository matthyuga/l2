import java.nio.file.Path;
import custom.SkillEnchantLab.EnchantCatalog;
public class EnchantCatalogCheck
{
    private static int checks;
    private static void check(boolean v){checks++;if(!v)throw new AssertionError("check "+checks);}
    public static void main(String[] args) throws Exception
    {
        var c=new EnchantCatalog(Path.of(args[0]));
        check(c.size()>100);
        var hydro=c.find(1235,130);check(hydro!=null);check(hydro.step()==30);check(hydro.kind().equals("Power"));
        check(hydro.changes().contains("108 -> 127"));
        var cost=c.find(1235,170);check(cost.changes().contains("55 -> 31"));check(cost.changes().contains("14 -> 7"));
        var surrender=c.find(1071,130);check(surrender.changes().contains("80 -> 100"));
        check(c.forSkill(1340).isEmpty());check(c.forSkill(337).isEmpty());
        check(c.find(1235,101)==null);check(c.find(1235,999)==null);check(c.find(-1,130)==null);
        check(c.find(1059,130).changes().contains("1200 -> 2400"));
        check(!c.find(1059,130).changes().contains("mAtk"));
        check(c.find(205,130)!=null && c.find(205,170)!=null);
        check(c.find(205,130).changes().contains("runSpd: 0 -> 20"));
        check(c.find(205,170).changes().contains("critDmgAdd: 0 -> 515"));
        for(int id=1;id<10000;id++) for(var r:c.forSkill(id))
        {check(r.id()==id);check(r.step()>0);check(r.base()>0);check(c.find(id,r.level())==r);check(!r.changes().contains("#"));}
        System.out.println("PASS "+checks+" catalog checks; "+c.size()+" maximum routes read from installed datapack");
    }
}
