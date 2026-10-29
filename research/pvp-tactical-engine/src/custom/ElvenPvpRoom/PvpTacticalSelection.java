package custom.ElvenPvpRoom;
/** Optional exact profile selection for repeatable isolated trials; empty during ordinary room use. */
public final class PvpTacticalSelection {
 private static final ThreadLocal<Integer> REQUESTED=new ThreadLocal<>();
 public static int requested(){Integer id=REQUESTED.get();return id==null?0:id;}
 public static void request(int id){REQUESTED.set(id);}
 public static void clear(){REQUESTED.remove();}
}
