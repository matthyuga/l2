package custom.WorldDamageNumbers;

/** Damage range must fit the client's ten available glyph positions. */
public class WorldDamageNumbersCheck
{
    public static void main(String[] args)
    {
        double[] amounts={0.01,0.49,0.5,1.49,1.5,999.5,2147483647.0,2147483648.0,Double.MAX_VALUE};
        int[] expected={1,1,1,1,2,1000,Integer.MAX_VALUE,Integer.MAX_VALUE,Integer.MAX_VALUE};
        for(int i=0;i<amounts.length;i++){
            int value=WorldDamageNumbers.damageValue(amounts[i]);
            if(value!=expected[i]||Integer.toString(value).length()>10)throw new AssertionError("damage range: "+amounts[i]);
        }
        if(WorldDamageNumbers.glyphSkill(0,0,0)!=19200||WorldDamageNumbers.glyphSkill(3,9,9)!=19599)throw new AssertionError("catalog bounds");
        System.out.println("PASS: damage rounds safely, saturates without overflow and fits all ten client glyph positions.");
    }
}
