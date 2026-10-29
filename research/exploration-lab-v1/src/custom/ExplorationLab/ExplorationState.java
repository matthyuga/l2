package custom.ExplorationLab;

import java.io.*;
import java.nio.file.*;
import java.util.Properties;
import java.util.UUID;

/** One isolated test region. Global data is independent of player variables. */
public final class ExplorationState
{
    public record Region(String id, int x, int y, int z, int instance, boolean revealed)
    {
        public boolean contains(int px, int py, int pz, int pi, int radius)
        {
            long dx=(long)px-x, dy=(long)py-y;
            return pi==instance && Math.abs((long)pz-z)<=180 && Math.abs(dx)<=radius
                && Math.abs(dy)<=radius && dx*dx+dy*dy<=(long)radius*radius;
        }
        public String visitKey(){return "EXPLAB_VISIT_"+id;}
        public String surveyKey(){return "EXPLAB_SURVEY_"+id;}
    }
    public enum Fog { TOTAL, PARTIAL, CLEAR }
    private final Path file;
    private Region region;
    public ExplorationState(Path file) throws IOException
    {
        this.file=file;
        if(Files.exists(file))
        {
            Properties p=new Properties();
            try(InputStream in=Files.newInputStream(file)){p.load(in);}
            try
            {
                String id=p.getProperty("id"); UUID.fromString(id);
                String visible=p.getProperty("revealed");
                if(!"true".equals(visible)&&!"false".equals(visible))throw new IllegalArgumentException("Invalid revealed flag");
                region=new Region(id,Integer.parseInt(p.getProperty("x")),Integer.parseInt(p.getProperty("y")),
                    Integer.parseInt(p.getProperty("z")),Integer.parseInt(p.getProperty("instance")),Boolean.parseBoolean(visible));
            }
            catch(RuntimeException e){throw new IOException("Invalid exploration state; original file preserved",e);}
        }
    }
    public synchronized Region current(){return region;}
    public synchronized Region anchor(int x,int y,int z,int instance) throws IOException
    {
        if(instance!=0)throw new IllegalArgumentException("Test region must be in the shared world");
        Region next=new Region(UUID.randomUUID().toString(),x,y,z,instance,false);
        persist(next);region=next;return next;
    }
    public synchronized boolean reveal() throws IOException
    {
        if(region==null)throw new IllegalStateException("No region anchored");
        if(region.revealed())return false;
        Region next=new Region(region.id(),region.x(),region.y(),region.z(),region.instance(),true);
        persist(next);region=next;return true;
    }
    public static Fog fog(Region r,boolean personallySurveyed)
    {
        return r==null||!r.revealed()?Fog.TOTAL:personallySurveyed?Fog.CLEAR:Fog.PARTIAL;
    }
    private void persist(Region r) throws IOException
    {
        Path parent=file.toAbsolutePath().getParent();Files.createDirectories(parent);
        Properties p=new Properties();p.setProperty("id",r.id());p.setProperty("x",""+r.x());p.setProperty("y",""+r.y());
        p.setProperty("z",""+r.z());p.setProperty("instance",""+r.instance());p.setProperty("revealed",""+r.revealed());
        Path tmp=Files.createTempFile(parent,"exploration-",".tmp");
        try
        {
            try(OutputStream out=Files.newOutputStream(tmp)){p.store(out,"Exploration lab only; no campaign state");}
            // Same-directory atomic replacement: fail without changing in-memory state if unsupported.
            Files.move(tmp,file,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
        }
        finally{Files.deleteIfExists(tmp);}
    }
}
