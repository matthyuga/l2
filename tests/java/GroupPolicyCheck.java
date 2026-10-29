import custom.GroupAgite.GroupPolicy;
public class GroupPolicyCheck
{
    private static int checks;
    private static void check(boolean value) {checks++;if(!value) throw new AssertionError("check="+checks);}
    private static void walk(GroupPolicy.Ladder l,int decisive)
    {
        check(l.holder!=l.challenger && l.holder!=l.waiting && l.challenger!=l.waiting);
        check(l.points[l.holder]<3 && l.points[l.challenger]<3 && l.points[l.waiting]<3);
        for(int winner:new int[]{l.holder,l.challenger})
        {
            GroupPolicy.Ladder n=new GroupPolicy.Ladder();System.arraycopy(l.points,0,n.points,0,3);
            n.holder=l.holder;n.challenger=l.challenger;n.waiting=l.waiting;n.round=l.round;
            int loser=winner==l.holder?l.challenger:l.holder;n.win(winner);
            check(n.points[winner]==l.points[winner]+1);
            if(n.champion>=0) {check(n.points[n.champion]==3);check(decisive+1<=7);}
            else {check(n.holder==winner && n.challenger==l.waiting && n.waiting==loser);walk(n,decisive+1);}
        }
    }
    public static void main(String[] args)
    {
        walk(new GroupPolicy.Ladder(),0);
        try {new GroupPolicy.Ladder().win(2);throw new AssertionError("Waiting team scored");}catch(IllegalArgumentException expected){checks++;}
        check(GroupPolicy.concern(.15,0,false,true)>GroupPolicy.concern(.9,0,true,false));
        check(GroupPolicy.heal(.64,0));check(!GroupPolicy.heal(.9,50));check(GroupPolicy.heal(.8,21));
        check(!GroupPolicy.massRevive(1,.1,false));check(GroupPolicy.massRevive(2,.8,false));
        check(!GroupPolicy.massRevive(2,.8,true));check(GroupPolicy.massRevive(3,.2,true));
        check(!GroupPolicy.focusPet(.1,true,3,.8));check(!GroupPolicy.focusPet(.1,true,0,.2));
        check(GroupPolicy.focusPet(.3,false,0,.8));check(GroupPolicy.focusPet(.8,true,0,.8));
        check(GroupPolicy.canSummon(0,.1,true));check(!GroupPolicy.canSummon(2,1,true));
        check(!GroupPolicy.canSummon(1,.6,false));check(GroupPolicy.canSummon(1,.61,false));
        System.out.println("PASS "+checks+" group checks: all winner-stays paths, 3-point champion, 7-round bound, support and summon policies");
    }
}
