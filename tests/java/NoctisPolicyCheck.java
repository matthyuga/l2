import custom.LabCombatPilots.LabCombatPilots.Policy;
public class NoctisPolicyCheck
{
    private static int checks;
    private static void check(boolean value) {checks++;if(!value) throw new AssertionError("check="+checks);}
    public static void main(String[] args)
    {
        check(Policy.canSummon(0,0,0,100));
        check(!Policy.canSummon(0,1,200,100));
        check(Policy.canSummon(1,1,0,100));
        check(!Policy.canSummon(1,2,0,100));
        check(!Policy.canSummon(2,2,0,100));
        check(Policy.selfHeal(.24,0));
        check(!Policy.selfHeal(.25,3999));
        check(Policy.selfHeal(.25,4000));
        check(Policy.selfHeal(.59,4000));
        check(!Policy.selfHeal(.60,9000));
        for(int attempts=2;attempts<100;attempts++) check(!Policy.canSummon(0,attempts,0,100000));
        System.out.println("PASS "+checks+" Noctis checks: pending casts, hard summon budget, emergency healing and heal spacing.");
    }
}
