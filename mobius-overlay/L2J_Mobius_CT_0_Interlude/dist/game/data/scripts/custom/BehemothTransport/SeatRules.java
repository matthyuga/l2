package custom.BehemothTransport;

/** Transport policy and transforms shared by runtime and deterministic tests. */
public final class SeatRules
{
    public enum Role { DRIVER, GUNNER }
    public record Point(int x,int y,int z) { }
    public static Point world(int x,int y,int z,int heading,Role role)
    {
        double angle=(heading & 65535)*Math.PI/32768.0;
        double forward=role==Role.DRIVER?6.75:-38;
        return new Point((int)Math.round(x+forward*Math.cos(angle)),(int)Math.round(y+forward*Math.sin(angle)),z+(role==Role.DRIVER?102:91));
    }
    public static boolean boardingRange(int dx,int dy,int dz,boolean sameInstance)
    {
        return sameInstance && (long)dx*dx+(long)dy*dy<=200L*200 && Math.abs((long)dz)<=120;
    }
    public static final class Seats
    {
        private int driver,gunner;private boolean closed;
        public synchronized boolean board(Role role,int id)
        {
            if(closed || id<=0 || driver==id || gunner==id)return false;
            if(role==Role.DRIVER){if(driver!=0)return false;driver=id;}
            else{if(gunner!=0)return false;gunner=id;}
            return true;
        }
        public synchronized Role leave(int id)
        {
            if(id<=0)return null;
            if(driver==id){driver=0;return Role.DRIVER;}
            if(gunner==id){gunner=0;return Role.GUNNER;}
            return null;
        }
        public synchronized int driver(){return driver;}
        public synchronized int gunner(){return gunner;}
        public synchronized void close(){closed=true;driver=0;gunner=0;}
        public synchronized boolean closed(){return closed;}
    }
}
