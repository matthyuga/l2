import custom.LabCombatPilots.LabCombatPilots;
import custom.LabCombatPilots.LabCombatPilots.Policy;

public class CombatPolicyCheck
{
    private static int checks;
    private static void check(boolean value) {checks++;if(!value) throw new AssertionError("Policy check="+checks);}
    public static void main(String[] args)
    {
        check(Policy.emergency(0));check(Policy.emergency(0.299));check(!Policy.emergency(0.30));check(!Policy.emergency(1));
        check(Policy.cpPotion(0.54));check(!Policy.cpPotion(0.55));check(!Policy.cpPotion(1));
        check(Policy.hpPotion(0.64));check(!Policy.hpPotion(0.65));check(!Policy.hpPotion(1));
        check(Policy.mpPotion(0.34));check(!Policy.mpPotion(0.35));check(!Policy.mpPotion(1));
        check(Policy.arcanePower(1,1,false));check(!Policy.arcanePower(0.60,1,false));check(!Policy.arcanePower(1,0.40,false));
        check(Policy.arcanePower(0.60,0.40,true));check(!Policy.arcanePower(0.35,1,true));check(!Policy.arcanePower(1,0.20,true));
        check(Policy.soulGuard(0.50,false));check(!Policy.soulGuard(0.30,false));check(Policy.soulGuard(0.30,true));check(!Policy.soulGuard(0.20,true));
        check(Policy.stance(0.50,false));check(!Policy.stance(0.30,false));check(Policy.stance(0.30,true));check(!Policy.stance(0.15,true));
        check(LabCombatPilots.cubicId(22)==2);check(LabCombatPilots.cubicId(33)==5);check(LabCombatPilots.cubicId(278)==4);check(LabCombatPilots.cubicId(1281)==8);check(LabCombatPilots.cubicId(12345)==-1);
        for(int i=0;i<=100;i++)
        {
            double value=i/100.0;
            check(Policy.cpPotion(value)==(i<55));
            check(Policy.hpPotion(value)==(i<65));
            check(Policy.mpPotion(value)==(i<35));
        }
        System.out.println("PASS "+checks+" policy checks: thresholds, boundaries, toggle hysteresis and cubic mapping.");
    }
}
