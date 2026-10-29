import custom.AcademyWorld.AcademyWorld;

public class AcademyBoundaryTest
{
    public static void main(String[] args)
    {
        if (!AcademyWorld.inside(148900,46100,-3400,0)) throw new AssertionError("Coliseum spawn");
        if (!AcademyWorld.inside(145500,43000,-5000,0)) throw new AssertionError("Inclusive lower boundary");
        if (AcademyWorld.inside(145499,46100,-3400,0)) throw new AssertionError("West boundary");
        if (AcademyWorld.inside(153001,46100,-3400,0)) throw new AssertionError("East boundary");
        if (AcademyWorld.inside(148900,42999,-3400,0)) throw new AssertionError("South boundary");
        if (AcademyWorld.inside(148900,49501,-3400,0)) throw new AssertionError("North boundary");
        if (AcademyWorld.inside(148900,46100,-1499,0)) throw new AssertionError("Upper vertical boundary");
        if (AcademyWorld.inside(148900,46100,-5001,0)) throw new AssertionError("Lower vertical boundary");
        if (AcademyWorld.inside(149000,46700,12040,0)) throw new AssertionError("Sky dock");
        if (AcademyWorld.inside(82698,148638,-3473,0)) throw new AssertionError("Giran");
        if (AcademyWorld.inside(148900,46100,-3400,1)) throw new AssertionError("Foreign instance");
        System.out.println("ACADEMY_BOUNDARY PASS: Coliseum entry, all spatial limits, dock/Giran exclusion and instance isolation.");
    }
}
