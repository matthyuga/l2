package custom.GroupAgite;

/** Pure event rules and decision priorities, independent of the game engine. */
public final class GroupPolicy
{
    private GroupPolicy() {}
    public static final int WIN_POINTS=3;
    public static final class Ladder
    {
        public final int[] points=new int[3];
        public int holder=0,challenger=1,waiting=2,round=1,champion=-1;
        public void win(int team)
        {
            if(champion>=0 || (team!=holder && team!=challenger)) throw new IllegalArgumentException("Inactive winner");
            int loser=team==holder?challenger:holder;
            if(++points[team]>=WIN_POINTS) {champion=team;return;}
            holder=team;challenger=waiting;waiting=loser;round++;
        }
    }
    public static double concern(double hp,double pressure,boolean leader,boolean healer)
    {return (1-hp)*100+Math.min(100,pressure)+(leader?12:0)+(healer?10:0)+(hp<.25?60:0);}
    public static boolean heal(double hp,double pressure) {return hp<.65 || (hp<.85 && pressure>20);}
    public static boolean massRevive(int dead,double hp,boolean threatened)
    {return dead>=2 && (!threatened || (dead==3 && hp<.30));}
    public static boolean focusPet(double petHp,boolean transferPain,int threats,double leaderHp)
    {return leaderHp>.30 && threats<2 && (petHp<.35 || transferPain);}
    public static boolean canSummon(int attempts,double hp,boolean preparation)
    {return attempts<2 && (preparation || hp>.60);}
}
