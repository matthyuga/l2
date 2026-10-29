package custom.ExplorationLab;
import java.nio.file.*;
public class ExplorationStateTest
{
    private static int checks;
    private static void check(boolean value){checks++;if(!value)throw new AssertionError("Check "+checks);}
    public static void main(String[] args) throws Exception
    {
        Path dir=Files.createTempDirectory("exploration-state-test-");Path file=dir.resolve("region.properties");
        try
        {
            ExplorationState s=new ExplorationState(file);check(s.current()==null);
            var r=s.anchor(-1000,2000,-3000,0);
            check(r.contains(-400,2000,-3000,0,600));check(!r.contains(-399,2000,-3000,0,600));
            check(!r.contains(-1000,2000,-2819,0,600));check(!r.contains(-1000,2000,-3000,1,600));
            check(!r.contains(Integer.MAX_VALUE,Integer.MIN_VALUE,-3000,0,600));
            check(ExplorationState.fog(r,false)==ExplorationState.Fog.TOTAL);
            check(ExplorationState.fog(r,true)==ExplorationState.Fog.TOTAL);
            check(s.reveal());check(!s.reveal());
            // A surveyed the beacon; B did not. Global reveal must preserve that distinction.
            check(ExplorationState.fog(s.current(),true)==ExplorationState.Fog.CLEAR);
            check(ExplorationState.fog(s.current(),false)==ExplorationState.Fog.PARTIAL);
            var loaded=new ExplorationState(file).current();check(loaded.equals(s.current()));
            check(loaded.surveyKey().equals(r.surveyKey()));check(!loaded.surveyKey().equals(loaded.visitKey()));
            var next=s.anchor(0,0,0,0);check(!next.id().equals(r.id()));check(!next.revealed());
            check(!next.surveyKey().equals(r.surveyKey()));
            try{s.anchor(0,0,0,1);throw new AssertionError("Private instance accepted");}catch(IllegalArgumentException expected){check(s.current().equals(next));}
            Files.writeString(file,"broken=true");
            try{new ExplorationState(file);throw new AssertionError("Corrupt state accepted");}catch(java.io.IOException expected){check(Files.readString(file).equals("broken=true"));}
            // Persistence failure must not mark an unrecovered region as globally recovered.
            Path blocked=dir.resolve("blocked");Files.writeString(blocked,"not a directory");
            ExplorationState failure=new ExplorationState(blocked.resolve("region.properties"));
            try{failure.anchor(0,0,0,0);throw new AssertionError("Invalid path accepted");}catch(java.io.IOException expected){check(failure.current()==null);}
            System.out.println("PASS "+checks+" checks: geometry, instances, dual fog, restart, revision, corrupt state and write failure.");
        }
        finally{try(var paths=Files.walk(dir)){for(Path p:paths.sorted(java.util.Comparator.reverseOrder()).toList())Files.delete(p);}}
    }
}
