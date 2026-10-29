import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public class AllRampsProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception {
  var g=GeoEngine.getInstance();if(!g.reloadRegion(24,19))throw new AssertionError("Geo reload failed");
  double[][] ramps={{0,-1,55856,55920,139888.0,139760,7968.0,8032.0},{0,-1,55856,55872,139872.0,139840,7968.0,7984.0},{0,-1,55888,55920,139888.0,139856,7968.0,7984.0},{0,-1,55920,55936,139904.0,139872,7968.0,7984.0},{0,-1,55536,55648,140528.0,140496,7872.0,7888.0},{0,-1,57056,57200,141232.0,141200,8000.0,8016.0},{0,-1,55984,56048,142656.0,142624,8064.0,8080.0},{0,-1,56160,56672,142656.0,142624,8064.0,8080.0},{0,1,54576,54608,138976.0,139008,8000.0,8016.0},{0,1,55792,55856,139680.0,139712,8032.0,8048.0},{0,1,56032,56176,142496.0,142560,8000.0,8032.0},{0,1,56048,56160,142496.0,142624,8000.0,8064.0},{0,1,56368,56512,142720.0,142752,8064.0,8080.0},{1,-1,142048,142224,54272.0,54208,8096.0,8128.0},{1,-1,142064,142208,54272.0,54240,8096.0,8112.0},{1,-1,140112,140176,54528.0,54512,7968.0,7976.0},{1,-1,139024,139136,54640.0,54576,8000.0,8032.0},{1,-1,139008,139136,54640.0,54608,8000.0,8016.0},{1,-1,141264,141376,55408.0,55216,8000.0,8096.0},{1,-1,141264,141392,55408.0,55344,8000.0,8032.0},{1,-1,140784,140928,55472.0,55440,8000.0,8016.0},{1,-1,139712,139760,55888.0,55856,8032.0,8048.0},{1,-1,139232,139440,56528.0,56464,8000.0,8032.0},{1,-1,139216,139456,56528.0,56496,8000.0,8016.0},{1,-1,141184,141328,56592.0,56560,8000.0,8016.0},{1,1,138928,139104,55136.0,55168,8000.0,8016.0},{1,1,138960,139072,55136.0,55200,8000.0,8032.0},{1,1,139856,139968,55712.0,55776,7888.0,7920.0},{1,1,139856,139968,55792.0,55824,7920.0,7936.0},{1,1,139856,139888,55712.0,55840,7888.0,7952.0},{1,1,139888,139920,55792.0,55856,7920.0,7952.0},{1,1,139936,139952,55840.0,55872,7936.0,7952.0}};StringBuilder out=new StringBuilder();int checks=0,fail=0;
  for(int n=0;n<ramps.length;n++){
   double[] f=ramps[n];int axis=(int)f[0],sign=(int)f[1],run=(int)Math.abs(f[5]-f[4]);
   for(int along:new int[]{(int)f[2]+8,(int)((f[2]+f[3])/2),(int)f[3]-8}){
    for(int step=-8;step<run+8;step+=8){
     int u=(int)f[4]+sign*step,nu=u+sign*8;
     int x=axis==0?u:along,y=axis==0?along:u,tx=axis==0?nu:along,ty=axis==0?along:nu;
     int ref=(int)(f[6]+(u-f[4])/(f[5]-f[4])*(f[7]-f[6])+43.35);
     int tref=(int)(f[6]+(nu-f[4])/(f[5]-f[4])*(f[7]-f[6])+43.35);
     int z=g.getHeight(x,y,ref),tz=g.getHeight(tx,ty,tref);
     boolean up=g.canMoveToTarget(x,y,z,tx,ty,tz,0),down=g.canMoveToTarget(tx,ty,tz,x,y,z,0);checks+=2;
     if(!up||!down){fail++;out.append("FAIL ramp="+n+" "+x+","+y+","+z+" -> "+tx+","+ty+","+tz+" up="+up+" down="+down+"\n");}
    }
   }
  }
  out.append("ramps="+ramps.length+" bidirectional_checks="+checks+" failed_segments="+fail+"\n");Files.writeString(Path.of(dir,"server-probe.txt"),out);
  if(fail>0)throw new AssertionError("Ramp path failures: "+fail);
 }
}