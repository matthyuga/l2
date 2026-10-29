package custom.ExplorationWalking;
import java.nio.file.*;
public class ExplorationPlacesTest {
    static int checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
    public static void main(String[] args)throws Exception {
        var places=new ExplorationPlaces(Path.of(args[0]));check(places.size()==167);
        var ketra=places.find(146990,-67128,-3640);check(ketra!=null&&ketra.name.equals("Ketra Orc Outpost"));
        // Deep inside the actual Ketra spawn polygon, far beyond the entry circle.
        ketra=places.find(137500,-90200,-3600);check(ketra!=null&&ketra.name.equals("Ketra Orc Outpost"));
        check(places.find(146990,-67128,25000)==null);check(places.find(-131000,300000,0)==null);
        var tracker=new ExplorationPlaces.Tracker();
        check(!tracker.enter("ketra",0));check(tracker.enter("ketra",1000));
        check(!tracker.enter("ketra",2000));check(!tracker.enter("",3000));check(!tracker.enter("ketra",4000));check(!tracker.enter("ketra",5000));
        check(!tracker.enter("",6000));check(!tracker.enter("",7000));
        check(!tracker.enter("ketra",8000));check(!tracker.enter("ketra",9000));check(tracker.enter("ketra",13000));
        check(!tracker.enter("varka",14000));check(!tracker.enter("varka",15000));check(tracker.enter("varka",25000));
        check(!tracker.enter("goddard",26000));check(!tracker.enter("varka",27000));check(!tracker.enter("varka",28000));
        System.out.println("PASS "+checks+" place checks: Ketra entry/interior, height, unknown terrain, stable entry, re-entry and border cooldown.");
    }
}
