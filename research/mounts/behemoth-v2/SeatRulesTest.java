import custom.BehemothTransport.SeatRules;
import static custom.BehemothTransport.SeatRules.Role.*;
public class SeatRulesTest
{
    static void check(boolean x){if(!x)throw new AssertionError();}
    public static void main(String[] args)
    {
        var s=new SeatRules.Seats();check(!s.board(DRIVER,0));check(s.board(DRIVER,1));check(!s.board(DRIVER,2));check(!s.board(GUNNER,1));check(s.board(GUNNER,2));check(!s.board(GUNNER,3));check(s.leave(2)==GUNNER);check(s.board(GUNNER,3));check(s.leave(1)==DRIVER);s.close();check(!s.board(DRIVER,1)&&s.driver()==0&&s.gunner()==0);
        check(SeatRules.boardingRange(120,120,80,true));check(!SeatRules.boardingRange(201,0,0,true));check(!SeatRules.boardingRange(0,0,0,false));check(!SeatRules.boardingRange(0,0,121,true));
        var a=SeatRules.world(100,200,300,0,DRIVER);check(a.x()==107&&a.y()==200&&a.z()==402);
        var b=SeatRules.world(100,200,300,16384,GUNNER);check(b.x()==100&&b.y()==162&&b.z()==391);
        check(SeatRules.world(100,200,300,65536,DRIVER).equals(a));
        System.out.println("BEHEMOTH_SEAT_RULES PASS: role exclusivity, closure, authorization geometry and heading transforms");
    }
}
